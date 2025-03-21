"""Likelihood factory function for cluster number counts."""

import os

import pyccl as ccl
import sacc

from firecrown.likelihood.gaussian import ConstGaussian
from firecrown.likelihood.binned_cluster_number_counts import (
    BinnedClusterNumberCounts,
)
from firecrown.likelihood.likelihood import Likelihood, NamedParameters
from firecrown.modeling_tools import ModelingTools
from firecrown.models.cluster.abundance import ClusterAbundance
from firecrown.models.cluster.properties import ClusterProperty
from firecrown.models.cluster.recipes.murata_binned_spec_z import (
    MurataBinnedSpecZRecipe,
)


def get_cluster_abundance() -> ClusterAbundance:
    """Creates and returns a ClusterAbundance object."""
    hmf = ccl.halos.MassFuncBocquet16()
    min_mass, max_mass = 13.0, 16.0
    min_z, max_z = 0.2, 0.8
    cluster_abundance = ClusterAbundance(min_mass, max_mass, min_z, max_z, hmf)

    return cluster_abundance


def build_likelihood(
    build_parameters: NamedParameters,
) -> tuple[Likelihood, ModelingTools]:
    """Builds the likelihood for Firecrown."""
    # Pull params for the likelihood from build_parameters
    average_on = ClusterProperty.NONE
    if build_parameters.get_bool("use_cluster_counts", True):
        average_on |= ClusterProperty.COUNTS
    if build_parameters.get_bool("use_mean_log_mass", False):
        average_on |= ClusterProperty.MASS

    survey_name = "numcosmo_simulated_redshift_richness"
    likelihood = ConstGaussian(
        [BinnedClusterNumberCounts(average_on, survey_name, MurataBinnedSpecZRecipe())]
    )

    # Read in sacc data
    sacc_path = "file.sacc"
    sacc_data = sacc.Sacc.load_fits(sacc_path) 
    likelihood.read(sacc_data)

    cluster_abundance = get_cluster_abundance()
    modeling_tools = ModelingTools(cluster_abundance=cluster_abundance)

    return likelihood, modeling_tools
