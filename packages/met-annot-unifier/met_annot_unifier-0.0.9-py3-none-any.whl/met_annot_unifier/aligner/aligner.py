from functools import reduce
from typing import Optional

import pandas as pd

from met_annot_unifier.aligner.parser import (
    extract_feature_id,
    prefix_columns,
    process_gnps_data,
    process_isdb_data,
    process_sirius_data,
    standardize_column_names,
)
from met_annot_unifier.aligner.utils import (
    count_sources,
    process_IK2D_sources,
    process_npc_class_sources,
    process_npc_pathway_sources,
    process_npc_superclass_sources,
)
from met_annot_unifier.exceptions import DataFileError


def align_data_vertically(
    gnps_file: Optional[str] = None,
    isdb_file: Optional[str] = None,
    sirius_file: Optional[str] = None,
) -> pd.DataFrame:
    """
    Aligns and merges data from GNPS, Sirius, and ISDB datasets optionally. Files can be provided for any subset of these datasets.
    The function standardizes column names, prefixes them to indicate their source, merges the data based on 'feature_id'
    and 'IK2D', and then creates consolidated 'Sources' and 'SMILES' columns.

    Args:
        gnps_file (str, optional): File path for the GNPS data in TSV format.
        sirius_file (str, optional): File path for the Sirius data in TSV format.
        isdb_file (str, optional): File path for the ISDB data in TSV format.

    Returns:
        pd.DataFrame: A DataFrame with aligned and merged data from the provided sources.

    Example:
        >>> gnps_file = 'path/to/gnps_data.tsv'
        >>> sirius_file = 'path/to/sirius_data.tsv'
        >>> aligned_data = align_data_vertically(gnps_file=gnps_file, sirius_file=sirius_file)
        >>> print(aligned_data.columns)
        Index(['feature_id', 'IK2D', 'Sources', 'SMILES', ...], dtype='object')
    """

    data_frames = []

    if gnps_file:
        gnps_data = process_gnps_data(gnps_file)
        data_frames.append(gnps_data)

    if isdb_file:
        isdb_data = process_isdb_data(isdb_file)
        data_frames.append(isdb_data)

    if sirius_file:
        sirius_data = process_sirius_data(sirius_file)
        data_frames.append(sirius_data)

    # Ensure that at least one data frame has been loaded
    if not data_frames:
        raise DataFileError()

    # Concatenate all available data frames
    combined_data = pd.concat([df for df in data_frames if not df.empty], axis=0, ignore_index=True)
    # Group by 'feature_id' and 'IK2D' and combine the annotations
    merged_data = combined_data.groupby(["feature_id", "IK2D"], as_index=False).agg(
        lambda x: ", ".join(x.dropna().astype(str).unique())
    )

    # Create the 'Sources' column
    source_columns = [col for col in merged_data.columns if col.endswith("annotation_source")]
    merged_data["Sources"] = merged_data.apply(
        lambda row: "|".join(sorted(filter(None, [row.get(col) for col in source_columns]))), axis=1
    )
    merged_data.drop(columns=source_columns, inplace=True)

    # Handle the SMILES column
    # Specify the priority order for SMILES columns explicitly
    smiles_columns = [
        "sirius_SMILES",  # Highest priority
        "isdb_SMILES",
        "gnps_SMILES",  # Lowest priority
    ]

    # Check and keep only those columns that actually exist in the merged data
    smiles_columns = [col for col in smiles_columns if col in merged_data.columns]
    merged_data["SMILES"] = merged_data.apply(
        lambda row: next((row[col] for col in smiles_columns if row[col]), None), axis=1
    )

    # Select and reorder columns
    selected_columns = ["feature_id", "IK2D", "Sources", "SMILES"]
    merged_data = merged_data[selected_columns + [col for col in merged_data.columns if col not in selected_columns]]

    return merged_data


# met-annot-unifier-cli align-horizontally --canopus-file /Users/pma/Dropbox/git_repos/COMMONS_Lab/SBL.20004.2024/docs/mapp_project_00050/mapp_batch_00109/results/sirius/canopus_compound_summary.tsv --gnps-file /Users/pma/Dropbox/git_repos/COMMONS_Lab/SBL.20004.2024/docs/mapp_project_00050/mapp_batch_00109/results/met_annot_enhancer/686365fe75624ed8be661d43be058592/nf_output/library/merged_results_with_gnps.tsv --gnps-mn-file /Users/pma/Dropbox/git_repos/COMMONS_Lab/SBL.20004.2024/docs/mapp_project_00050/mapp_batch_00109/results/met_annot_enhancer/686365fe75624ed8be661d43be058592/nf_output/networking/clustersummary_with_network.tsv --sirius-file /Users/pma/Dropbox/git_repos/COMMONS_Lab/SBL.20004.2024/docs/mapp_project_00050/mapp_batch_00109/results/sirius/compound_identifications.tsv --isdb-file /Users/pma/Dropbox/git_repos/COMMONS_Lab/SBL.20004.2024/docs/mapp_project_00050/mapp_batch_00109/results/met_annot_enhancer/mapp_batch_00109/mapp_batch_00109_spectral_match_results_repond_flat.tsv --output /Users/pma/Dropbox/git_repos/COMMONS_Lab/SBL.20004.2024/docs/mapp_project_00050/mapp_batch_00109/results/tmp/mapp_batch_00109_met_annot_unified_new.tsv

canopus_file = "/Users/pma/git_repos/mapp-metabolomics-unit/thomas-auer-group/docs/mapp_project_00055/mapp_batch_00154/results/sirius/canopus_structure_summary.tsv"
gnps_file = "/Users/pma/git_repos/mapp-metabolomics-unit/thomas-auer-group/docs/mapp_project_00055/mapp_batch_00154/results/met_annot_enhancer/b947d7e448bf4954b6cb0eef4076fe8c/nf_output/library/merged_results_with_gnps.tsv"
gnps_mn_file = "/Users/pma/git_repos/mapp-metabolomics-unit/thomas-auer-group/docs/mapp_project_00055/mapp_batch_00154/results/met_annot_enhancer/b947d7e448bf4954b6cb0eef4076fe8c/nf_output/networking/clustersummary_with_network.tsv"
sirius_file = "/Users/pma/git_repos/mapp-metabolomics-unit/thomas-auer-group/docs/mapp_project_00055/mapp_batch_00154/results/sirius/structure_identifications.tsv"
isdb_file = "/Users/pma/git_repos/mapp-metabolomics-unit/thomas-auer-group/docs/mapp_project_00055/mapp_batch_00154/results/met_annot_enhancer/mapp_batch_00154/mapp_batch_00154_spectral_match_results_repond_flat.tsv"


def align_data_horizontally(
    canopus_file: Optional[str] = None,
    gnps_file: Optional[str] = None,
    gnps_mn_file: Optional[str] = None,
    isdb_file: Optional[str] = None,
    sirius_file: Optional[str] = None,
) -> pd.DataFrame:
    """
    Aligns and merges data from GNPS, Sirius, ISDB  and CANOPUS datasets, if provided. This function merges the data horizontally,
    keeping the data in a wide format. The function standardizes column names, prefixes them to indicate their source,
    and merges the data based on 'feature_id'.

    Args:
    canopus_file (Optional[str]): File path for the CANOPUS data in TSV format.
    gnps_file (Optional[str]): File path for the GNPS data in TSV format.
    isdb_file (Optional[str]): File path for the ISDB data in TSV format.
    sirius_file (Optional[str]): File path for the Sirius data in TSV format.

    Returns:
    pd.DataFrame: A DataFrame with aligned and merged data from the provided sources.
    """

    data_frames = []

    if canopus_file:
        canopus_data = pd.read_csv(canopus_file, sep="\t")
        canopus_data = standardize_column_names(canopus_data, "mappingFeatureId", "feature_id")
        canopus_data = prefix_columns(canopus_data, "canopus_", exclude_columns=[])
        # the CANOPUS NPC classifier columns names are standardized
        canopus_data = standardize_column_names(canopus_data, "canopus_NPC#pathway", "canopus_npc_pathway")
        canopus_data = standardize_column_names(canopus_data, "canopus_NPC#superclass", "canopus_npc_superclass")
        canopus_data = standardize_column_names(canopus_data, "canopus_NPC#class", "canopus_npc_class")
        canopus_data = extract_feature_id(canopus_data, "canopus_feature_id")
        canopus_data = standardize_column_names(canopus_data, "canopus_feature_id", "feature_id")
        data_frames.append(canopus_data)

    if gnps_file:
        gnps_data = pd.read_csv(gnps_file, sep="\t")
        gnps_data = standardize_column_names(gnps_data, "InChIKey-Planar", "IK2D")
        gnps_data = standardize_column_names(gnps_data, "#Scan#", "feature_id")
        gnps_data = standardize_column_names(gnps_data, "Smiles", "SMILES")
        gnps_data = prefix_columns(gnps_data, "gnps_", exclude_columns=[])
        # the GNPS NPC classifier columns names are standardized
        gnps_data = standardize_column_names(gnps_data, "gnps_npclassifier_pathway", "gnps_npc_pathway")
        gnps_data = standardize_column_names(gnps_data, "gnps_npclassifier_superclass", "gnps_npc_superclass")
        gnps_data = standardize_column_names(gnps_data, "gnps_npclassifier_class", "gnps_npc_class")
        gnps_data = standardize_column_names(gnps_data, "gnps_feature_id", "feature_id")
        data_frames.append(gnps_data)

    if isdb_file:
        isdb_data = pd.read_csv(isdb_file, sep="\t")
        isdb_data = standardize_column_names(isdb_data, "short_inchikey", "IK2D")
        isdb_data = standardize_column_names(isdb_data, "feature_id", "feature_id")
        isdb_data = standardize_column_names(isdb_data, "structure_smiles", "SMILES")
        isdb_data = prefix_columns(isdb_data, "isdb_", exclude_columns=[])
        # the ISDB NPC classifier columns names are standardized
        isdb_data = standardize_column_names(
            isdb_data, "isdb_structure_taxonomy_npclassifier_01pathway", "isdb_npc_pathway"
        )
        isdb_data = standardize_column_names(
            isdb_data, "isdb_structure_taxonomy_npclassifier_02superclass", "isdb_npc_superclass"
        )
        isdb_data = standardize_column_names(
            isdb_data, "isdb_structure_taxonomy_npclassifier_03class", "isdb_npc_class"
        )
        isdb_data = standardize_column_names(isdb_data, "isdb_feature_id", "feature_id")
        data_frames.append(isdb_data)

    if sirius_file:
        # Read and process Sirius data
        sirius_data = pd.read_csv(sirius_file, sep="\t")
        sirius_data = standardize_column_names(sirius_data, "InChIkey2D", "IK2D")
        sirius_data = standardize_column_names(sirius_data, "mappingFeatureId", "feature_id")
        sirius_data = standardize_column_names(sirius_data, "smiles", "SMILES")
        sirius_data = prefix_columns(sirius_data, "sirius_", exclude_columns=[])
        sirius_data = extract_feature_id(sirius_data, "sirius_feature_id")
        sirius_data = standardize_column_names(sirius_data, "sirius_feature_id", "feature_id")
        data_frames.append(sirius_data)

    if not data_frames:
        raise DataFileError()

    # Merge the dataframes horizontally on 'feature_id'
    merged_data = reduce(lambda left, right: pd.merge(left, right, on="feature_id", how="outer"), data_frames)

    # The sources of the annotations are processed and combined
    # Create the 'Sources' column. Fill it according the content of the tool_IK2D columns.
    # E.g. if sirius_IK2D is not null and matches isdb_IK2D, then the source is 'SIRIUS, ISDB'

    merged_data = process_IK2D_sources(merged_data)
    merged_data = process_npc_pathway_sources(merged_data)
    merged_data = process_npc_superclass_sources(merged_data)
    merged_data = process_npc_class_sources(merged_data)

    merged_data["sources_number_IK2D"] = merged_data["sources_IK2D"].apply(count_sources)

    # Load GNPS MN data if provided

    if gnps_mn_file:
        gnps_mn_data = pd.read_csv(gnps_mn_file, sep="\t")
        gnps_mn_data = standardize_column_names(gnps_mn_data, "cluster index", "feature_id")
        gnps_mn_data = prefix_columns(gnps_mn_data, "gnps_mn_", exclude_columns=[])
        gnps_mn_data = standardize_column_names(gnps_mn_data, "gnps_mn_feature_id", "feature_id")
        merged_data = pd.merge(merged_data, gnps_mn_data, on="feature_id", how="outer")

    # Select columns

    selected_columns = [
        "feature_id",
        "sources_IK2D",
        "sources_number_IK2D",
        "sources_npc_pathway",
        "sources_npc_superclass",
        "sources_npc_class",
    ]

    # Place the selected columns at the front of the dataframe

    merged_data = merged_data[
        selected_columns + [column for column in merged_data.columns if column not in selected_columns]
    ]

    return merged_data
