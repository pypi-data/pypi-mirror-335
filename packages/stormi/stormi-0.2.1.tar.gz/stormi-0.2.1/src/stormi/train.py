import time
from typing import Any, Optional

import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy.sparse as sp
from beartype import beartype
from numpyro.infer import SVI, Trace_ELBO


@beartype
class ScaledTrace_ELBO(Trace_ELBO):
    def __init__(self, scale: int, *args, **kwargs):
        """
        Initializes the ScaledTrace_ELBO.

        Args:
            scale (float): The factor by which to scale the ELBO loss.
            *args: Additional positional arguments for Trace_ELBO.
            **kwargs: Additional keyword arguments for Trace_ELBO.
        """
        super().__init__(*args, **kwargs)
        self.scale = scale

    def loss(self, *args, **kwargs):
        """
        Computes the scaled ELBO loss.

        Returns:
            float: The scaled ELBO loss.
        """
        original_loss = super().loss(*args, **kwargs)
        scaled_loss = original_loss / self.scale
        return scaled_loss

    # Check if the layers are sparse and convert them to dense arrays if necessary
    def convert_to_dense(layer):
        if sp.issparse(layer):
            return layer.toarray()
        else:
            return layer


@beartype
def cell_data_loader(
    data: jnp.ndarray,
    M_c: jnp.ndarray,
    batch_index: jnp.ndarray,
    tf_indices: jnp.ndarray,
    batch_size: int,
    rng_seed: int = 0,
    shuffle: bool = True,
    drop_last: bool = True,
    data_atac: Optional[jnp.ndarray] = None,
):
    rng = np.random.default_rng(rng_seed)
    num_cells = data.shape[0]
    all_indices = np.arange(num_cells)

    while True:
        if shuffle:
            rng.shuffle(all_indices)

        start = 0
        while start + batch_size <= num_cells:
            idx_sub = all_indices[start : start + batch_size]
            data_sub = data[idx_sub, ...]
            if data_atac is not None:
                data_atac_sub = data_atac[idx_sub, ...]
            else:
                data_atac_sub = None
            M_c_sub = M_c[idx_sub, ...]
            batch_index_sub = batch_index[idx_sub, ...]
            yield (
                idx_sub,
                data_sub,
                data_atac_sub,
                M_c_sub,
                batch_index_sub,
                tf_indices,
            )
            start += batch_size


@beartype
def train_svi(
    model: Any,
    guide: Any,
    model_input: dict,
    max_iterations: int = 800,
    min_lr: float = 0.001,
    max_lr: float = 0.01,
    ramp_up_fraction: float = 0.1,
    seed: int = 0,
    log_interval: int = 25,
    cell_batch_size: int = 64,
    region_batch_size: int = 10000,
):
    """
    Train an SVI model with a custom scaled ELBO, a one-cycle LR schedule,
    and optional cell-level minibatching if `cell_batch_size > 0`.
    Also supports region-level batching if 'num_regions' is in `model_input`.

    Parameters
    ----------
    model : Callable
        A NumPyro model function.
    guide : Callable
        A NumPyro guide function.
    model_input : dict
        Dictionary of model inputs in the order that `model` and `guide` expect.
        If "num_regions" is present, region-level batching is enabled for ATAC data.
    max_iterations : int, optional
        Total number of SVI update steps (default=800).
    min_lr : float, optional
        Minimum learning rate in the one-cycle schedule (default=0.001).
    max_lr : float, optional
        Maximum (peak) LR in the one-cycle schedule (default=0.01).
    ramp_up_fraction : float, optional
        Fraction of steps to ramp from min_lr to max_lr (default=0.1).
    seed : int, optional
        PRNG seed for reproducibility (default=0).
    log_interval : int, optional
        Print logs every `log_interval` steps (default=25).
    cell_batch_size : int, optional
        If > 0, enable cell-level minibatching with this batch size. If 0, use full data.
    region_batch_size : int, optional
        If > 0, Use region-level minibatching with this batch size. If 0, use full data.

    Returns
    -------
    guide : Callable
        The same guide, now trained.
    svi : SVI
        The NumPyro SVI object.
    svi_state : SVIState
        The final trained state (containing learned parameters).
    losses : list of float
        The ELBO loss after each iteration.
    model_input: Updated model input.
    """

    # 1) Extract basic arrays from model_input
    data = model_input["data"]
    M_c = model_input["M_c"]
    batch_index = model_input["batch_index"]
    tf_indices = model_input["tf_indices"]
    do_region_batching = "num_regions" in model_input
    if do_region_batching:
        data_atac = model_input["data_atac"]
    else:
        data_atac = None

    # 2) Set up cell minibatching if cell_batch_size > 0
    enable_cell_minibatch = cell_batch_size > 0
    if enable_cell_minibatch:
        rng_seed_loader = seed + 123  # offset from main seed
        loader = cell_data_loader(
            data=data,
            M_c=M_c,
            batch_index=batch_index,
            tf_indices=tf_indices,
            batch_size=cell_batch_size,
            rng_seed=rng_seed_loader,
            shuffle=True,
            drop_last=True,
            data_atac=data_atac,
        )
        idx_sub, data_sub, data_atac_sub, M_c_sub, batch_index_sub, tf_sub = next(
            loader
        )
    else:
        # Use entire dataset
        data_sub = data
        data_atac_sub = data_atac
        M_c_sub = M_c
        batch_index_sub = batch_index
        tf_sub = tf_indices

    # 3) Handle region-level batching if 'num_regions' is present
    if do_region_batching:
        num_regions = model_input["num_regions"]
        all_region_indices = np.arange(num_regions)
        rng_local = np.random.default_rng(seed)
        if region_batch_size == 0:
            region_batch_size = num_regions

        # For init
        init_region_batch = rng_local.choice(
            all_region_indices, size=region_batch_size, replace=False
        )
        data_atac_sub = data_atac_sub[:, init_region_batch]
    else:
        data_atac_sub = data_atac_sub

    # 4) Compute a scale factor for custom ELBO
    cells, genes, modalities = data.shape
    if do_region_batching:
        if enable_cell_minibatch:
            scale_factor = (
                cell_batch_size * genes * modalities
                + cell_batch_size * region_batch_size
            )
        else:
            scale_factor = cells * genes * modalities + cells * region_batch_size
    else:
        if enable_cell_minibatch:
            scale_factor = cell_batch_size * genes * modalities
        else:
            scale_factor = cells * genes * modalities

    scaled_elbo = ScaledTrace_ELBO(scale=scale_factor)

    # 5) Define the one-cycle LR schedule
    learning_rate_schedule = optax.linear_onecycle_schedule(
        transition_steps=max_iterations,
        peak_value=max_lr,
        pct_start=ramp_up_fraction,
        div_factor=max_lr / min_lr,
    )

    # 6) Create the SVI object
    optax_optimizer = optax.chain(
        optax.clip_by_global_norm(1.0), optax.adam(learning_rate=learning_rate_schedule)
    )
    svi = SVI(model, guide, optax_optimizer, loss=scaled_elbo)

    # 7) Initialize SVI with either minibatch or full data
    rng_key = jax.random.PRNGKey(seed)
    local_model_input = dict(model_input)  # shallow copy

    # Update these fields with our initial batch
    local_model_input["data"] = data_sub
    local_model_input["M_c"] = M_c_sub
    local_model_input["batch_index"] = batch_index_sub
    local_model_input["tf_indices"] = tf_sub

    if do_region_batching:
        local_model_input["batch_region_indices"] = init_region_batch
        local_model_input["data_atac"] = data_atac_sub
        local_model_input["region_tf_pairs_mask"] = np.where(
            jnp.isin(local_model_input["region_tf_pairs"][:, 0], init_region_batch)
        )[0]
        model_input["batch_region_indices"] = local_model_input["batch_region_indices"]
        model_input["region_tf_pairs_mask"] = local_model_input["region_tf_pairs_mask"]

    # Convert to argument list
    init_args = list(local_model_input.values())
    svi_state = svi.init(rng_key, *init_args, sde_rng_key=rng_key)

    # 8) Training loop
    losses = []
    start_time = time.time()

    for step in range(max_iterations):
        # Generate a new PRNG key for this epoch; this is only used when the model is stochastic (SDE) and we wish to sample a random path (or many paths).
        # By creating a new key at each iteration, we ensure that the infered model has a different realization of the stochastic process at each iteration.
        rng_key, subkey = jax.random.split(rng_key)  # NEW: Generate a fresh PRNG key

        # (a) Cell minibatching
        if enable_cell_minibatch:
            idx_sub, data_sub, data_atac_sub, M_c_sub, batch_index_sub, tf_sub = next(
                loader
            )
            local_model_input["data"] = data_sub
            local_model_input["M_c"] = M_c_sub
            local_model_input["batch_index"] = batch_index_sub
            local_model_input["tf_indices"] = tf_sub

        # (b) Region minibatching
        if do_region_batching:
            region_batch = rng_local.choice(
                all_region_indices, size=region_batch_size, replace=False
            )
            local_model_input["batch_region_indices"] = region_batch
            local_model_input["region_tf_pairs_mask"] = np.where(
                jnp.isin(local_model_input["region_tf_pairs"][:, 0], region_batch)
            )[0]

            model_input["batch_region_indices"] = local_model_input[
                "batch_region_indices"
            ]
            model_input["region_tf_pairs_mask"] = local_model_input[
                "region_tf_pairs_mask"
            ]

            if enable_cell_minibatch:
                local_model_input["data_atac"] = data_atac_sub[:, region_batch]
            else:
                local_model_input["data_atac"] = data_atac[:, region_batch]

        current_args = list(local_model_input.values())
        svi_state, loss_val = svi.update(svi_state, *current_args, sde_rng_key=subkey)
        losses.append(loss_val)

        if step % log_interval == 0:
            current_lr = learning_rate_schedule(step)
            print(f"Step {step}, Loss: {loss_val:.4f}, LR: {current_lr:.6f}")

    elapsed_time = time.time() - start_time
    print(f"Training completed in {elapsed_time:.2f}s over {max_iterations} steps.")

    return guide, svi, svi_state, losses, model_input
