from collections import OrderedDict
from functools import partial
from typing import Any, Callable, Dict, List, Optional

import jax
import jax.numpy as jnp
import jax.random as random
import matplotlib.pyplot as plt
import numpy as np
import numpyro
import numpyro.distributions as dist
import pandas as pd
import scanpy as sc
import scipy.sparse as sp
from anndata import AnnData
from beartype import beartype
from diffrax import Euler, ODETerm, RecursiveCheckpointAdjoint, SaveAt, diffeqsolve
from einops import rearrange
from jaxtyping import Float, jaxtyped
from numpyro.handlers import scale
from numpyro.infer import SVI, Predictive, Trace_ELBO
from numpyro.infer.autoguide import AutoNormal
from numpyro.optim import Adam

# Import helper functions from preprocessing module
from ..preprocessing import (
    build_region_gene_pairs,
    construct_region_tf_gene_triplets,
    convert_to_dense,
    extract_region_tf_pairs,
    precompute_mapping,
    precompute_region_tf_indices,
)

# Import functions from model_utils.py
from .utils import solve_DE, sort_times_over_all_cells


@beartype
def prepare_model_input(
    adata_rna: AnnData,
    adata_atac: AnnData,
    tf_list: List[str],
    motif_scores: pd.DataFrame,
    n_cells_col: Optional[str] = "n_cells",
    batch_annotation: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare input data for the model by converting layers, stacking counts, and
    computing region–TF/gene relationships.

    This function performs the following steps:

      1. **Dense Conversion & Stacking RNA Data:**
         - Converts the `'spliced'` and `'unspliced'` layers of `adata_rna` to dense
           format using `convert_to_dense`.
         - Stacks the two arrays along a new axis (last dimension) and converts the
           resulting array to a JAX array.

      2. **ATAC Data Conversion:**
         - Converts the ATAC data (`adata_atac.X`) to a JAX array.

      3. **Additional Metadata Extraction:**
         - **M_c:** If `n_cells_col` is provided (not `None`), extracts that column from
           `adata_rna.obs` and reshapes it into a (cells, 1, 1) JAX array. Otherwise,
           sets `M_c` to an array of ones.
         - **batch_index:** If `batch_annotation` is provided, maps each unique batch
           to an integer and assigns these to cells. Otherwise, assigns a value of 1
           to all cells.
         - Determines the indices (and count) of transcription factors (TFs) in
           `adata_rna.var_names` using `tf_list`.
         - Determines the number of regions from the ATAC data.

      4. **Region–TF and Region–Gene Relationships:**
         - Computes `region_tf_pairs` using the `motif_scores` DataFrame
           together with `adata_atac` and `adata_rna`.
         - Computes `region_gene_pairs` from the RNA and ATAC AnnData objects.
         - Constructs all unique (region, TF, gene) triplets.
         - Precomputes a mapping from region–TF pairs to indices.
         - Computes the region–TF indices corresponding to each triplet.
         - Extracts gene indices from the triplets.

    Parameters
    ----------
    adata_rna : AnnData
        AnnData object containing RNA expression data with at least two layers:
        `'spliced'` and `'unspliced'`. Also requires an observation column (if used)
        containing the number of cells per metacell and a `var_names` attribute.
    adata_atac : AnnData
        AnnData object containing ATAC data. Its main count matrix is used.
    tf_list : List[str]
        List of transcription factor names.
    motif_scores : pd.DataFrame
        DataFrame (previously called moods_scores) that contains at least the columns used in
        the helper function `extract_region_tf_pairs` (by default, columns named `"0"` for regions
        and `"mouse_gene_name"` for TFs).
    n_cells_col : Optional[str], default "n_cells"
        Name of the column in `adata_rna.obs` that contains the number of cells in each metacell.
        If set to `None`, `M_c` is set to an array of ones.
    batch_annotation : Optional[str], default None
        Name of the column in `adata_rna.obs` that contains batch names.
        If `None`, all cells are assigned a batch value of 1. Otherwise, each unique batch is
        mapped to an integer.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
          - `data`: JAX array of shape (cells, features, 2) with stacked unspliced and spliced RNA counts.
          - `data_atac`: JAX array of ATAC counts.
          - `M_c`: JAX array of shape (cells, 1, 1) holding the per-cell metacell size.
          - `batch_index`: JAX array of batch indices for each cell.
          - `tf_indices`: JAX array of indices of transcription factors.
          - `num_tfs`: Total number of transcription factors (int).
          - `num_regions`: Total number of regions from the ATAC data (int).
          - `region_tf_pairs`: JAX array of region–TF pairs.
          - `region_gene_pairs`: JAX array of region–gene pairs with a weight.
          - `region_tf_gene_triplets`: JAX array of triplets (region, TF, gene).
          - `map_region_tf_to_index`: JAX array mapping each [region, TF] pair to its index.
          - `region_tf_indices`: JAX array of indices corresponding to the triplets.
          - `gene_indices`: JAX array of gene indices from the triplets.

    Example
    -------
    >>> inputs = prepare_model_input_data(adata_rna, adata_atac, tf_list, motif_scores,
    ...                                    n_cells_col="n_cells", batch_annotation="batch")
    >>> print(inputs["data"].shape)
    """

    # --- Step 1: Convert and stack RNA layers ---
    spliced_dense = convert_to_dense(adata_rna.layers["spliced"])
    unspliced_dense = convert_to_dense(adata_rna.layers["unspliced"])
    # Stack along a new last axis: shape becomes (cells, features, 2)
    data = np.stack([unspliced_dense, spliced_dense], axis=-1)
    data = jnp.array(data)
    del unspliced_dense, spliced_dense

    # --- Step 2: Convert ATAC data ---
    data_atac = jnp.array(adata_atac.X)

    # --- Step 3: Extract additional metadata ---
    # M_c: Use provided column or default to ones.
    if n_cells_col is not None:
        M_c = jnp.array(
            np.expand_dims(
                np.expand_dims(adata_rna.obs[n_cells_col].to_numpy(), -1), -1
            )
        )
    else:
        M_c = jnp.ones((adata_rna.n_obs, 1, 1))
    total_num_cells = adata_rna.n_obs

    # batch_index: Map batch annotation to integer labels if provided; otherwise, assign 1 to all.
    if batch_annotation is not None:
        # Create a mapping from batch names to integers
        batch_series = adata_rna.obs[batch_annotation]
        unique_batches = batch_series.unique()
        batch_map = {batch: i for i, batch in enumerate(unique_batches)}
        batch_index = jnp.array(batch_series.map(batch_map).to_numpy())
    else:
        batch_index = jnp.zeros(adata_rna.n_obs, dtype=int)

    # Determine which genes in adata_rna.var_names are TFs.
    is_tf = adata_rna.var_names.isin(tf_list)
    tf_indices = jnp.array(np.where(is_tf)[0])
    num_tfs = int(tf_indices.shape[0])
    num_regions = int(data_atac.shape[1])

    # --- Step 4: Compute region–TF and region–gene relationships ---
    region_tf_pairs = extract_region_tf_pairs(motif_scores, adata_atac, adata_rna)
    region_gene_pairs = build_region_gene_pairs(adata_atac, adata_rna)
    region_tf_gene_triplets = construct_region_tf_gene_triplets(
        region_tf_pairs, region_gene_pairs
    )
    map_region_tf_to_index = precompute_mapping(
        region_tf_pairs, region_tf_gene_triplets, num_regions, num_tfs
    )
    region_tf_indices = precompute_region_tf_indices(
        region_tf_gene_triplets, map_region_tf_to_index, num_tfs
    )
    gene_indices = region_tf_gene_triplets[:, 2]

    return OrderedDict(
        [
            ("data", data),
            ("data_atac", data_atac),
            ("M_c", M_c),
            ("batch_index", batch_index),
            ("tf_indices", tf_indices),
            ("region_tf_pairs", region_tf_pairs),
            ("region_gene_pairs", region_gene_pairs),
            ("region_tf_gene_triplets", region_tf_gene_triplets),
            ("region_tf_indices", region_tf_indices),
            ("gene_indices", gene_indices),
            ("num_regions", num_regions),
            ("total_num_cells", total_num_cells),
        ]
    )


@beartype
def sample_prior(
    model: Callable[..., Any],
    model_input: Dict[str, Any],
    num_samples: int = 5,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Runs prior predictive sampling for a given model.

    Parameters:
    - model (Callable[..., Any]): The probabilistic model to sample from.
    - model_input (Dict[str, Any]): Input arguments to be passed to the model.
    - num_samples (int): Number of prior predictive samples to generate.
    - seed (int): Random seed for reproducibility.

    Returns:
    - Dict[str, Any]: Prior predictive samples generated by the model.
    """
    # Generate a random seed
    rng_key = random.PRNGKey(
        seed
    )  # Replace 42 with any integer seed for reproducibility

    # Run the prior predictive simulation with your model
    predictive = Predictive(model, num_samples=num_samples)

    # For init
    num_regions = model_input["num_regions"]
    all_region_indices = np.arange(num_regions)
    rng_local = np.random.default_rng(0)
    init_region_batch = rng_local.choice(
        all_region_indices, size=num_regions, replace=False
    )
    model_input["batch_region_indices"] = init_region_batch
    model_input["region_tf_pairs_mask"] = np.where(
        jnp.isin(model_input["region_tf_pairs"][:, 0], init_region_batch)
    )[0]

    prior_samples = predictive(rng_key, **model_input)
    return prior_samples


# Define the ODE function
@beartype
def dstate_dt(t, state, args):
    """
    Compute the derivative of the state vector for the coupled system using TF binding mechanics.

    Args:
        t: Time scalar.
        state: State vector [u_1, ..., u_G, s_1, ..., s_G].
        args: Tuple containing parameters (G, beta_g, gamma_g, nn_params, T_ON).

    Returns:
        Derivative of the state vector
    """

    (
        alpha0_g,
        beta_g,
        gamma_g,
        lamda,
        kappa,
        K_rh_vector,
        w_grh_vector,
        b_g,
        tf_indices,
        region_tf_pairs,
        region_tf_gene_triplets,
        region_tf_indices,
        gene_indices,
        num_genes,
        T_ON,
    ) = args

    u = state[..., 0]  # Unspliced counts for all genes.
    s = state[..., 1]  # Spliced counts for all genes.
    p = state[..., 2]  # Proteins for all genes.

    # Clip state values to increase numerical stability (maybe not necessary):
    u = jnp.clip(u, 0, 1e3)
    s = jnp.clip(s, 0, 1e3)
    p = jnp.clip(p, 0, 1e3)

    # Calculate binding probability for each TF:
    p_h_values = p[0, region_tf_pairs[:, 1]]
    P_rh_vector = p_h_values / (p_h_values + K_rh_vector)

    # Calculate transcription rate by summing up effects of all TF-region pairs:
    P_rh_for_rtg = P_rh_vector[region_tf_indices]  # [num_rtg_triplets]
    wP = w_grh_vector * P_rh_for_rtg
    sum_w_P = jax.ops.segment_sum(wP, gene_indices, num_segments=num_genes)
    alpha = alpha0_g * jax.nn.softplus(b_g + sum_w_P)

    # ODEs:
    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s
    dp_dt = jnp.zeros_like(u)  # Compute dp_dt only for TF indices
    dp_dt = dp_dt.at[tf_indices].set(lamda * s[tf_indices] - kappa * p[tf_indices])

    dstate_dt = jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)  # Shape: (3G,)

    return dstate_dt


def compute_d_cr(
    p: jnp.ndarray,  # shape (305, 1000)
    region_tf_pairs: jnp.ndarray,  # shape (2550, 2) => [r, h]
    K_rh_vector: jnp.ndarray,  # shape (2550,)
    w_h: jnp.ndarray,  # shape (num_TFs=109,)
    w_r: jnp.ndarray,  # shape (num_regions,)
    num_regions: int,
) -> jnp.ndarray:
    """
    Compute d_cr for each of C=305 rows (cells/time points) and R regions:
      d_cr = w_r + sum_{(r,h)} [w_h[h] * P_{rh}(c)],
    where
      P_{rh}(c) = p[c,h] / (p[c,h] + K_rh).

    Returns shape (305, num_regions).
    """

    # 1) Gather protein for each (region, TF) pair
    #    region_tf_pairs[:,1] are TF indices
    p_h_values = p[:, region_tf_pairs[:, 1]]

    # 2) Binding probabilities
    P_rh_vector = p_h_values / (p_h_values + K_rh_vector[None, :])

    # 3) Convert TF-level weights to pair-level weights
    tf_indices = region_tf_pairs[:, 1]
    w_h_for_pairs = w_h[tf_indices]

    # 4) Weighted binding
    w_h_P = w_h_for_pairs * P_rh_vector

    # 5) Sum over region indices
    region_indices = region_tf_pairs[:, 0]

    # Swap axes:
    w_h_P_swapped = jnp.swapaxes(w_h_P, 0, 1)  # axis 0 -> pairs, axis 1 -> time

    # Do segment_sum over axis=0, grouping by region_indices
    sum_w_hP_swapped = jax.ops.segment_sum(
        w_h_P_swapped, region_indices, num_segments=num_regions
    )

    # 3) Swap back
    sum_w_hP = jnp.swapaxes(sum_w_hP_swapped, 0, 1)

    # 6) Add baseline w_r
    d_cr = jax.nn.relu(sum_w_hP + w_r) + 10 ** (-5)
    return d_cr


# Define the complete NumPyro model
@beartype
def model(
    data: Any,
    data_atac: Any,
    M_c: Any,
    batch_index: Any,
    tf_indices: Any,
    region_tf_pairs: Any,
    region_gene_pairs: Any,
    region_tf_gene_triplets: Any,
    region_tf_indices: Any,
    gene_indices: Any,
    num_regions: Any,
    total_num_cells: int,
    batch_region_indices: Any,
    region_tf_pairs_mask: Any,
    n_batch: int = 1,
    Tmax_alpha: float = 50.0,
    Tmax_beta: float = 1.0,
    splicing_rate_alpha_hyp_prior_alpha: float = 20.0,
    splicing_rate_alpha_hyp_prior_mean: float = 5.0,
    splicing_rate_mean_hyp_prior_alpha: float = 10.0,
    splicing_rate_mean_hyp_prior_mean: float = 1.0,
    degradation_rate_alpha_hyp_prior_alpha: float = 20.0,
    degradation_rate_alpha_hyp_prior_mean: float = 5.0,
    degradation_rate_mean_hyp_prior_alpha: float = 10.0,
    degradation_rate_mean_hyp_prior_mean: float = 1.0,
    transcription_rate_alpha_hyp_prior_alpha: float = 20.0,
    transcription_rate_alpha_hyp_prior_mean: float = 2.0,
    transcription_rate_mean_hyp_prior_alpha: float = 10.0,
    transcription_rate_mean_hyp_prior_mean: float = 5.0,
    lambda_alpha: float = 1.0,
    lambda_mean: float = 1.0,
    kappa_alpha: float = 1.0,
    kappa_mean: float = 1.0,
    detection_mean_hyp_prior_alpha: float = 1.0,
    detection_mean_hyp_prior_beta: float = 1.0,
    detection_hyp_prior_alpha: float = 10.0,
    detection_i_prior_alpha: float = 100.0,
    detection_gi_prior_alpha: float = 200.0,
    gene_add_alpha_hyp_prior_alpha: float = 9.0,
    gene_add_alpha_hyp_prior_beta: float = 3.0,
    gene_add_mean_hyp_prior_alpha: float = 1.0,
    gene_add_mean_hyp_prior_beta: float = 100.0,
    stochastic_v_ag_hyp_prior_alpha: float = 9.0,
    stochastic_v_ag_hyp_prior_beta: float = 3.0,
    sde_rng_key: Any = random.PRNGKey(0),
):
    """
    NumPyro model for coupled transcription, splicing, protein, chromatin dynamics.

    Args:
        data: Observed data array of shape (num_cells, num_genes, num_modalities).
        ... (other model inputs)
        ... (other hyperparameters for priors)
        key: Random number generator key.

    Returns:
        None. Defines the probabilistic model for inference.
    """
    num_cells, num_genes, num_modalities = data.shape
    num_tfs = tf_indices.shape[0]
    num_pairs = len(region_tf_pairs)
    num_rg_pairs = len(region_gene_pairs)
    num_rtg_triplets = len(region_tf_gene_triplets)
    num_regions_total = num_regions
    num_regions_batch = data_atac.shape[1]
    batch_size = num_cells
    obs2sample = jax.nn.one_hot(
        batch_index, num_classes=n_batch
    )  # Shape: (num_cells, n_batch)

    # Dissociation constant
    K_rh_alpha = numpyro.sample("K_rh_alpha", dist.Gamma(4.0, 1.0))
    K_rh_beta = numpyro.sample("K_rh_beta", dist.Gamma(0.4, 1.0))
    K_rh_vector = numpyro.sample(
        "K_rh_vector", dist.Gamma(K_rh_alpha, K_rh_beta).expand([num_pairs])
    )

    # Basal transcription rate
    alpha0_g = numpyro.sample(
        "alpha0_g",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([num_genes]).to_event(1),
    )

    # Bias term for transcription rate function:
    b_g_mean = numpyro.sample("b_g_mean", dist.Normal(1.0, 1.0))
    b_g_sd = numpyro.sample("b_g_sd", dist.Gamma(1.0, 1.0))
    b_g = numpyro.sample(
        "b_g", dist.Normal(b_g_mean, b_g_sd).expand([num_genes]).to_event(1)
    )

    # Effect of region-tf pairs on target gene transcription rate
    w_grh_mean = numpyro.sample("w_grh_mean", dist.Normal(5.0, 5.0))
    w_grh_sd = numpyro.sample("w_grh_sd", dist.Gamma(1.0, 1.0 / 5.0))
    w_grh_vector = numpyro.sample(
        "w_grh_vector", dist.Normal(w_grh_mean, w_grh_sd).expand([num_rtg_triplets])
    )

    # Effect of TF binding on region ATAC counts:
    w_h = numpyro.sample("w_h", dist.Normal(1.0, 1.0).expand([num_tfs]))
    # Baseline ATAC cound for each region
    w_r = numpyro.sample("w_r", dist.Normal(1.0, 1.0).expand([num_regions_total]))

    # Splicing Rates for mRNA
    splicing_alpha = numpyro.sample(
        "splicing_alpha",
        dist.Gamma(
            splicing_rate_alpha_hyp_prior_alpha,
            splicing_rate_alpha_hyp_prior_alpha / splicing_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_alpha = jnp.clip(splicing_alpha, a_min=1e-2, a_max=1e3)

    splicing_mean = numpyro.sample(
        "splicing_mean",
        dist.Gamma(
            splicing_rate_mean_hyp_prior_alpha,
            splicing_rate_mean_hyp_prior_alpha / splicing_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    splicing_mean = jnp.clip(splicing_mean, a_min=1e-2, a_max=1e3)

    beta_g = numpyro.sample(
        "beta_g",
        dist.Gamma(splicing_alpha, splicing_alpha / splicing_mean, validate_args=True)
        .expand([num_genes])
        .to_event(1),
    )

    # Degradation Rates for mRNA
    degradation_alpha = numpyro.sample(
        "degradation_alpha",
        dist.Gamma(
            degradation_rate_alpha_hyp_prior_alpha,
            degradation_rate_alpha_hyp_prior_alpha
            / degradation_rate_alpha_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_alpha = degradation_alpha + 0.001  # Prevent zero

    degradation_mean = numpyro.sample(
        "degradation_mean",
        dist.Gamma(
            degradation_rate_mean_hyp_prior_alpha,
            degradation_rate_mean_hyp_prior_alpha
            / degradation_rate_mean_hyp_prior_mean,
            validate_args=True,
        ),
    )
    degradation_mean = jnp.clip(degradation_mean, a_min=1e-2, a_max=1e3)

    gamma_g = numpyro.sample(
        "gamma_g",
        dist.Gamma(
            degradation_alpha, degradation_alpha / degradation_mean, validate_args=True
        )
        .expand([num_genes])
        .to_event(1),
    )

    # Translation rate for proteins
    lamda = numpyro.sample(
        "lambda",
        dist.Gamma(lambda_alpha, lambda_alpha / lambda_mean, validate_args=True)
        .expand([num_genes])
        .to_event(1),
    )
    # Degradation rate for proteins
    kappa = numpyro.sample(
        "kappa",
        dist.Gamma(kappa_alpha, kappa_alpha / kappa_mean, validate_args=True)
        .expand([num_genes])
        .to_event(1),
    )

    # Time Parameters
    Tmax = numpyro.sample("Tmax", dist.Gamma(Tmax_alpha, Tmax_beta, validate_args=True))

    t_c_loc = numpyro.sample("t_c_loc", dist.Gamma(1.0, 1.0 / 0.5, validate_args=True))
    t_c_scale = numpyro.sample(
        "t_c_scale", dist.Gamma(1.0, 1.0 / 0.25, validate_args=True)
    )
    t_c_scale = jnp.clip(t_c_scale, a_min=1e-2)  # Prevent too small scales

    with numpyro.plate("cells", batch_size):
        t_c = numpyro.sample("t_c", dist.Normal(t_c_loc, t_c_scale))

    T_c = numpyro.deterministic("T_c", t_c * Tmax)

    # Time at which to start from initial condition:
    t_ON = numpyro.sample(
        "t_ON", dist.Normal(t_c_loc - t_c_scale, t_c_scale, validate_args=True)
    )

    T_ON = Tmax * t_ON

    # ============= Expression model =============== #

    # Initial Conditions for ODE, sampling only for spliced and unspliced
    initial_state_2d = numpyro.sample(
        "initial_state_2d",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([1, num_genes, 2]).to_event(1),
    )

    # Create the third dimension containing proteins, only for TFs:
    third_dimension = jnp.zeros((1, num_genes))
    third_dimension = third_dimension.at[0, tf_indices].set(
        numpyro.sample(
            "initial_state_tf",
            dist.Gamma(1.0, 1.0, validate_args=True).expand([len(tf_indices)]),
        )
    )

    # Concatenate the dimensions to form the final initial state
    initial_state = jnp.concatenate(
        [initial_state_2d, third_dimension[..., None]], axis=-1
    )

    # Prepare Parameters for ODE Solver
    params = (
        alpha0_g,
        beta_g,
        gamma_g,
        lamda,
        kappa,
        K_rh_vector,
        w_grh_vector,
        b_g,
        tf_indices,
        region_tf_pairs,
        region_tf_gene_triplets,
        region_tf_indices,
        gene_indices,
        num_genes,
        T_ON,
    )

    # Get Ordered Time Vector
    all_times, time_indices, _ = sort_times_over_all_cells(T_c)

    # Solve the Coupled ODE
    predictions = solve_DE(
        ts=all_times.squeeze(),
        params=params,
        initial_state=initial_state,
        time_step=0.1,
        drift=dstate_dt,
    )

    # Ensure predictions are floating-point
    predictions = numpyro.deterministic("predictions", predictions.astype(jnp.float32))

    predictions_rearranged = numpyro.deterministic(
        "predictions_rearranged", predictions[time_indices.ravel(), :]
    )

    mu_expression = jnp.clip(
        predictions_rearranged[..., :2].squeeze(1), a_min=10 ** (-5), a_max=10 ** (5)
    )

    mu_protein = predictions_rearranged[..., 2].squeeze(1)

    # ============= Detection efficiency of spliced and unspliced counts =============== #

    detection_mean_y_e = numpyro.sample(
        "detection_mean_y_e",
        dist.Beta(
            jnp.ones((1, 1)) * detection_mean_hyp_prior_alpha,
            jnp.ones((1, 1)) * detection_mean_hyp_prior_beta,
            validate_args=True,
        ).to_event(2),
        sample_shape=(n_batch, 1),
    )

    beta1 = ((detection_hyp_prior_alpha / (obs2sample @ detection_mean_y_e)).T)[0, ...]

    with numpyro.plate("cells", batch_size):
        detection_y_c = numpyro.sample(
            "detection_y_c", dist.Gamma(detection_hyp_prior_alpha, beta1[:, 0, 0])
        )

    detection_y_i = numpyro.sample(
        "detection_y_i",
        dist.Gamma(detection_i_prior_alpha, detection_i_prior_alpha, validate_args=True)
        .expand([1, 1, 2])
        .to_event(3),
    )

    detection_y_gi = numpyro.sample(
        "detection_y_gi",
        dist.Gamma(
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            jnp.ones((1, 1)) * detection_gi_prior_alpha,
            validate_args=True,
        )
        .expand([1, num_genes, 2])
        .to_event(3),
    )

    # ============= Detection efficiency of ATAC counts =============== #

    detection_mean_l_e = numpyro.sample(
        "detection_mean_l_e",
        dist.Beta(
            jnp.ones((1, 1)) * detection_mean_hyp_prior_alpha,
            jnp.ones((1, 1)) * detection_mean_hyp_prior_beta,
            validate_args=True,
        ).to_event(2),
        sample_shape=(n_batch, 1),
    )

    beta2 = ((detection_hyp_prior_alpha / (obs2sample @ detection_mean_l_e)).T)[0, ...]

    with numpyro.plate("cells", batch_size):
        detection_l_c = numpyro.sample(
            "detection_l_c", dist.Gamma(detection_hyp_prior_alpha, beta2[:, 0, 0])
        )

    # ======= Gene-specific additive component (Ambient RNA/ "Soup") for spliced and unspliced counts ====== #

    s_g_gene_add_alpha_hyp = numpyro.sample(
        "s_g_gene_add_alpha_hyp",
        dist.Gamma(
            gene_add_alpha_hyp_prior_alpha,
            gene_add_alpha_hyp_prior_beta,
            validate_args=True,
        ),
        sample_shape=(2,),
    )

    s_g_gene_add_mean = numpyro.sample(
        "s_g_gene_add_mean",
        dist.Gamma(
            gene_add_mean_hyp_prior_alpha,
            gene_add_mean_hyp_prior_beta,
            validate_args=True,
        )
        .expand([n_batch, 1, 2])
        .to_event(3),
    )

    s_g_gene_add_alpha_e_inv = numpyro.sample(
        "s_g_gene_add_alpha_e_inv",
        dist.Exponential(s_g_gene_add_alpha_hyp).expand([n_batch, 1, 2]).to_event(3),
    )

    s_g_gene_add_alpha_e = jnp.ones((1, 1)) / s_g_gene_add_alpha_e_inv**2

    s_g_gene_add = numpyro.sample(
        "s_g_gene_add",
        dist.Gamma(
            s_g_gene_add_alpha_e,
            s_g_gene_add_alpha_e / s_g_gene_add_mean,
            validate_args=True,
        )
        .expand([n_batch, num_genes, 2])
        .to_event(3),
    )

    # ========= Gene-specific overdispersion of spliced and unspliced counts ============== #

    stochastic_v_ag_hyp = numpyro.sample(
        "stochastic_v_ag_hyp",
        dist.Gamma(
            stochastic_v_ag_hyp_prior_alpha,
            stochastic_v_ag_hyp_prior_beta,
            validate_args=True,
        )
        .expand([1, 2])
        .to_event(2),
    )

    stochastic_v_ag_hyp = stochastic_v_ag_hyp + 0.001

    stochastic_v_ag_inv = numpyro.sample(
        "stochastic_v_ag_inv",
        dist.Exponential(stochastic_v_ag_hyp).expand([1, num_genes, 2]).to_event(3),
    )

    stochastic_v_ag = jnp.ones((1, 1)) / stochastic_v_ag_inv**2

    # ===================== Expected value for RNA and ATAC counts======================= #

    mu = numpyro.deterministic(
        "mu",
        (
            mu_expression
            + jnp.einsum(
                "cbi,bgi->cgi", jnp.expand_dims(obs2sample, axis=0), s_g_gene_add
            )
        )
        * detection_y_c[:, None, None]
        * detection_y_i
        * detection_y_gi
        * M_c,
    )

    d_cr = numpyro.deterministic(
        "d_cr",
        compute_d_cr(
            mu_protein,
            region_tf_pairs[region_tf_pairs_mask],
            K_rh_vector[region_tf_pairs_mask],
            w_h,
            w_r[batch_region_indices],
            num_regions_batch,
        ),
    )

    mu_atac = numpyro.deterministic(
        "mu_atac", detection_l_c[..., 0] * M_c[..., 0] * d_cr
    )

    # ===================== DATA likelihood ======================= #

    concentration = stochastic_v_ag * M_c
    rate = concentration / mu

    # We apply a scale factor so that the negative log-likelihood is multiplied
    # by the ratio of the full dataset to the minibatch dataset, to have an unbiased gradient estimate.
    scale_factor_rna = total_num_cells / batch_size
    with scale(scale=scale_factor_rna):
        data_target = numpyro.sample(
            "data_target", dist.GammaPoisson(concentration, rate), obs=data
        )

    # We further adjust the scale factor here to give equal weight to RNA and ATAC data
    # no matter the number of features in each
    scale_factor_atac = scale_factor_rna * 2 * num_genes / num_regions_batch
    with scale(scale=scale_factor_atac):
        data_target_atac = numpyro.sample(
            "data_target_atac", dist.Poisson(mu_atac), obs=data_atac
        )
