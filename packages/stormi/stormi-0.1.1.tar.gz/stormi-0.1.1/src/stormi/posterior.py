import jax
from numpyro.infer import Predictive


def extract_posterior_estimates(
    model,
    guide,
    svi,
    svi_state,
    model_input: dict = None,
    quantiles: list = [0.5, 0.05, 0.95],
    num_samples: int = 0,
    modes: list = [],
    deterministic_sites: list = [],
):
    """
    Extract posterior estimates.

    This function returns transformed quantiles/medians, posterior samples,
    and if mode 1 is specified, the posterior mean estimates (combining global
    and local parameters) using the guide's extract_all_means method. It also returns
    deterministic site samples if deterministic sites is specified.

    Parameters
    ----------
    model : Callable
        The model used in SVI.
    guide : Callable
        The autoguide used in SVI.
    svi : SVI
        The trained SVI object.
    svi_state : SVIState
        The SVI state containing learned parameters.
    model_input : dict, optional
        Dictionary containing the model inputs, as returned from the train_svi function.
    quantiles : list of float, optional
        A list of quantiles to extract (e.g. [0.5, 0.05, 0.95]).
    num_samples : int, optional
        Number of posterior samples to draw (0 means no sampling).
    modes : list, optional
        A list of mode codes. If 1 is in modes, the function extracts the mean
        (using guide.extract_all_means) and saves it under key 'means'.
    deterministic_sites : list, optional
        A list with names of deterministic sites to extract. If num_samples is 0
        it will use 5 samples by default.

    Returns
    -------
    results : dict
        A dictionary with keys:
          - "quantiles": Quantile estimates (if quantiles other than 0.5 are provided).
          - "median": Median estimates (if 0.5 is in quantiles).
          - "posterior_samples": Samples from the posterior (if num_samples > 0).
          - "means": Combined posterior means (global and local) if 1 is in modes.
    """
    # 1) Get the raw variational parameters.
    raw_params = svi.get_params(svi_state)
    # Stop gradients to force the values to be concrete.
    raw_params = jax.tree_map(jax.lax.stop_gradient, raw_params)

    results = {}

    # 2) Extract transformed quantiles (excluding 0.5) and median if needed
    quantiles_to_extract = [q for q in quantiles if q != 0.5]
    if quantiles_to_extract:
        results["quantiles"] = guide.quantiles(raw_params, quantiles_to_extract)
    if 0.5 in quantiles:
        results["median"] = guide.median(raw_params)

    # 3) Draw posterior samples if requested
    if num_samples > 0:
        rng_key = jax.random.PRNGKey(0)
        posterior_samples = guide.sample_posterior(
            rng_key, raw_params, sample_shape=(num_samples,)
        )
        results["posterior_samples"] = posterior_samples

    # 4) If mode 1 is specified, extract the combined posterior means.
    if 1 in modes:
        if model_input is None or "data" not in model_input:
            raise ValueError(
                "To extract means, model_input must contain the key 'data'."
            )
        # Use the guide's extraction function to obtain global and local means.
        global_means, local_means = guide.extract_all_means(
            svi_state, svi, model_input["data"]
        )
        # Combine the dictionaries. In case of duplicate keys, local_means will override.
        combined_means = {**global_means, **local_means}
        results["means"] = combined_means

    # 5) Return deterministic sites if requested:

    if deterministic_sites:
        rng_key = jax.random.PRNGKey(0)
        if num_samples == 0:
            num_samples = 5
        predictive = Predictive(
            model,
            guide=guide,  # include the guide so that latent variables come from the variational posterior
            params=raw_params,
            return_sites=deterministic_sites,
            num_samples=num_samples,
        )
        posterior_samples = predictive(rng_key, **model_input)

        results["deterministic"] = posterior_samples

    return results
