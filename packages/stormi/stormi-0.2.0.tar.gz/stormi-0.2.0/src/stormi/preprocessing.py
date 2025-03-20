from __future__ import annotations

import math
import warnings
from typing import List, Optional, Tuple, Union

import jax.numpy as jnp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyranges as pr
import scanpy as sc
import scipy.sparse as sp
from anndata import AnnData
from beartype import beartype
from pybiomart import Server
from scipy.sparse import csr_matrix
from scvi.model import MULTIVI, SCVI


def compute_pca_complexity(
    adata: AnnData, variance_threshold: float = 0.9, n_comps: int = 50
) -> int:
    """
    Computes a simple measure of dataset complexity: the number of principal components
    required to explain at least `variance_threshold` of the variance.

    If PCA has not yet been computed, this function runs sc.pp.pca on the adata.
    """
    if "pca" not in adata.uns:
        sc.pp.pca(adata, n_comps=n_comps)
    variance_ratio = adata.uns["pca"]["variance_ratio"]
    cum_var = np.cumsum(variance_ratio)
    complexity = int(np.searchsorted(cum_var, variance_threshold)) + 1
    return complexity


def default_n_latent(n_obs: int, complexity: int) -> int:
    """
    Computes a default latent dimension.
    Base is 20 + 10 * log10(n_obs/1e3) and then adjusted upward by 0.5 * complexity.
    Capped at 150.
    """
    base = 20 + 10 * math.log10(n_obs / 1000)
    return int(max(20, min(150, base + 0.5 * complexity)))


def default_n_hidden(n_obs: int, complexity: int) -> int:
    """
    Computes a default number of hidden units per layer.
    Base is 256 + 64 * log10(n_obs/1e3) and then adjusted upward by 8 * complexity.
    Capped at 1024.
    """
    base = 256 + 64 * math.log10(n_obs / 1000)
    return int(max(256, min(1024, base + 8 * complexity)))


def default_n_layers(n_obs: int, complexity: int) -> int:
    """
    Returns a default number of layers.
    For fewer than 1e5 cells, use 2 layers if complexity < 20, else 3.
    For larger datasets, use 3 layers if complexity < 30, else 4.
    """
    if n_obs < 1e5:
        return 2 if complexity < 20 else 3
    else:
        return 3 if complexity < 30 else 4


def default_epochs(n_obs: int, complexity: int) -> int:
    """
    Computes a default number of training epochs.
    Base increases with n_obs and is scaled by the complexity.
    For 1e4 cells with moderate complexity, ~600 epochs are used.
    The final number is increased by a factor (1 + complexity/50)
    to ensure higher iterations for more complex datasets.
    """
    base = 600 + 200 * math.log10(n_obs / 10000)
    return int(max(400, base * (1 + complexity / 50)))


def run_scvi(
    adata_rna: AnnData,
    adata_atac: Optional[AnnData] = None,
    latent_key: str = "X_scVI",
    n_hidden: Optional[int] = None,
    n_latent: Optional[int] = None,
    n_layers: Optional[int] = None,
    dropout_rate: Optional[float] = None,
    max_epochs: Optional[int] = None,
    save_model_path: Optional[str] = None,
    variance_threshold: float = 0.9,
    n_comps: int = 50,
    **kwargs,
) -> Union[AnnData, Tuple[AnnData, AnnData]]:
    """
    Runs scVI (if only RNA is provided) or multiVI (if both RNA and ATAC are provided)
    on the input AnnData object(s). Hyperparameters are chosen automatically based on the
    number of cells and a measure of dataset complexity (computed via PCA) unless explicitly
    provided by the user.

    The latent representation is stored in .obsm under the key `latent_key` (default "X_scVI").
    Optionally, the trained model is saved to a user-defined directory.

    Parameters
    ----------
    adata_rna : AnnData
        AnnData object with RNA counts.
    adata_atac : Optional[AnnData]
        AnnData object with ATAC counts. Must have the same cells (and order) as adata_rna.
    latent_key : str, default: "X_scVI"
        Key to store the latent representation in .obsm.
    n_hidden : Optional[int]
        Number of hidden units per layer. Defaults to an automatic choice.
    n_latent : Optional[int]
        Dimensionality of the latent space. Defaults to an automatic choice.
    n_layers : Optional[int]
        Number of hidden layers. Defaults to an automatic choice.
    dropout_rate : Optional[float]
        Dropout rate. Defaults to 0.1.
    max_epochs : Optional[int]
        Maximum number of training epochs. Defaults to an automatic choice.
    save_model_path : Optional[str]
        Directory to save the trained model. If None, the model is not saved.
    variance_threshold : float, default: 0.9
        Fraction of variance that PCA must explain to define dataset complexity.
    n_comps : int, default: 50
        Maximum number of PCA components to compute for complexity estimation.
    **kwargs
        Additional keyword arguments passed to the model constructor.

    Returns
    -------
    Union[AnnData, Tuple[AnnData, AnnData]]:
        If only RNA is provided, returns the updated adata_rna.
        If ATAC is provided, returns a tuple (adata_rna, adata_atac)
        with the latent representation added.
    """
    n_obs = adata_rna.n_obs
    # Compute a simple complexity measure: #PCs needed to reach variance_threshold
    complexity = compute_pca_complexity(
        adata_rna, variance_threshold=variance_threshold, n_comps=n_comps
    )

    # Set defaults if parameters are not provided.
    if n_hidden is None:
        n_hidden = default_n_hidden(n_obs, complexity)
    if n_latent is None:
        n_latent = default_n_latent(n_obs, complexity)
    if n_layers is None:
        n_layers = default_n_layers(n_obs, complexity)
    if dropout_rate is None:
        dropout_rate = 0.1
    if max_epochs is None:
        max_epochs = default_epochs(n_obs, complexity)

    # Print out chosen hyperparameters
    print("Chosen Hyperparameters:")
    print(f"  - Number of hidden units per layer: {n_hidden}")
    print(f"  - Latent space dimensionality: {n_latent}")
    print(f"  - Number of layers: {n_layers}")
    print(f"  - Dropout rate: {dropout_rate}")
    print(f"  - Maximum training epochs: {max_epochs}")

    # ------------------------ RNA only: SCVI ------------------------
    if adata_atac is None:
        # 1) Set up Anndata specifically for SCVI
        SCVI.setup_anndata(adata_rna)

        # 2) Create and train the SCVI model
        model = SCVI(
            adata=adata_rna,
            n_hidden=n_hidden,
            n_layers=n_layers,
            n_latent=n_latent,
            dropout_rate=dropout_rate,
            **kwargs,
        )
        model.train(max_epochs=max_epochs)

        # 3) Store latent representation
        latent = model.get_latent_representation()
        adata_rna.obsm[latent_key] = latent

        # 4) Save model if path provided
        if save_model_path is not None:
            model.save(save_model_path, overwrite=True)

        return adata_rna

    # --------------------- RNA + ATAC: MULTIVI ----------------------
    else:
        # Ensure consistent cell order
        if not (adata_rna.obs_names == adata_atac.obs_names).all():
            raise ValueError(
                "RNA and ATAC AnnData objects must have the same obs_names in the same order."
            )

        # 1) Create a joint object by copying RNA and storing ATAC in obsm
        adata_joint = adata_rna.copy()
        adata_joint.obsm["X_atac"] = adata_atac.X

        # 2) Set up Anndata specifically for MULTIVI
        MULTIVI.setup_anndata(adata_joint)

        # 3) Create and train the MULTIVI model
        model = MULTIVI(
            adata_joint,
            n_hidden=n_hidden,
            n_layers=n_layers,
            n_latent=n_latent,
            dropout_rate=dropout_rate,
            **kwargs,
        )
        model.train(max_epochs=max_epochs)

        # 4) Store latent representation in both objects
        latent = model.get_latent_representation()
        adata_rna.obsm[latent_key] = latent
        adata_atac.obsm[latent_key] = latent

        # 5) Save model if path provided
        if save_model_path is not None:
            model.save(save_model_path, overwrite=True)

        return adata_rna, adata_atac


@beartype
def compute_metacells(
    adata_rna: "AnnData",
    adata_atac: Optional["AnnData"] = None,
    latent_key: str = "X_scVI",
    invariant_keys: List[str] = [],
    merge_categorical_keys: List[str] = [],
    numerical_keys: List[str] = [],
    n_neighbors: int = 10,
    resolution: int = 50,
    verbose: bool = True,
    merge_umap: bool = True,
    umap_key: Optional[str] = None,
) -> Union["AnnData", Tuple["AnnData", "AnnData"]]:
    """
    Computes metacells by clustering cells in a latent space and merging counts and metadata.
    If ATAC data is provided, both RNA and ATAC metacells are computed and returned.
    Otherwise, only RNA metacells are computed.

    All .var and .uns fields are copied from the original objects.

    Args:
        adata_rna (AnnData): AnnData object with RNA counts.
        adata_atac (Optional[AnnData]): AnnData object with ATAC counts (optional).
        latent_key (str): Name of latent space key in .obsm of adata_rna.
        invariant_keys (List[str], optional): List of categorical keys in adata_rna.obs that must be homogeneous
            within a metacell.
        merge_categorical_keys (List[str], optional): List of categorical keys in adata_rna.obs that can be merged.
        numerical_keys (List[str], optional): List of numerical keys in adata_rna.obs to be averaged in each metacell.
        n_neighbors (int, optional): Number of nearest neighbors for the cell–cell graph.
        resolution (int, optional): Resolution parameter for Leiden clustering.
        verbose (bool, optional): Whether to print progress and diagnostic plots.
        merge_umap (bool, optional): Whether to merge UMAP coordinates for metacells.
        umap_key (Optional[str], optional): Key for UMAP embedding in adata_rna.obsm.

    Returns:
        Union[AnnData, Tuple[AnnData, AnnData]]:
            - If adata_atac is None: returns the merged RNA AnnData object.
            - Otherwise: returns a tuple (rna_metacells, atac_metacells).
    """

    # Ensure RNA data is in sparse format and add total counts.
    if not isinstance(adata_rna.X, csr_matrix):
        adata_rna.X = csr_matrix(adata_rna.X)
    adata_rna.obs["RNA counts"] = np.array(adata_rna.X.sum(axis=1)).ravel()

    # Process ATAC data if provided.
    if adata_atac is not None:
        if len(adata_rna.obs_names) != len(adata_atac.obs_names):
            raise ValueError("RNA and ATAC data do not have the same number of cells.")
        if not (adata_rna.obs_names == adata_atac.obs_names).all():
            raise ValueError(
                "RNA and ATAC data do not contain the same cells in obs_names."
            )
        if not isinstance(adata_atac.X, csr_matrix):
            adata_atac.X = csr_matrix(adata_atac.X)
        adata_atac = adata_atac[adata_rna.obs_names, :]
        adata_atac.obs["ATAC counts"] = np.array(adata_atac.X.sum(axis=1)).ravel()

    # --- CLUSTERING STEP on RNA ---
    if verbose:
        print("Computing neighbors and running Leiden clustering on RNA data...")
    sc.pp.neighbors(adata_rna, use_rep=latent_key, n_neighbors=n_neighbors)
    sc.tl.leiden(adata_rna, key_added="leiden", resolution=resolution)

    # Define metacell labels.
    if invariant_keys:
        combined = adata_rna.obs[invariant_keys].astype(str).agg("_".join, axis=1)
        adata_rna.obs["metacell"] = adata_rna.obs["leiden"].astype(str) + "_" + combined
    else:
        adata_rna.obs["metacell"] = adata_rna.obs["leiden"]

    if adata_atac is not None:
        adata_atac.obs["metacell"] = adata_rna.obs["metacell"]
    cluster_key = "metacell"

    if verbose:
        counts = adata_rna.obs[cluster_key].value_counts()
        print("Total number of cells:", adata_rna.n_obs)
        print("Total number of metacells:", len(counts))
        print(
            "Cells per metacell -- min: {}, mean: {:.1f}, max: {}".format(
                counts.min(), counts.mean(), counts.max()
            )
        )
        plt.hist(counts, bins=10)
        plt.xlabel("Cells per metacell")
        plt.ylabel("Number of metacells")
        plt.show()

    # --- MERGE FUNCTIONS ---
    @beartype
    def merge_RNA(
        adata_rna: "AnnData",
        cluster_key: str,
        invariant_keys: List[str],
        merge_categorical_keys: List[str],
        numerical_keys: List[str],
        verbose: bool = True,
    ) -> "AnnData":
        if verbose:
            print("Merging RNA counts...")
        clusters = np.unique(adata_rna.obs[cluster_key])
        merged_X_list = []
        n_cells_list = []
        merged_annots = {
            key: []
            for key in (invariant_keys + merge_categorical_keys + numerical_keys)
        }

        for c in clusters:
            idx = adata_rna.obs[cluster_key] == c
            X_sum = np.array(adata_rna.X[idx, :].sum(axis=0)).ravel()
            merged_X_list.append(X_sum)
            n_cells = int(idx.sum())
            n_cells_list.append(n_cells)

            for key in invariant_keys:
                unique_vals = adata_rna.obs.loc[idx, key].unique()
                if len(unique_vals) != 1:
                    raise ValueError(
                        f"Metacell {c} is not homogeneous for invariant key '{key}'. Found: {unique_vals}"
                    )
                merged_annots[key].append(unique_vals[0])
            for key in merge_categorical_keys:
                mode_val = adata_rna.obs.loc[idx, key].mode()[0]
                merged_annots[key].append(mode_val)
            for key in numerical_keys:
                avg_val = adata_rna.obs.loc[idx, key].mean()
                merged_annots[key].append(avg_val)

        merged_X = np.vstack(merged_X_list)
        adata_meta = sc.AnnData(X=merged_X)
        adata_meta.var = adata_rna.var.copy()
        # Copy the unstructured data
        adata_meta.uns = adata_rna.uns.copy() if hasattr(adata_rna, "uns") else {}

        meta_obs = pd.DataFrame(index=clusters)
        meta_obs["n_cells"] = n_cells_list
        for key in invariant_keys + merge_categorical_keys + numerical_keys:
            meta_obs[key] = merged_annots[key]
        meta_obs["RNA counts"] = merged_X.sum(axis=1)
        adata_meta.obs = meta_obs

        # Merge additional layers if present.
        for layer in ["unspliced", "spliced"]:
            if layer in adata_rna.layers:
                layer_list = []
                for c in clusters:
                    idx = adata_rna.obs[cluster_key] == c
                    layer_sum = np.array(
                        adata_rna.layers[layer][idx, :].sum(axis=0)
                    ).ravel()
                    layer_list.append(layer_sum)
                merged_layer = np.vstack(layer_list)
                adata_meta.layers[layer] = csr_matrix(merged_layer, dtype=np.uint16)

        if verbose:
            print(
                "Mean RNA counts per cell before:", np.mean(adata_rna.obs["RNA counts"])
            )
            print(
                "Mean RNA counts per metacell after:",
                np.mean(adata_meta.obs["RNA counts"]),
            )
            plt.hist(
                adata_rna.obs["RNA counts"], bins=10, label="Single cells", alpha=0.5
            )
            plt.hist(
                adata_meta.obs["RNA counts"], bins=20, label="Metacells", alpha=0.5
            )
            plt.xlabel("Total RNA Counts")
            plt.ylabel("Frequency")
            plt.legend()
            plt.show()
        return adata_meta

    @beartype
    def merge_UMAP(
        adata_rna: "AnnData",
        adata_meta: "AnnData",
        cluster_key: str,
        umap_key: str = "X_umap",
        verbose: bool = True,
    ) -> "AnnData":
        if verbose:
            print("Merging UMAP coordinates...")
        clusters = np.unique(adata_rna.obs[cluster_key])
        umap_list = []
        for c in clusters:
            idx = adata_rna.obs[cluster_key] == c
            coord = np.mean(adata_rna.obsm[umap_key][idx, :], axis=0)
            umap_list.append(coord)
        adata_meta.obsm[umap_key] = np.vstack(umap_list)
        return adata_meta

    @beartype
    def merge_ATAC(
        adata_atac: "AnnData",
        cluster_key: str,
        invariant_keys: List[str],
        merge_categorical_keys: List[str],
        numerical_keys: List[str],
        verbose: bool = True,
    ) -> "AnnData":
        if verbose:
            print("Merging ATAC counts...")
        clusters = np.unique(adata_atac.obs[cluster_key])
        merged_X_list = []
        n_cells_list = []
        merged_annots = {
            key: []
            for key in (invariant_keys + merge_categorical_keys + numerical_keys)
        }

        for c in clusters:
            idx = adata_atac.obs[cluster_key] == c
            X_sum = np.array(adata_atac.X[idx, :].sum(axis=0)).ravel()
            merged_X_list.append(X_sum)
            n_cells = int(idx.sum())
            n_cells_list.append(n_cells)
            for key in invariant_keys:
                unique_vals = adata_atac.obs.loc[idx, key].unique()
                if len(unique_vals) != 1:
                    raise ValueError(
                        f"Metacell {c} is not homogeneous for invariant key '{key}'. Found: {unique_vals}"
                    )
                merged_annots[key].append(unique_vals[0])
            for key in merge_categorical_keys:
                mode_val = adata_atac.obs.loc[idx, key].mode()[0]
                merged_annots[key].append(mode_val)
            for key in numerical_keys:
                avg_val = adata_atac.obs.loc[idx, key].mean()
                merged_annots[key].append(avg_val)

        merged_X = np.vstack(merged_X_list)
        adata_meta = sc.AnnData(X=merged_X)
        adata_meta.var = adata_atac.var.copy()
        # Copy over unstructured data
        adata_meta.uns = adata_atac.uns.copy() if hasattr(adata_atac, "uns") else {}

        meta_obs = pd.DataFrame(index=clusters)
        meta_obs["n_cells"] = n_cells_list
        for key in invariant_keys + merge_categorical_keys + numerical_keys:
            meta_obs[key] = merged_annots[key]
        meta_obs["ATAC counts"] = merged_X.sum(axis=1)
        adata_meta.obs = meta_obs

        if verbose:
            print(
                "Mean ATAC counts per cell before:",
                np.mean(adata_atac.obs["ATAC counts"]),
            )
            print(
                "Mean ATAC counts per metacell after:",
                np.mean(adata_meta.obs["ATAC counts"]),
            )
            plt.hist(
                adata_atac.obs["ATAC counts"], bins=10, label="Single cells", alpha=0.5
            )
            plt.hist(
                adata_meta.obs["ATAC counts"], bins=20, label="Metacells", alpha=0.5
            )
            plt.xlabel("Total ATAC Counts")
            plt.ylabel("Frequency")
            plt.legend()
            plt.show()
        return adata_meta

    # --- MERGE RNA METACELLS ---
    adata_meta_rna = merge_RNA(
        adata_rna,
        cluster_key=cluster_key,
        invariant_keys=invariant_keys,
        merge_categorical_keys=merge_categorical_keys,
        numerical_keys=numerical_keys,
        verbose=verbose,
    )

    if merge_umap:
        if not umap_key or umap_key not in adata_rna.obsm:
            if verbose:
                warnings.warn(
                    "UMAP embedding not found; computing with sc.tl.umap()...",
                    UserWarning,
                )
            sc.tl.umap(adata_rna)
            umap_key = "X_umap"
        adata_meta_rna = merge_UMAP(
            adata_rna,
            adata_meta_rna,
            cluster_key=cluster_key,
            umap_key=umap_key,
            verbose=verbose,
        )

    # --- MERGE ATAC METACELLS if provided ---
    if adata_atac is not None:
        adata_meta_atac = merge_ATAC(
            adata_atac,
            cluster_key=cluster_key,
            invariant_keys=invariant_keys,
            merge_categorical_keys=merge_categorical_keys,
            numerical_keys=numerical_keys,
            verbose=verbose,
        )
        # Optionally copy ATAC counts into the RNA metacell object.
        adata_meta_rna.obs["ATAC counts"] = adata_meta_atac.obs["ATAC counts"]
        if verbose:
            print("Metacell construction complete for both RNA and ATAC data.")
        return adata_meta_rna, adata_meta_atac
    else:
        if verbose:
            print("Metacell construction complete for RNA data only.")
        return adata_meta_rna


@beartype
def convert_to_dense(layer):
    """
    Convert a sparse matrix to a dense numpy array.

    Args:
        layer: Input array or sparse matrix.

    Returns:
        Dense numpy array.
    """
    if sp.issparse(layer):
        return layer.toarray()
    else:
        return layer


@beartype
def filter_genes(
    adata_rna: AnnData,
    tf_list: List[str],
    n_top_genes: int = 1000,
    count_threshold: Optional[int] = None,
) -> AnnData:
    """
    Filters genes in the AnnData object by selecting the most variable genes
    and optionally including transcription factors (TFs) above a count threshold.

    Parameters:
    - adata_rna: AnnData object containing gene expression data.
    - tf_list: List of transcription factors to consider.
    - n_top_genes: Number of most variable genes to retain (default: 1000).
    - count_threshold: Optionally add all TFs above this total count threshold. If set to None,
      no additional TFs are added.

    Returns:
    - Filtered AnnData object.
    """
    # Step 1: Filter to the most variable genes
    sc.pp.highly_variable_genes(adata_rna, n_top_genes=n_top_genes)
    highly_variable_genes = set(adata_rna.var[adata_rna.var["highly_variable"]].index)

    # Step 2: Optionally filter TFs based on total counts
    if count_threshold is not None:
        tf_in_adata = [tf for tf in tf_list if tf in adata_rna.var_names]
        tf_with_counts = [
            tf
            for tf in tf_in_adata
            if np.sum(
                adata_rna[:, tf].layers["spliced"]
                + adata_rna[:, tf].layers["unspliced"]
            )
            >= count_threshold
        ]
        highly_variable_genes = highly_variable_genes.union(tf_with_counts)

    # Step 3: Subset the AnnData object
    final_genes = list(set(highly_variable_genes) & set(adata_rna.var_names))
    return adata_rna[:, final_genes]


@beartype
def filter_regions(
    adata_atac: AnnData,
    min_cells: int = 5,
    target_sum: Union[int, float] = 1e4,
    n_top_regions: int = 10**6,
) -> AnnData:
    """
    Filter an ATAC-seq AnnData object to retain the most important regions through a
    series of preprocessing steps. The procedure includes filtering regions by the
    minimum number of cells in which they are detected, normalizing and log-transforming
    the data to compute variability, and finally subsetting to the top variable regions.

    Parameters
    ----------
    adata_atac : AnnData
        An AnnData object containing ATAC-seq peak count data.
    min_cells : int, optional
        Minimum number of cells in which a region must be detected to be retained.
    target_sum : int or float, optional
        The target total count for normalization per cell.
    n_top_regions : int, optional
        The number of top variable regions to select. Setting this to a high value (e.g., 10**6)
        will effectively retain all regions after filtering.

    Returns
    -------
    AnnData
        The filtered AnnData object containing only the selected regions.

    Example
    -------
    >>> filtered_atac = filter_peaks(adata_atac, min_cells=5, target_sum=1e4, n_top_regions=10**6)
    >>> print(filtered_atac.shape)
    """

    # Step 1: Filter peaks that are detected in at least `min_cells` cells.
    sc.pp.filter_genes(adata_atac, min_cells=min_cells)

    # Step 2: Save the raw counts.
    adata_atac.layers["raw_counts"] = adata_atac.X.copy()

    # Step 3: Normalize total counts per cell.
    sc.pp.normalize_total(adata_atac, target_sum=target_sum)

    # Step 4: Log-transform the data.
    sc.pp.log1p(adata_atac)

    # Step 5: Identify highly variable peaks and subset the AnnData object.
    sc.pp.highly_variable_genes(adata_atac, n_top_genes=n_top_regions, subset=True)

    # Step 6: Restore the original raw counts and remove the temporary layer.
    adata_atac.X = adata_atac.layers["raw_counts"]
    del adata_atac.layers["raw_counts"]

    return adata_atac


@beartype
def filter_motif_scores(
    motif_scores: pd.DataFrame,
    adata_rna: AnnData,
    adata_atac: AnnData,
    rna_col: str,
    atac_col: str,
) -> pd.DataFrame:
    """
    Filter the motif_scores DataFrame based on the variable names in the provided AnnData objects.

    The function performs two filtering steps:
      1. Keeps only those rows in `motif_scores` where the value in the column specified by
         `rna_col` exists in `adata_rna.var_names`.
      2. From the resulting DataFrame, keeps only those rows where the value in the column
         specified by `atac_col` exists in `adata_atac.var_names`.

    Parameters
    ----------
    motif_scores : pd.DataFrame
        DataFrame containing motif scores. Must include at least the columns defined by `rna_col`
        and `atac_col`.
    adata_rna : AnnData
        An AnnData object containing RNA data. Its `var_names` are used to filter the column
        specified by `rna_col` in `motif_scores`.
    adata_atac : AnnData
        An AnnData object containing ATAC data. Its `var_names` are used to filter the column
        specified by `atac_col` in `motif_scores`.
    rna_col : str
        The column name in `motif_scores` corresponding to RNA gene names.
    atac_col : str
        The column name in `motif_scores` corresponding to ATAC peak identifiers.

    Returns
    -------
    pd.DataFrame
        The filtered motif_scores DataFrame containing only rows where:
          - The value in `rna_col` is present in `adata_rna.var_names`, and
          - The value in `atac_col` is present in `adata_atac.var_names`.

    Example
    -------
    >>> filtered_scores = filter_motif_scores(motif_scores, adata_rna, adata_atac)
    >>> print(filtered_scores.shape)
    """
    # Filter based on RNA variable names.
    subset_rna = [g in adata_rna.var_names for g in motif_scores[rna_col]]
    filtered_scores = motif_scores.loc[subset_rna, :]

    # Filter based on ATAC variable names.
    subset_atac = [m in adata_atac.var_names for m in filtered_scores[atac_col]]
    filtered_scores = filtered_scores.loc[subset_atac, :]

    return filtered_scores


def extract_region_tf_pairs(
    dataframe, adata_atac, adata_rna, region_col="0", tf_col="mouse_gene_name"
):
    """
    Extract non-zero region-TF pairs.

    Args:
        dataframe: A pandas DataFrame containing region-TF metadata.
        adata_atac: AnnData object for ATAC data (regions/peaks).
        adata_rna: AnnData object for RNA data (genes/TFs).
        region_col: Column name for region (peak) identifiers in the DataFrame.
        tf_col: Column name for TF (gene) names in the DataFrame.

    Returns:
        region_tf_pairs: A JAX numpy array of region-TF pairs.
    """
    # Collect region-TF pairs as tuples
    region_tf_pairs = []
    for _, row in dataframe.iterrows():
        region_name = row[region_col]
        tf_name = row[tf_col]

        # Check existence in AnnData objects
        if region_name in adata_atac.var_names and tf_name in adata_rna.var_names:
            region_idx = adata_atac.var_names.get_loc(region_name)
            tf_idx = adata_rna.var_names.get_loc(tf_name)
            region_tf_pairs.append((region_idx, tf_idx))

    # Convert to jax array
    region_tf_pairs = jnp.array(region_tf_pairs, dtype=np.int32)

    return region_tf_pairs


def build_gene_tss_dict(adata_rna, dataset_name="mmusculus_gene_ensembl"):
    """
    Query Ensembl Biomart for chromosome, start, end, strand, and external_gene_name,
    then build a dictionary: gene_name -> (chrom, TSS).

    Args:
        adata_rna: an AnnData object with gene names in `adata_rna.var_names`
        dataset_name: typically "mmusculus_gene_ensembl" for mouse.

    Returns:
        gene_dict: {gene_name: (chrom, tss)}
                   where 'chrom' is a string (e.g., '1', '2', 'X')
                         'tss'   is an integer
    """
    # 1) Connect to Ensembl via pybiomart
    server = Server(host="http://www.ensembl.org")
    dataset = server.marts["ENSEMBL_MART_ENSEMBL"].datasets[dataset_name]

    # 2) Query for genes
    df = dataset.query(
        attributes=[
            "chromosome_name",  # might return 'Chromosome/scaffold name'
            "start_position",  # might return 'Gene start (bp)'
            "end_position",  # might return 'Gene end (bp)'
            "strand",  # might return 'Strand'
            "external_gene_name",  # might return 'Gene name'
        ]
    )

    rename_dict = {}
    for col in df.columns:
        c_lower = col.lower()
        if "chromosome" in c_lower:
            rename_dict[col] = "chromosome_name"
        elif "start" in c_lower:
            rename_dict[col] = "start_position"
        elif "end" in c_lower:
            rename_dict[col] = "end_position"
        elif "strand" in c_lower:
            rename_dict[col] = "strand"
        elif "gene name" in c_lower or "external_gene_name" in c_lower:
            rename_dict[col] = "external_gene_name"

    df.rename(columns=rename_dict, inplace=True)

    # 4) Convert to a dictionary: gene_name -> (chrom, tss)
    #    TSS depends on the strand
    gene_dict = {}
    rna_gene_set = set(adata_rna.var_names)

    for row in df.itertuples(index=False):
        chrom = str(row.chromosome_name)
        start = int(row.start_position)
        end = int(row.end_position)
        strand = int(row.strand)  # 1 or -1 for Ensembl
        gname = str(row.external_gene_name)

        # Skip if gene not in adata_rna
        if gname not in rna_gene_set:
            continue

        # Optional: skip weird contigs
        if not chrom.isdigit() and chrom not in ["X", "Y"]:
            continue

        # TSS depends on strand
        tss = start if strand == 1 else end

        # If multiple lines appear for the same gene, you can decide how to handle them
        if gname not in gene_dict:
            gene_dict[gname] = (chrom, tss)

    return gene_dict


def parse_region_name(region_str):
    """
    Parse region like 'chr1:1000-2000' => (chrom, start, end).
    If your naming scheme is different, adapt accordingly.
    """
    region_str = region_str.replace("chr", "")  # remove "chr" if present
    chrom, coords = region_str.split(":")
    start, end = coords.split("-")
    start, end = int(start), int(end)
    return chrom, start, end


def build_pyranges_for_regions(adata_atac):
    """
    Convert each region in adata_atac.var_names into a PyRanges object
    with columns: Chromosome, Start, End, region_idx.
    """
    rows = []
    for region_idx, region_str in enumerate(adata_atac.var_names):
        chrom, start, end = parse_region_name(region_str)
        rows.append([chrom, start, end, region_idx])
    df_regions = pd.DataFrame(
        rows, columns=["Chromosome", "Start", "End", "region_idx"]
    )
    return pr.PyRanges(df_regions)


def build_pyranges_for_genes(adata_rna, gene_dict):
    """
    For each gene in adata_rna, if it's in gene_dict, create a PyRanges interval
    at [tss, tss+1]. Columns: Chromosome, Start, End, gene_idx.
    """
    rows = []
    for gene_idx, gene_name in enumerate(adata_rna.var_names):
        if gene_name not in gene_dict:
            continue
        chrom, tss = gene_dict[gene_name]
        rows.append([chrom, tss, tss + 1, gene_idx])
    df_genes = pd.DataFrame(rows, columns=["Chromosome", "Start", "End", "gene_idx"])
    return pr.PyRanges(df_genes)


def build_region_gene_pairs(
    adata_atac,
    adata_rna,
    distance1=5_000,
    distance2=200_000,
):
    """
    Build a jax array of shape (N, 3): [region_idx, gene_idx, weight].

    Rules:
      - If distance < 5 kb => weight = 1.0
      - Else if distance < 200 kb => weight = 0
      - Otherwise, exclude the pair
      - Exclusive logic: If a region is within 5 kb of ANY gene => only keep 1.0 pairs
    """

    # 1) Build gene TSS dict (using pybiomart)
    gene_dict = build_gene_tss_dict(adata_rna)

    # 2) Convert to PyRanges
    gr_regions = build_pyranges_for_regions(adata_atac)
    gr_genes = build_pyranges_for_genes(adata_rna, gene_dict)

    # 3) Expand the gene intervals by ±distance2 => up to 200 kb
    gr_genes_expanded = gr_genes.slack(distance2)

    # 4) Join region intervals with expanded gene intervals => all pairs < 200 kb
    joined = gr_regions.join(gr_genes_expanded)
    df_joined = joined.df

    region_start_col = "Start"
    region_end_col = "End"
    gene_start_col = "Start_b"
    gene_end_col = "End_b"

    if "Start_a" in df_joined.columns:
        region_start_col = "Start_a"
        region_end_col = "End_a"
    if "Start_b" not in df_joined.columns:
        # Possibly "Start" is for genes, "Start_a" for regions
        # We'll guess the columns by checking region_idx vs gene_idx
        if "Start_a" in df_joined.columns and "gene_idx" in df_joined.columns:
            # Then "Start_a", "End_a" might be region, so "Start_b", "End_b" is gene
            # But if we don't see "Start_b", it might be "Start"
            pass
        else:
            # or handle more systematically
            pass

    # 5) Compute distances
    region_mid = (df_joined[region_start_col] + df_joined[region_end_col]) // 2
    gene_tss = (df_joined[gene_start_col] + df_joined[gene_end_col]) // 2
    distance = (region_mid - gene_tss).abs()

    # 6) Assign raw weight
    #    We'll skip rows >= distance2 (200 kb)
    valid_mask = distance < distance2
    df_valid = df_joined[valid_mask].copy()

    # Mark rows < 5 kb => 1.0
    raw_weight = np.full(len(df_valid), 0)
    mask1 = distance[valid_mask] < distance1
    raw_weight[mask1] = 1

    df_valid["weight"] = raw_weight

    # 7) Enforce the exclusive logic:
    #    If a region has any 1.0 link, discard that region's 0 links)
    out_list = []
    grouped = df_valid.groupby("region_idx", sort=False)
    for _, subdf in grouped:
        if (subdf["weight"] == 1.0).any():
            # keep only the 1.0 rows
            keep_rows = subdf[subdf["weight"] == 1.0]
        else:
            # keep 0
            keep_rows = subdf
        out_list.append(keep_rows)

    df_final = pd.concat(out_list, ignore_index=True)

    # 8) Extract columns => [region_idx, gene_idx, weight]
    out_array = df_final[["region_idx", "gene_idx", "weight"]].to_numpy(
        dtype=np.float32
    )

    # Convert to JAX array
    region_gene_pairs = jnp.array(out_array)

    return region_gene_pairs


def construct_region_tf_gene_triplets(region_tf_pairs, region_gene_pairs):
    """
    Constructs all unique (region, tf, gene) combinations based on existing pairs.

    Args:
        region_tf_pairs: JAX array of shape (num_pairs, 2) with [region_idx, tf_idx]
        region_gene_pairs: JAX array of shape (num_rg_pairs, 3) with [region_idx, gene_idx, score]

    Returns:
        region_tf_gene_triplets: JAX array of shape (P, 3) with [region_idx, tf_idx, gene_idx]
    """
    # Convert JAX arrays to NumPy arrays for preprocessing
    region_tf_pairs_np = np.array(region_tf_pairs)
    region_gene_pairs_np = np.array(region_gene_pairs)

    region_to_tfs = {}
    for pair in region_tf_pairs_np:
        region, tf = pair
        region = int(region)  # Convert to Python int
        tf = int(tf)  # Convert to Python int
        region_to_tfs.setdefault(region, []).append(tf)

    region_to_genes = {}
    for pair in region_gene_pairs_np:
        region, gene = pair[:2]  # Ignore the third column
        region = int(region)  # Convert to Python int
        gene = int(gene)  # Convert to Python int
        region_to_genes.setdefault(region, []).append(gene)

    # Now, create all (region, tf, gene) triplets where tf and gene share the same region
    region_tf_gene_triplets = []
    for region in region_to_tfs:
        tfs = region_to_tfs[region]
        genes = region_to_genes.get(region, [])
        for tf in tfs:
            for gene in genes:
                region_tf_gene_triplets.append([region, tf, gene])

    # Convert the list to a NumPy array and then to a JAX array
    region_tf_gene_triplets_np = np.array(region_tf_gene_triplets, dtype=int)
    region_tf_gene_triplets_jax = jnp.array(region_tf_gene_triplets_np)

    return region_tf_gene_triplets_jax


def precompute_region_tf_indices(
    region_tf_gene_triplets, map_region_tf_to_index, num_tfs
):
    """
    Precompute region_tf_indices for each [R, H, G] triplet in region_tf_gene_triplets.

    Args:
        region_tf_gene_triplets: numpy array of shape (num_rtg_triplets, 3) with [region_idx, tf_idx, gene_idx].
        map_region_tf_to_index: numpy array of shape (num_regions * num_tfs,) mapping [R, H] to index.
        num_tfs: Integer, total number of transcription factors.

    Returns:
        region_tf_indices: numpy array of shape (num_rtg_triplets,) mapping each triplet to index in region_tf_pairs.
    """
    # Compute flat indices for [R, H] in region_tf_gene_triplets
    flat_indices = (
        region_tf_gene_triplets[:, 0] * num_tfs + region_tf_gene_triplets[:, 1]
    )  # [num_rtg_triplets]

    # Retrieve the corresponding indices in region_tf_pairs
    region_tf_indices = map_region_tf_to_index[flat_indices]  # [num_rtg_triplets]

    return region_tf_indices


def precompute_mapping(region_tf_pairs, region_tf_gene_triplets, num_regions, num_tfs):
    """
    Precompute a mapping from [region_idx, tf_idx] to index in region_tf_pairs.

    Args:
        region_tf_pairs: numpy array of shape (num_pairs, 2) with [region_idx, tf_idx].
        region_tf_gene_triplets: numpy array of shape (num_rtg_triplets, 3) with [region_idx, tf_idx, gene_idx].
        num_regions: Integer, total number of regions.
        num_tfs: Integer, total number of transcription factors.

    Returns:
        map_region_tf_to_index: numpy array of shape (num_regions * num_tfs,) mapping [R, H] to index.
    """
    # Initialize the mapping array with -1 (indicating unmapped)
    map_region_tf_to_index = np.full(num_regions * num_tfs, -1, dtype=int)

    # Populate the mapping array
    for idx, (R, H) in enumerate(region_tf_pairs):
        flat_index = R * num_tfs + H
        map_region_tf_to_index[flat_index] = idx

    # Verify that all [R, H] in region_tf_gene_triplets are present in region_tf_pairs
    region_tf_gene_flat_indices = (
        region_tf_gene_triplets[:, 0] * num_tfs + region_tf_gene_triplets[:, 1]
    )
    missing = map_region_tf_to_index[region_tf_gene_flat_indices] == -1
    if np.any(missing):
        missing_count = np.sum(missing)
        raise ValueError(
            f"{missing_count} [region_idx, tf_idx] pairs in region_tf_gene_triplets are missing in region_tf_pairs."
        )

    return jnp.array(map_region_tf_to_index)
