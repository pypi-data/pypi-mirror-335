from __future__ import annotations

from typing import Any, Dict

import diffrax as dfx
import jax
import jax.numpy as jnp
import jax.random as jr
import numpyro
import numpyro.distributions as dist
from beartype import beartype
from numpyro.distributions import TruncatedNormal
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


# Define the drift function using the MLP
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

    alpha_0, beta_g, gamma_g, lamda, kappa, nn_params, tf_indices, d_constant, T_ON = (
        args
    )
    u = state[..., 0]  # Unspliced counts for all genes.
    s = state[..., 1]  # Spliced counts for all genes.
    p = state[..., 2]  # Proteins for all genes.

    # Clip state values to increase numerical stability:
    u = jnp.clip(u, 0, 1e3)
    s = jnp.clip(s, 0, 1e3)
    p = jnp.clip(p, 0, 1e3)

    # Compute transcription rates using the neural network
    alpha = alpha_0 * jnp.clip(mlp(nn_params, p[:, tf_indices]), 0, 1e3)  # Shape: (G,)

    du_dt = alpha - beta_g * u
    ds_dt = beta_g * u - gamma_g * s
    # Compute dp_dt only for TF indices
    dp_dt = jnp.zeros_like(u)
    dp_dt = dp_dt.at[:, tf_indices].set(
        lamda * s[:, tf_indices] - kappa * p[:, tf_indices]
    )

    dstate_dt = jnp.stack([du_dt, ds_dt, dp_dt], axis=-1)  # Shape: (3G,)
    return dstate_dt


# Define the diffusion function using a constant
@beartype
def diffusion_fn(t, state, args):
    """
    Compute the diffusion term for the coupled system.

    Args:
        t: Time scalar.
        state: State vector [u_1, ..., u_G, s_1, ..., s_G].
        args: Tuple containing parameters (G, beta_g, gamma_g, nn_params, T_ON).

    Returns:
        Diffusion term for the state vector.
    """

    ## only extract the second-to-last element of args---this is the diffusion constant
    d_constant = args[-2]

    u_coeff = (
        d_constant * jnp.ones_like(state[..., 0])
    )  # Constant diffusion for unspliced mRNA (account for un-resolved transcriptional processes)
    s_coeff = jnp.zeros_like(state[..., 1])  # No diffusion for spliced mRNA
    p_coeff = jnp.zeros_like(state[..., 2])  # No diffusion for proteins

    return jnp.stack([u_coeff, s_coeff, p_coeff], axis=-1)  # Shape: (3G,)


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
    diffusion_constant_prior_lower: float = 1e-2,
    diffusion_constant_prior_upper: float = 1,
    sde_rng_key: Any = jr.PRNGKey(0),
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
        Tmax_alpha: Alpha parameter for Tmax prior.
        Tmax_beta: Beta parameter for Tmax prior.
        ... (other hyperparameters for priors)
        sde_rng_key: Random number generator key.

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

    # Rate Parameters
    # For β (splicing rates): desired mean = splicing_rate_mean_hyp_prior_mean,
    # variance = splicing_rate_mean_hyp_prior_mean^2 / splicing_rate_alpha_hyp_prior_alpha.
    sigma_beta = jnp.sqrt(jnp.log1p(1.0 / splicing_rate_alpha_hyp_prior_alpha))
    mu_beta = jnp.log(splicing_rate_mean_hyp_prior_mean) - 0.5 * jnp.log1p(
        1.0 / splicing_rate_alpha_hyp_prior_alpha
    )
    log_beta = numpyro.sample(
        "log_beta_g", dist.Normal(mu_beta, sigma_beta).expand([num_genes]).to_event(1)
    )
    beta_g = jnp.exp(log_beta)

    # For γ (degradation rates): desired mean = degradation_rate_mean_hyp_prior_mean,
    # variance = degradation_rate_mean_hyp_prior_mean^2 / degradation_rate_alpha_hyp_prior_alpha.
    sigma_gamma = jnp.sqrt(jnp.log1p(1.0 / degradation_rate_alpha_hyp_prior_alpha))
    mu_gamma = jnp.log(degradation_rate_mean_hyp_prior_mean) - 0.5 * jnp.log1p(
        1.0 / degradation_rate_alpha_hyp_prior_alpha
    )
    log_gamma = numpyro.sample(
        "log_gamma_g",
        dist.Normal(mu_gamma, sigma_gamma).expand([num_genes]).to_event(1),
    )
    gamma_g = jnp.exp(log_gamma)

    # For translation rate λ: desired mean = lambda_mean, variance = lambda_mean^2 / lambda_alpha.
    sigma_lambda = jnp.sqrt(jnp.log1p(1.0 / lambda_alpha))
    mu_lambda = jnp.log(lambda_mean) - 0.5 * jnp.log1p(1.0 / lambda_alpha)
    log_lambda = numpyro.sample(
        "log_lambda", dist.Normal(mu_lambda, sigma_lambda).expand([num_tfs]).to_event(1)
    )
    lamda = jnp.exp(log_lambda)

    # For protein degradation rate κ: desired mean = kappa_mean, variance = kappa_mean^2 / kappa_alpha.
    sigma_kappa = jnp.sqrt(jnp.log1p(1.0 / kappa_alpha))
    mu_kappa = jnp.log(kappa_mean) - 0.5 * jnp.log1p(1.0 / kappa_alpha)
    log_kappa = numpyro.sample(
        "log_kappa", dist.Normal(mu_kappa, sigma_kappa).expand([num_tfs]).to_event(1)
    )
    kappa = jnp.exp(log_kappa)

    # For the scale of α in the expression model, α₀.
    sigma_alpha0 = jnp.sqrt(jnp.log(2.0))
    mu_alpha0 = -0.5 * jnp.log(2.0)
    log_alpha0 = numpyro.sample(
        "log_alpha_0",
        dist.Normal(mu_alpha0, sigma_alpha0).expand([num_genes]).to_event(1),
    )
    alpha_0 = jnp.exp(log_alpha0)

    with numpyro.plate("cells", batch_size):
        # Sample t_c from a truncated normal so that t_c is always between -20 and 20.
        t_c = numpyro.sample("t_c", TruncatedNormal(low=-13, high=15.0, loc=1, scale=4))

    T_c = numpyro.deterministic("T_c", t_c)

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

    # Neural Net parameters
    in_dim = num_tfs
    out_dim = num_genes

    W = numpyro.sample("W", dist.Normal(0, 0.025), sample_shape=(in_dim, out_dim))

    b = numpyro.sample("b", dist.Normal(0, 0.025), sample_shape=(out_dim,))

    # Organize parameters into a dictionary
    nn_params = {
        "W": W,
        "b": b,
    }

    # # sample diffusion constant
    # d_constant = numpyro.sample(
    #     'd_constant',
    #     dist.Uniform(
    #         diffusion_constant_prior_lower,
    #         diffusion_constant_prior_upper
    #     )
    # )

    # # Global hyperparameter controlling the rate of diffusion constants.
    # global_rate = numpyro.sample("global_rate", dist.Gamma(2.0, 0.1))
    # # Sample gene-specific diffusion constants (one per gene)
    # d_constant = numpyro.sample(
    #     "d_constant",
    #     dist.Exponential(global_rate).expand((num_genes,))
    # )

    d_constant = numpyro.deterministic("d_constant", jnp.full((num_genes,), 10 ** (-9)))

    # Prepare Parameters for ODE Solver
    params = (
        alpha_0,
        beta_g,
        gamma_g,
        lamda,
        kappa,
        nn_params,
        tf_indices,
        d_constant,
        0.0,
    )

    # Get Ordered Time Vector
    all_times, time_indices, _ = sort_times_over_all_cells(T_c)

    # build the brownian motion tree that will be used to instantiate the diffusion process

    # Some notes:
    # 1. here, it is a SCALAR diffusion process that will be applied the same to all (unspliced) genes...this is determined by shape=()
    # 2. we need to change the key if we want each call of the model to result in a different SDE path
    # 3. Our limits of integration cannot be learnable (it complains about t0 being non-autodifferentiable).
    #   So we set them to -10 and 10, and then grab the values at the time points we want after the fact.
    brownian_motion = dfx.VirtualBrownianTree(
        -15, 15.0, tol=1e-1, shape=(), key=sde_rng_key
    )

    # Solve the Coupled DE
    predictions = solve_DE(
        ts=all_times.squeeze(),
        params=params,
        initial_state=initial_state,
        time_step=0.01,
        drift=dstate_dt,
        diffusion=diffusion_fn,
        bm=brownian_motion,
        dense=False,
        t0=-15.0,
        t1=15.0,
    )

    predictions = numpyro.deterministic("predictions", predictions.astype(jnp.float32))

    predictions_rearranged = numpyro.deterministic(
        "predictions_rearranged", predictions[time_indices.ravel(), :]
    )

    mu_expression = jnp.clip(
        predictions_rearranged[..., :2].squeeze(1), a_min=10 ** (-5), a_max=10 ** (7)
    )

    if return_alpha:
        final_p_clipped = jnp.clip(predictions_rearranged[..., 2].squeeze(1), 0, 1e3)
        alpha_cg = jnp.clip(
            alpha_0 * mlp(nn_params, final_p_clipped[:, tf_indices]), 0, 1e3
        )
        alpha_cg = numpyro.deterministic("alpha_cg", alpha_cg)

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

    beta = ((detection_hyp_prior_alpha / (obs2sample @ detection_mean_y_e)).T)[0, ...]

    with numpyro.plate("cells", batch_size):
        detection_y_c = numpyro.sample(
            "detection_y_c", dist.Gamma(detection_hyp_prior_alpha, beta[:, 0, 0])
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

    # sample the gene-additive mean
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
    s_g_gene_add_mean = jnp.clip(s_g_gene_add_mean, a_min=1e-2, a_max=1e3)

    # Fixed concentration value (the higher c0 is, the lower the variance)
    c0 = 10.0

    # Compute the LogNormal parameters so that:
    #   E[s_g_gene_add] = s_g_gene_add_mean
    #   Var[s_g_gene_add] = s_g_gene_add_mean^2 / c0
    sigma_ln = jnp.sqrt(jnp.log1p(1.0 / c0))  # sqrt( ln(1+1/c0) )
    mu_ln = jnp.log(s_g_gene_add_mean) - 0.5 * jnp.log1p(1.0 / c0)

    # Now sample the gene-additive term from a LogNormal.
    log_s_g_gene_add = numpyro.sample(
        "log_s_g_gene_add",
        dist.Normal(mu_ln, sigma_ln).expand([n_batch, num_genes, 2]).to_event(3),
    )
    s_g_gene_add = jnp.exp(log_s_g_gene_add)

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

    # ===================== Expected expression ======================= #

    additive_term = numpyro.deterministic(
        "additive_term", jnp.einsum("cb,bgi->cgi", obs2sample, s_g_gene_add)
    )

    normalizing_term = numpyro.deterministic(
        "normalizing_term",
        detection_y_c[:, None, None] * detection_y_i * detection_y_gi * M_c,
    )

    mu = numpyro.deterministic("mu", (mu_expression + additive_term) * normalizing_term)

    # ===================== DATA likelihood ======================= #

    concentration = stochastic_v_ag * M_c
    rate = concentration / mu

    # Likelihood (sampling distribution)
    # We apply a scale factor so that the negative log-likelihood is multiplied
    # by (total_num_cells / batch_size). That ensures an unbiased gradient estimate.
    scale_factor = total_num_cells / batch_size
    with scale(scale=scale_factor):
        data_target = numpyro.sample(
            "data_target", dist.GammaPoisson(concentration, rate), obs=data
        )
