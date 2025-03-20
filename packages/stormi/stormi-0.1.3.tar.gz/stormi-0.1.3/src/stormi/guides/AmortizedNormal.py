from functools import partial

import jax
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from numpyro.handlers import block, seed
from numpyro.infer.autoguide import AutoGuideList, AutoNormal

################################################################################
# 1) Shared forward pass function: _amortized_network
################################################################################


def _amortized_network(params_dict: dict, data_array: jnp.ndarray):
    """
    Performs the forward pass of the neural network for the amortized guide,
    returning loc/scale for 't_c', 'detection_y_c', and optionally for 'detection_l_c'.

    Args:
        params_dict (dict): Dictionary of NN parameters. Must include:
            V_shared, c_shared,
            V_t_c, c_t_c, V_out_t_c, c_out_t_c,
            V_det, c_det, V_out_det, c_out_det,
            [optional] V_det_l, c_det_l, V_out_det_l, c_out_det_l
        data_array (jnp.ndarray): shape (n_cells, n_genes, n_mods).

    Returns:
        If detection_l_c branch is present:
          (loc_t_c_raw, scale_t_c, loc_det_raw, scale_det, loc_det_l_raw, scale_det_l)
        Otherwise:
          (loc_t_c_raw, scale_t_c, loc_det_raw, scale_det)
    """

    def normalize_by_total_counts(data_2d):
        total_counts = jnp.sum(data_2d, axis=1, keepdims=True)
        return data_2d / (total_counts + 1e-8)

    n_cells, n_genes, n_mods = data_array.shape
    d_in = n_genes * n_mods

    data_2d = data_array.reshape((n_cells, d_in))
    data_2d_log1p = jnp.log1p(normalize_by_total_counts(data_2d))

    # Extract common parameters
    V_shared = params_dict["V_shared"]
    c_shared = params_dict["c_shared"]
    V_t_c = params_dict["V_t_c"]
    c_t_c = params_dict["c_t_c"]
    V_out_t_c = params_dict["V_out_t_c"]
    c_out_t_c = params_dict["c_out_t_c"]
    V_det = params_dict["V_det"]
    c_det = params_dict["c_det"]
    V_out_det = params_dict["V_out_det"]
    c_out_det = params_dict["c_out_det"]

    # Shared layer
    hidden_shared = jax.nn.elu(
        jnp.einsum("cd,dh->ch", data_2d_log1p, V_shared) + c_shared
    )

    # t_c branch
    hidden_t_c = jax.nn.elu(jnp.einsum("ch,hm->cm", hidden_shared, V_t_c) + c_t_c)
    out_raw_t_c = jnp.einsum("cm,mo->co", hidden_t_c, V_out_t_c) + c_out_t_c
    loc_t_c_raw = out_raw_t_c[:, 0]
    scale_t_c_raw = out_raw_t_c[:, 1]
    scale_t_c = jax.nn.softplus(scale_t_c_raw) + 1e-3

    # detection_y_c branch
    hidden_det = jax.nn.elu(jnp.einsum("ch,hm->cm", hidden_shared, V_det) + c_det)
    out_raw_det = jnp.einsum("cm,mo->co", hidden_det, V_out_det) + c_out_det
    loc_det_raw = out_raw_det[:, 0]
    scale_det_raw = out_raw_det[:, 1]
    scale_det = jax.nn.softplus(scale_det_raw) + 1e-3

    # ----- Optional branch: detection_l_c -----
    if "V_det_l" in params_dict:
        V_det_l = params_dict["V_det_l"]
        c_det_l = params_dict["c_det_l"]
        V_out_det_l = params_dict["V_out_det_l"]
        c_out_det_l = params_dict["c_out_det_l"]

        hidden_det_l = jax.nn.elu(
            jnp.einsum("ch,hm->cm", hidden_shared, V_det_l) + c_det_l
        )
        out_raw_det_l = jnp.einsum("cm,mo->co", hidden_det_l, V_out_det_l) + c_out_det_l
        loc_det_l_raw = out_raw_det_l[:, 0]
        scale_det_l_raw = out_raw_det_l[:, 1]
        scale_det_l = jax.nn.softplus(scale_det_l_raw) + 1e-3

        return (
            loc_t_c_raw,
            scale_t_c,
            loc_det_raw,
            scale_det,
            loc_det_l_raw,
            scale_det_l,
        )
    else:
        return loc_t_c_raw, scale_t_c, loc_det_raw, scale_det


################################################################################
# 2) The amortized_guide function
################################################################################


def amortized_guide(*args, predict_detection_l_c: bool = True, **kwargs):
    """
    A flexible amortized guide for local variables 't_c' and 'detection_y_c', and
    optionally 'detection_l_c'. It retrieves 'data' (from the first positional argument
    or kwargs["data"]), defines network parameters, then calls _amortized_network(...) to
    get loc/scale for the latents, sampling them with a plate over cells.

    Returns:
      dict: contains "t_c", "detection_y_c", and optionally "detection_l_c"
    """

    # 1) Retrieve data
    data = kwargs.get("data", None)
    if data is None and args:
        data = args[0]
    if data is None:
        raise ValueError(
            "amortized_guide expects 'data' as a keyword or first positional argument!"
        )

    # 2) Data shape
    n_cells, n_genes, n_mods = data.shape
    d_in = n_genes * n_mods

    # 3) Define network dimensions
    hidden_dim_shared = 256
    hidden_dim_t_c = 128
    hidden_dim_det = 128
    out_dim = 2  # (loc, scale)

    # 4) Create the parameters (NumPyro param store)
    V_shared = numpyro.param(
        "V_shared",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(1)), (d_in, hidden_dim_shared)
        )
        * 0.01,
    )
    c_shared = numpyro.param("c_shared", jnp.zeros((hidden_dim_shared,)))

    V_t_c = numpyro.param(
        "V_t_c",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(2)),
            (hidden_dim_shared, hidden_dim_t_c),
        )
        * 0.01,
    )
    c_t_c = numpyro.param("c_t_c", jnp.zeros((hidden_dim_t_c,)))
    V_out_t_c = numpyro.param(
        "V_out_t_c",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(3)), (hidden_dim_t_c, out_dim)
        )
        * 0.01,
    )
    c_out_t_c = numpyro.param("c_out_t_c", jnp.zeros((out_dim,)))

    V_det = numpyro.param(
        "V_det",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(4)),
            (hidden_dim_shared, hidden_dim_det),
        )
        * 0.01,
    )
    c_det = numpyro.param("c_det", jnp.zeros((hidden_dim_det,)))
    V_out_det = numpyro.param(
        "V_out_det",
        jax.random.normal(
            jax.lax.stop_gradient(jax.random.PRNGKey(5)), (hidden_dim_det, out_dim)
        )
        * 0.01,
    )
    c_out_det = numpyro.param("c_out_det", jnp.zeros((out_dim,)))

    net_params = {
        "V_shared": V_shared,
        "c_shared": c_shared,
        "V_t_c": V_t_c,
        "c_t_c": c_t_c,
        "V_out_t_c": V_out_t_c,
        "c_out_t_c": c_out_t_c,
        "V_det": V_det,
        "c_det": c_det,
        "V_out_det": V_out_det,
        "c_out_det": c_out_det,
    }

    # ----- Optional: add parameters for detection_l_c branch -----
    if predict_detection_l_c:
        V_det_l = numpyro.param(
            "V_det_l",
            jax.random.normal(
                jax.lax.stop_gradient(jax.random.PRNGKey(6)),
                (hidden_dim_shared, hidden_dim_det),
            )
            * 0.01,
        )
        c_det_l = numpyro.param("c_det_l", jnp.zeros((hidden_dim_det,)))
        V_out_det_l = numpyro.param(
            "V_out_det_l",
            jax.random.normal(
                jax.lax.stop_gradient(jax.random.PRNGKey(7)), (hidden_dim_det, out_dim)
            )
            * 0.01,
        )
        c_out_det_l = numpyro.param("c_out_det_l", jnp.zeros((out_dim,)))
        net_params.update(
            {
                "V_det_l": V_det_l,
                "c_det_l": c_det_l,
                "V_out_det_l": V_out_det_l,
                "c_out_det_l": c_out_det_l,
            }
        )

    # 5) Call the shared forward pass
    outputs = _amortized_network(net_params, data)
    if predict_detection_l_c:
        loc_t_c, scale_t_c, loc_det, scale_det, loc_det_l, scale_det_l = outputs
    else:
        loc_t_c, scale_t_c, loc_det, scale_det = outputs

    # 6) Sample the latents with appropriate transforms
    with numpyro.plate("cells", n_cells):
        t_c = numpyro.sample("t_c", dist.Normal(loc_t_c, scale_t_c))
        detection_y_c = numpyro.sample(
            "detection_y_c",
            dist.TransformedDistribution(
                dist.Normal(loc_det, scale_det), dist.transforms.ExpTransform()
            ),
        )
        if predict_detection_l_c:
            detection_l_c = numpyro.sample(
                "detection_l_c",
                dist.TransformedDistribution(
                    dist.Normal(loc_det_l, scale_det_l), dist.transforms.ExpTransform()
                ),
            )

    out_dict = {"t_c": t_c, "detection_y_c": detection_y_c}
    if predict_detection_l_c:
        out_dict["detection_l_c"] = detection_l_c

    return out_dict


################################################################################
# 3) Extraction helper functions
################################################################################


def extract_global_posterior_mean(guide, svi_state, svi):
    """
    Extract posterior means for global parameters from the AutoNormal sub-guide.
    This function uses the AutoNormal sub-guide's built-in transformation (via its median method).
    """
    auto_guide = guide._guides[0]  # AutoNormal sub-guide (global parameters)
    params = svi.get_params(svi_state)
    return auto_guide.median(params)


def extract_local_posterior_mean(guide, svi_state, svi, data):
    """
    Extract posterior means for local variables (from the amortized guide):
      - t_c mean = loc_t_c (Normal)
      - detection_y_c mean = exp(loc_det) (ExpTransform)
      - detection_l_c mean = exp(loc_det_l) (if available)
    """
    params = svi.get_params(svi_state)
    needed_keys = [
        "V_shared",
        "c_shared",
        "V_t_c",
        "c_t_c",
        "V_out_t_c",
        "c_out_t_c",
        "V_det",
        "c_det",
        "V_out_det",
        "c_out_det",
    ]
    # Add keys for detection_l_c if available.
    if "V_det_l" in params:
        needed_keys.extend(["V_det_l", "c_det_l", "V_out_det_l", "c_out_det_l"])

    for k in needed_keys:
        if k not in params:
            raise ValueError(
                f"Missing param '{k}' in SVI state, cannot extract local posterior means."
            )

    net_params = {k: params[k] for k in needed_keys}

    outputs = _amortized_network(net_params, data)
    if len(outputs) == 6:
        loc_t_c, scale_t_c, loc_det, scale_det, loc_det_l, scale_det_l = outputs
    else:
        loc_t_c, scale_t_c, loc_det, scale_det = outputs

    t_c_mean = loc_t_c
    detection_y_c_mean = jnp.exp(loc_det)

    result = {"t_c": t_c_mean, "detection_y_c": detection_y_c_mean}
    if len(outputs) == 6:
        detection_l_c_mean = jnp.exp(loc_det_l)
        result["detection_l_c"] = detection_l_c_mean

    return result


def extract_posterior_means(guide, svi_state, svi, data):
    """
    Convenience wrapper returning (global_means, local_means).
    """
    global_means = extract_global_posterior_mean(guide, svi_state, svi)
    local_means = extract_local_posterior_mean(guide, svi_state, svi, data)
    return global_means, local_means


################################################################################
# 4) The AmortizedNormal class
################################################################################


class AmortizedNormal:
    def __init__(self, model, predict_detection_l_c: bool = True, init_loc_fn=None):
        """
        A guide that hides t_c, detection_y_c (and optionally detection_l_c) from AutoNormal,
        delegating them to the amortized_guide function.
        """
        self.model = model
        self.predict_detection_l_c = predict_detection_l_c
        self.guide_list = AutoGuideList(model)

        # (Optional) seed the model for consistent param init
        seeded_model = seed(model, rng_seed=0)

        # Build the list of sites to hide.
        hide_list = [
            "t_c",
            "detection_y_c",
            "T_c",
            "predictions",
            "mu",
            "d_cr",
            "mu_atac",
            "predictions_rearranged",
            "alpha_cg",
            "additive_term",
            "normalizing_term",
            "P_rh",
        ]
        if predict_detection_l_c:
            hide_list.append("detection_l_c")

        blocked_model = block(seeded_model, hide=hide_list)
        auto_normal_guide = AutoNormal(blocked_model, init_loc_fn=init_loc_fn)
        self.guide_list.append(auto_normal_guide)

        self.guide_list.append(
            partial(amortized_guide, predict_detection_l_c=self.predict_detection_l_c)
        )

    def __call__(self, *args, **kwargs):
        return self.guide_list(*args, **kwargs)

    def quantiles(self, params, quantiles):
        return self.guide_list.quantiles(params, quantiles)

    def median(self, params):
        return self.guide_list.median(params)

    def sample_posterior(self, rng_key, params, sample_shape=()):
        return self.guide_list.sample_posterior(rng_key, params, sample_shape)

    def get_posterior(self, params):
        return self.guide_list.get_posterior(params)

    # ---- Additional convenience methods for extraction ----
    def extract_global_means(self, svi_state, svi):
        return extract_global_posterior_mean(self.guide_list, svi_state, svi)

    def extract_local_means(self, svi_state, svi, data):
        return extract_local_posterior_mean(self.guide_list, svi_state, svi, data)

    def extract_all_means(self, svi_state, svi, data):
        return extract_posterior_means(self.guide_list, svi_state, svi, data)
