from __future__ import annotations

from typing import Any, Dict

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from beartype import beartype
from numpyro.handlers import scale

from .utils import solve_DE, sort_times_over_all_cells


@beartype
def mlp(
    params: Dict,
    x: Any,
) -> Any:
    """
    One or Multilayer Perceptron (MLP) with residual connections.

    Args:
        params: Dictionary containing neural network parameters (weights and biases).
        x: Input data array.

    Returns:
        Output array after passing through the MLP.
    """

    # First hidden layer with residual connections
    out = jnp.dot(x, params["W"]) + params["b"]
    out = jax.nn.softplus(out)

    return out


# Define the ODE function using the MLP
@beartype
def dstate_dt(t, state, args):
    """
    Compute the derivative of the state vector for the coupled system using a neural network.

    Args:
        t: Time scalar.
        state: State vector [u_1, ..., u_G, s_1, ..., s_G].
        args: Tuple containing parameters (G, beta_g, gamma_g, nn_params, T_ON).

    Returns:
        Derivative of the state vector
    """

    alpha_0, beta_g, gamma_g, lamda, kappa, nn_params, tf_indices, T_ON = args
    u = state[..., 0]  # Unspliced counts for all genes.
    s = state[..., 1]  # Spliced counts for all genes.

    # Clip state values to increase numerical stability:
    u = jnp.clip(u, 0, 1e3)
    s = jnp.clip(s, 0, 1e3)

    # Compute transcription rates using the neural network
    alpha = alpha_0 * jnp.clip(mlp(nn_params, s[:, tf_indices]), 0, 1e3)  # Shape: (G,)

    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s

    dstate_dt = jnp.stack([du_dt, ds_dt], axis=-1)  # Shape: (2G,)
    return dstate_dt


# Define the complete NumPyro model
@beartype
def model(
    data: Any,
    M_c: Any,
    batch_index: Any,
    tf_indices: Any,
    total_num_cells: int,
    return_alpha: bool = False,
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
    lambda_mean: float = 20.0,
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
):
    """
    NumPyro model for coupled transcription and splicing dynamics.

    Args:
        data: Observed data array of shape (num_cells, num_genes, num_modalities).
        M_c: Number of cells in each metacell.
        batch_index: Array indicating batch assignments for each cell.
        tf_indices: Indices of genes that are TFs.
        total_num_cells: Number of cells in the full dataset.
        n_batch: Number of batches.
        return_alpha: Whether to recompute the transcription rate (alpha), outside the ODE and save it as a deterministic site.
        Tmax_alpha: Alpha parameter for Tmax prior.
        Tmax_beta: Beta parameter for Tmax prior.
        ... (other hyperparameters for priors)
        key: Random number generator key.

    Returns:
        None. Defines the probabilistic model for inference.
    """

    num_cells = int(data.shape[0])
    num_genes = int(data.shape[1])
    num_modalities = int(data.shape[2])
    num_tfs = tf_indices.shape[0]
    batch_size = num_cells
    obs2sample = jax.nn.one_hot(
        batch_index, num_classes=n_batch
    )  # Shape: (num_cells, n_batch)

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

    # scale of alpha
    alpha_0 = numpyro.sample(
        "alpha_0",
        dist.Gamma(0.5, 0.5, validate_args=True).expand([num_genes]).to_event(1),
    )

    # Initial Conditions for ODE, sampling only for spliced and unspliced
    initial_state = numpyro.sample(
        "initial_state",
        dist.Gamma(1.0, 1.0, validate_args=True).expand([1, num_genes, 2]).to_event(1),
    )

    # Neural Net parameters
    in_dim = num_tfs
    out_dim = num_genes

    W = numpyro.sample("W", dist.Normal(0, 0.1), sample_shape=(in_dim, out_dim))

    b = numpyro.sample("b", dist.Normal(0, 0.1), sample_shape=(out_dim,))

    # Organize parameters into a dictionary
    nn_params = {
        "W": W,
        "b": b,
    }

    # Prepare Parameters for ODE Solver
    params = (alpha_0, beta_g, gamma_g, lamda, kappa, nn_params, tf_indices, T_ON)

    # Get Ordered Time Vector
    all_times, time_indices, _ = sort_times_over_all_cells(T_c)

    # Solve the Coupled ODE
    predictions = solve_DE(
        ts=all_times.squeeze(),
        params=params,
        initial_state=initial_state,
        time_step=0.05,
        model=dstate_dt,
        dense=False,
    )

    predictions = numpyro.deterministic("predictions", predictions.astype(jnp.float32))

    predictions_rearranged = numpyro.deterministic(
        "predictions_rearranged", predictions[time_indices.ravel(), :]
    )

    mu_expression = jnp.clip(
        predictions_rearranged[..., :2].squeeze(1), a_min=10 ** (-5), a_max=10 ** (5)
    )

    if return_alpha:
        final_s_clipped = jnp.clip(mu_expression[..., 1], 0, 1e3)
        alpha_cg = jnp.clip(
            alpha_0 * mlp(nn_params, final_s_clipped[:, tf_indices]), 0, 1e3
        )
        alpha_cg = numpyro.deterministic("alpha_cg", alpha_cg)

    # ============= Detection efficiency of spliced and unspliced counts =============== #

    with numpyro.plate("cells", batch_size):
        detection_y_c = numpyro.sample(
            "detection_y_c",
            dist.Gamma(detection_hyp_prior_alpha, detection_hyp_prior_alpha),
        )

    # ===================== Expected expression ======================= #

    mu = numpyro.deterministic("mu", mu_expression * detection_y_c[:, None, None] * M_c)

    # ===================== DATA likelihood ======================= #

    # Likelihood (sampling distribution)
    # We apply a scale factor so that the negative log-likelihood is multiplied
    # by (total_num_cells / batch_size). That ensures an unbiased gradient estimate.
    scale_factor = total_num_cells / batch_size
    with scale(scale=scale_factor):
        data_target = numpyro.sample("data_target", dist.Poisson(mu), obs=data)
