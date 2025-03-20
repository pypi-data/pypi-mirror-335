# models

- RNA_1layer_simple - the simplest implementation of dynamical transcription + measurment model, using a 1 layer neural net to link spliced counts to the transcription rate
- RNA_1layer - a more complex model including latent protein levels, NB instead of Poisson distribution for the likelihood etc. , but still just a 1 layer NN to for the transcription rate
- RNA_1layer_constantDiffusion - base stochastic model consisting of RNA_1layer model with a constant diffusion term added.
- RNA_1layer_constantDiffusion_LogNormal - extension to base stochastic model that replaces gamma distributions with LogNormal and other minor adjustments for numerical stability
- RNA_3layer - deprecated model with a 3 layer neural net for the transcription rate
- ATAC_RNA - base model for joint ATAC+RNA data, using a mechanistic model of TF binding to DNA regions (using prior knowledge about motifs and genomic distances) to link latent protein levels to the transcription rate.