import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from beartype import beartype
from jax import Array
from matplotlib.colors import LogNorm
from matplotlib.figure import Figure


@beartype
def predictions_vs_data(
    observed: Union[np.ndarray, Array],
    predictions: Union[np.ndarray, Array],  # Renamed from "prior"
    bins: int = 50,
    figsize: Tuple[int, int] = (8, 6),
    log_norm: bool = True,
    x_log: bool = True,
    y_log: bool = True,
    log_base: int = 10,
    min_value: float = 5 * 1e-1,
    title: Optional[str] = "Predictions vs Data Density Heatmap",
    xlabel: str = "Observed Data",
    ylabel: str = "Predictions",
    seed: int = 42,
    log_bins: bool = True,
    normalize_cols: bool = False,
) -> plt.Figure:
    """
    Creates a heatmap that visualizes the density of points for observed data vs predictions.

    If the predictions array contains multiple posterior samples, each observed data point
    is paired with all corresponding samples by repeating it.

    All data points are clipped to be at least `min_value` (default: 9e-2). The x and y axes
    are optionally set to a logarithmic scale using the specified `log_base`. If `log_bins=True`,
    then the bins themselves are logarithmically spaced based on `log_base`.

    If `normalize_cols=True`, each column (observed bin) is normalized so that the density
    across predictions sums to 1.

    Args:
        observed (Union[np.ndarray, Array]): Observed data values (num_cells, num_genes, 2).
        predictions (Union[np.ndarray, Array]): Prediction values, possibly with multiple samples.
        bins (int): Number of bins for the 2D histogram. Defaults to 50.
        figsize (Tuple[int, int]): Figure size (width, height). Defaults to (8, 6).
        log_norm (bool): Apply logarithmic normalization to the color scale.
        x_log (bool): Set the x-axis to a logarithmic scale.
        y_log (bool): Set the y-axis to a logarithmic scale.
        log_base (int): Base of the logarithm (default: 2).
        min_value (float): Minimum value for data points (avoids log(0)).
        title (Optional[str]): Title of the plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        seed (int): Random seed for reproducibility.
        log_bins (bool): Use logarithmically spaced bins based on `log_base`.
        normalize_cols (bool): Normalize each column in the density plot.

    Returns:
        matplotlib.figure.Figure: The figure object containing the heatmap.
    """
    # Convert inputs to NumPy arrays
    observed = np.asarray(observed)
    predictions = np.asarray(predictions)

    # Ensure observed data has the same shape as mu (without samples)
    if observed.shape != predictions.shape[1:]:  # Check if first dim is num_samples
        raise ValueError(
            f"Observed data shape {observed.shape} does not match prediction shape {predictions.shape[1:]}"
        )

    # Flatten observed and prediction arrays
    observed = observed.flatten()

    # If multiple posterior samples exist, flatten them correctly
    if predictions.ndim > 3:  # Shape: (num_samples, num_cells, num_genes, 2)
        n_samples = predictions.shape[0]
        predictions = predictions.reshape(
            n_samples, -1
        )  # Shape: (num_samples, num_cells * num_genes * 2)
        observed = np.tile(observed, n_samples)  # Repeat observed for each sample
        predictions = predictions.flatten()
    else:
        predictions = predictions.flatten()

    # Clip values to avoid log(0)
    observed = np.clip(observed, min_value, None)
    predictions = np.clip(predictions, min_value, None)

    # Compute common axis limits from the data
    common_min = min(observed.min(), predictions.min())
    common_max = max(observed.max(), predictions.max())

    # Decide on bin edges
    if log_bins:
        xedges = np.logspace(
            np.log(common_min) / np.log(log_base),
            np.log(common_max) / np.log(log_base),
            bins,
            base=log_base,
        )
        yedges = xedges  # Use same edges for both axes.
    else:
        xedges = np.linspace(common_min, common_max, bins)
        yedges = xedges

    # Compute the 2D histogram
    hist, xedges, yedges = np.histogram2d(observed, predictions, bins=[xedges, yedges])

    # Normalize columns if needed
    if normalize_cols:
        col_sums = hist.sum(axis=0, keepdims=True)
        hist = hist / (col_sums + 1e-8)  # Normalize so each column sums to 1

    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    norm = LogNorm(vmin=max(1, hist[hist > 0].min())) if log_norm else None
    mesh = ax.pcolormesh(
        xedges, yedges, hist.T, shading="auto", cmap="viridis", norm=norm
    )
    fig.colorbar(
        mesh, ax=ax, label="Normalized Density" if normalize_cols else "Density"
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if title is not None:
        ax.set_title(title)

    # Set log scale if needed
    if x_log:
        ax.set_xscale("log", base=log_base)
    if y_log:
        ax.set_yscale("log", base=log_base)

    # Use the same range for both axes
    ax.set_xlim(common_min - 0.1, common_max + 0.5)
    ax.set_ylim(common_min - 0.1, common_max + 0.5)

    plt.tight_layout()
    plt.show()

    return fig


@beartype
def prior_data_geneset(
    prior_samples: Dict[str, Any],
    model_input: Dict[str, Any],
    adata_rna,
    geneset: List[str],
    subplot_size: Tuple[int, int] = (15, 12),
    window_size: int = 40,
    plot_alpha: bool = False,  # Toggle alpha plotting
    alpha_clamp: Tuple[float, float] = (1e-3, 1e5),
    plot_moving_average: bool = True,  # Toggle moving average plotting
) -> Figure:
    """
    Plot prior predictions (all samples) and observed RNA expression for selected genes,
    with an optional overlay of alpha_cg (transcription rates) on the same y-axis, and an optional
    moving average for the observed expression.
    """
    # 1) Shared time axis by averaging across all prior samples
    T_c_obs = np.mean(prior_samples["T_c"], axis=0)  # shape: (num_cells,)
    n_samples = prior_samples["T_c"].shape[0]

    # 2) Sort this time axis so smoothing aligns with ascending time
    sort_idx = np.argsort(T_c_obs)
    T_c_sorted = T_c_obs[sort_idx]

    T_c_sorted = T_c_sorted - np.min(T_c_sorted)

    # 3) Helper function to smooth only the y-values
    @beartype
    def smooth_expression(y: Array, window: int) -> np.ndarray:
        y = np.asarray(y)
        return np.convolve(y, np.ones(window) / window, mode="same")

    # 4) Observed data
    detection_y_c_med = np.mean(
        prior_samples["detection_y_c"], axis=0
    )  # shape: (num_cells,)
    M_c = model_input["M_c"]  # e.g. shape: (num_cells, 1, 1)
    rna_scaling = detection_y_c_med[:, None, None] * M_c

    observed_rna_adjusted = (
        np.stack(
            [
                adata_rna.layers["unspliced"].toarray(),
                adata_rna.layers["spliced"].toarray(),
            ],
            axis=2,
        )
        / rna_scaling
    )  # shape: (num_cells, num_genes, 2)

    # 5) Convert user-specified gene names to indices
    gene_indices = [np.where(adata_rna.var_names == gene)[0][0] for gene in geneset]

    # 6) Subplots
    n_genes = len(geneset)
    n_cols = int(np.ceil(np.sqrt(n_genes)))
    n_rows = int(np.ceil(n_genes / n_cols))
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=subplot_size, sharex=True, sharey=False
    )
    axes = np.atleast_1d(axes).flatten()

    # 7) Loop over each gene
    for ax, gene_idx, gene_name in zip(axes, gene_indices, geneset, strict=False):
        # Observed unspliced/spliced
        observed_unspliced = observed_rna_adjusted[:, gene_idx, 0] + 1e-2
        observed_spliced = observed_rna_adjusted[:, gene_idx, 1] + 1e-2

        # Sort them
        obs_u_sorted = observed_unspliced[sort_idx]
        obs_s_sorted = observed_spliced[sort_idx]

        # Smooth them
        obs_u_smooth = smooth_expression(obs_u_sorted, window_size)
        obs_s_smooth = smooth_expression(obs_s_sorted, window_size)

        # Plot Observed on main axis
        ax.scatter(
            T_c_sorted,
            obs_u_sorted,
            marker="x",
            color="red",
            alpha=0.8,
            label="Observed U",
        )
        ax.scatter(
            T_c_sorted,
            obs_s_sorted,
            marker="x",
            color="blue",
            alpha=0.8,
            label="Observed S",
        )
        if plot_moving_average:
            ax.plot(
                T_c_sorted, obs_u_smooth, color="darkred", linewidth=2, label="Smooth U"
            )
            ax.plot(
                T_c_sorted,
                obs_s_smooth,
                color="darkblue",
                linewidth=2,
                label="Smooth S",
            )

        # Plot all prior samples for unspliced/spliced on main axis
        for sample_idx in range(n_samples):
            unspliced_prior = (
                prior_samples["predictions_rearranged"][sample_idx, 0, :, gene_idx, 0]
                + 1e-2
            )
            spliced_prior = (
                prior_samples["predictions_rearranged"][sample_idx, 0, :, gene_idx, 1]
                + 1e-2
            )

            unspliced_sorted = unspliced_prior[sort_idx]
            spliced_sorted = spliced_prior[sort_idx]

            label_u = "Prior U" if sample_idx == 0 else None
            label_s = "Prior S" if sample_idx == 0 else None

            ax.scatter(
                T_c_sorted,
                unspliced_sorted,
                color="red",
                alpha=0.25 / n_samples,
                label=label_u,
            )
            ax.scatter(
                T_c_sorted,
                spliced_sorted,
                color="blue",
                alpha=0.25 / n_samples,
                label=label_s,
            )

        # Optionally plot alpha on the same y-axis
        if plot_alpha and "alpha_cg" in prior_samples:
            for sample_idx in range(n_samples):
                alpha_prior = prior_samples["alpha_cg"][
                    sample_idx, :, gene_idx
                ]  # shape: (num_cells,)
                alpha_sorted = alpha_prior[sort_idx]

                # Clamp to avoid extreme log scales
                alpha_clamped = np.clip(alpha_sorted, alpha_clamp[0], alpha_clamp[1])

                label_a = "Alpha" if sample_idx == 0 else None
                ax.plot(
                    T_c_sorted,
                    alpha_clamped,
                    color="green",
                    alpha=1,
                    linewidth=1,
                    label=label_a,
                )

        # Finishing touches per subplot
        ax.set_title(gene_name)
        ax.set_xlabel("Time (T_c)")
        ax.set_ylabel("Expression")
        ax.set_yscale("log")

    # Remove extra subplots if any
    for ax in axes[n_genes:]:
        ax.set_visible(False)

    # Create one global legend above the subplots.
    # Gather unique handles and labels from all axes
    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        for handle, label in zip(h, l, strict=False):
            if label is not None and label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=min(4, len(labels)),
        bbox_to_anchor=(0.5, 0.98),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
    return fig


@beartype
def posterior_data_geneset(
    posterior: Dict[str, Any],
    model_input: Dict[str, Any],
    adata_rna,
    geneset: List[str],
    subplot_size: Tuple[int, int] = (15, 12),
    window_size: int = 50,
    plot_alpha: bool = False,  # Toggle alpha plotting
    alpha_clamp: Tuple[float, float] = (1e-3, 1e5),
    plot_moving_average: bool = True,  # Toggle moving average plotting
) -> Figure:
    """
    Plot posterior mean predictions and observed RNA expression for selected genes,
    with an optional overlay of posterior α (transcription rates) on the same y-axis,
    and an optional moving average for the observed expression.
    """

    # Helper function to extract the mean estimate for a given key.
    def get_mean_estimate(key: str) -> np.ndarray:
        if "means" in posterior and key in posterior["means"]:
            candidate = np.asarray(posterior["means"][key])
        elif "medians" in posterior and key in posterior["medians"]:
            candidate = np.asarray(posterior["medians"][key])
        elif "posterior_samples" in posterior and key in posterior["posterior_samples"]:
            candidate = np.mean(np.asarray(posterior["posterior_samples"][key]), axis=0)
        elif "deterministic" in posterior and key in posterior["deterministic"]:
            candidate = np.mean(posterior["deterministic"][key], axis=0)
        else:
            raise ValueError(f"Key '{key}' not found in posterior estimates.")
        return candidate

    # 1) Get the common (mean) time axis from the posterior.
    T_c_est = get_mean_estimate("T_c")  # Expected shape: (num_cells,)
    if T_c_est.ndim != 1:
        raise ValueError(f"Expected T_c to be 1D (per cell), got shape {T_c_est.shape}")
    n_cells = T_c_est.shape[0]

    # 2) Sort the time axis so that smoothing is applied in ascending time.
    sort_idx = np.argsort(T_c_est)
    T_c_sorted = T_c_est[sort_idx]

    T_c_sorted = T_c_sorted - np.min(T_c_sorted)

    # 3) Helper function: smooth only the y-values (expression)
    @beartype
    def smooth_expression(y: Array, window: int) -> np.ndarray:
        y = np.asarray(y)
        return np.convolve(y, np.ones(window) / window, mode="same")

    # 4) Prepare observed data (as in prior_data_geneset)
    detection_y_c_med = get_mean_estimate("detection_y_c")  # shape: (num_cells,)
    M_c = model_input["M_c"]  # e.g. shape: (num_cells, 1, 1)
    rna_scaling = detection_y_c_med[:, None, None] * M_c

    observed_rna_adjusted = (
        np.stack(
            [
                adata_rna.layers["unspliced"].toarray(),
                adata_rna.layers["spliced"].toarray(),
            ],
            axis=2,
        )
        / rna_scaling
    )  # shape: (num_cells, num_genes, 2)

    # 5) Convert the geneset to gene indices.
    gene_indices = [np.where(adata_rna.var_names == gene)[0][0] for gene in geneset]

    # 6) Figure layout.
    n_genes = len(geneset)
    n_cols = int(np.ceil(np.sqrt(n_genes)))
    n_rows = int(np.ceil(n_genes / n_cols))
    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=subplot_size, sharex=True, sharey=False
    )
    axes = np.atleast_1d(axes).flatten()

    # 7) Get the posterior predicted expression ("mu") mean.
    # Expected shape: (num_cells, num_genes, 2) with last dimension: [unspliced, spliced]
    mu_est = get_mean_estimate("predictions_rearranged")[:, 0, ...]

    # 8) Optionally get posterior α if available.
    if plot_alpha:
        try:
            alpha_est = get_mean_estimate(
                "alpha_cg"
            )  # Expected shape: (num_cells, num_genes)
        except ValueError:
            alpha_est = None
            plot_alpha = False

    # 9) Loop over each gene and plot.
    for ax, gene_idx, gene_name in zip(axes, gene_indices, geneset, strict=False):
        # --- Observed data ---
        observed_unspliced = observed_rna_adjusted[:, gene_idx, 0] + 1e-2
        observed_spliced = observed_rna_adjusted[:, gene_idx, 1] + 1e-2

        obs_u_sorted = observed_unspliced[sort_idx]
        obs_s_sorted = observed_spliced[sort_idx]

        obs_u_smooth = smooth_expression(obs_u_sorted, window_size)
        obs_s_smooth = smooth_expression(obs_s_sorted, window_size)

        ax.scatter(
            T_c_sorted,
            obs_u_sorted,
            marker="x",
            color="red",
            alpha=0.2,
            label="Observed U",
        )
        ax.scatter(
            T_c_sorted,
            obs_s_sorted,
            marker="x",
            color="blue",
            alpha=0.2,
            label="Observed S",
        )
        if plot_moving_average:
            ax.plot(
                T_c_sorted, obs_u_smooth, color="darkred", linewidth=2, label="Smooth U"
            )
            ax.plot(
                T_c_sorted,
                obs_s_smooth,
                color="darkblue",
                linewidth=2,
                label="Smooth S",
            )

        # --- Posterior predictions ---
        unspliced_pred = mu_est[:, gene_idx, 0] + 1e-2  # shape: (num_cells,)
        spliced_pred = mu_est[:, gene_idx, 1] + 1e-2  # shape: (num_cells,)

        unspliced_pred_sorted = unspliced_pred[sort_idx]
        spliced_pred_sorted = spliced_pred[sort_idx]

        ax.plot(
            T_c_sorted,
            unspliced_pred_sorted,
            color="red",
            linestyle="--",
            linewidth=2,
            label="Post. U",
        )
        ax.plot(
            T_c_sorted,
            spliced_pred_sorted,
            color="blue",
            linestyle="--",
            linewidth=2,
            label="Post. S",
        )

        # --- Optionally plot posterior α on the same y-axis ---
        if plot_alpha and alpha_est is not None:
            alpha_gene = alpha_est[:, gene_idx]  # shape: (num_cells,)
            alpha_sorted = alpha_gene[sort_idx]
            alpha_clamped = np.clip(alpha_sorted, alpha_clamp[0], alpha_clamp[1])
            ax.plot(
                T_c_sorted,
                alpha_clamped,
                color="green",
                linestyle="-",
                linewidth=2,
                label="Post. Alpha",
            )

        ax.set_title(gene_name)
        ax.set_xlabel("Time (T_c)")
        ax.set_ylabel("Expression")
        ax.set_yscale("log")

    for ax in axes[n_genes:]:
        ax.set_visible(False)

    # Create one global legend above the subplots.
    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        for handle, label in zip(h, l, strict=False):
            if label is not None and label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=min(4, len(labels)),
        bbox_to_anchor=(0.5, 0.98),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    return fig


def plot_elbo_loss(
    losses, directory=None, figsize=(12, 5), save=False, dpi=300, save_format="png"
):
    """
    Plot the ELBO loss over all iterations and the last 10%, with optional saving.

    Parameters
    ----------
    losses : list or np.ndarray
        List or array of ELBO loss values over iterations.
    directory : str, optional
        Directory where figures will be saved (required if save=True).
    figsize : tuple, optional
        Figure size for the plots (default: (12, 5)).
    save : bool, optional
        Whether to save the plots (default: False).
    dpi : int, optional
        Resolution of the saved figure in dots per inch (default: 300).
    save_format : str, optional
        File format for saving figures (default: "png", e.g., "pdf", "svg", etc.).
    """
    if save and directory is None:
        warnings.warn(
            "Saving is enabled, but no directory was provided. Figures will not be saved.",
            UserWarning,
        )

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Plot all iterations
    axes[0].plot(range(len(losses)), losses, label="Scaled ELBO Loss")
    axes[0].set_xlabel("Iteration")
    axes[0].set_ylabel("Scaled ELBO Loss")
    axes[0].set_title("SVI Training Loss with Scaled ELBO")
    axes[0].legend()
    axes[0].grid(True)

    # Ensure last_10_percent is at least 1 to avoid an empty slice
    last_10_percent = max(1, int(np.round(len(losses) / 10)))

    # Plot last 10% of iterations
    axes[1].plot(
        range(len(losses) - last_10_percent, len(losses)),
        losses[-last_10_percent:],
        label="Scaled ELBO Loss",
    )
    axes[1].set_xlabel("Iteration")
    axes[1].set_ylabel("Scaled ELBO Loss")
    axes[1].set_title("SVI Training Loss (Last 10%)")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()

    if save and directory:
        plt.savefig(
            f"{directory}/ELBOloss_All.{save_format}", dpi=dpi, format=save_format
        )

    plt.show()
