from importlib import metadata

from . import models
from .main import main
from .plotting import (
    plot_elbo_loss,
    posterior_data_geneset,
    predictions_vs_data,
    prior_data_geneset,
)
from .posterior import extract_posterior_estimates
from .preprocessing import (
    build_gene_tss_dict,
    build_pyranges_for_genes,
    build_pyranges_for_regions,
    build_region_gene_pairs,
    compute_metacells,
    construct_region_tf_gene_triplets,
    convert_to_dense,
    extract_region_tf_pairs,
    filter_genes,
    filter_motif_scores,
    filter_regions,
    parse_region_name,
    precompute_mapping,
    precompute_region_tf_indices,
    run_scvi,
)
from .train import train_svi

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = "unknown"

del metadata


__all__ = [
    "train_svi",
    "extract_posterior_estimates",
    "plot_elbo_loss",
    "convert_to_dense",
    "filter_regions",
    "filter_motif_scores",
    "extract_region_tf_pairs",
    "build_gene_tss_dict",
    "parse_region_name",
    "build_pyranges_for_regions",
    "build_pyranges_for_genes",
    "build_region_gene_pairs",
    "construct_region_tf_gene_triplets",
    "precompute_region_tf_indices",
    "precompute_mapping",
    "compute_metacells",
    "filter_genes",
    "models",
    "guides",
    "run_scvi",
    "prior_data_geneset",
    "predictions_vs_data",
    "posterior_data_geneset",
    "main",
]
