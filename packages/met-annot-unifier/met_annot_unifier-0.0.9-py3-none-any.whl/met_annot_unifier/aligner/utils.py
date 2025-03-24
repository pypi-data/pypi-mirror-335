# Function to determine matching sources
import json
from importlib import resources
from typing import Any, cast

import pandas as pd
from pandas import DataFrame, Series

# def determine_source(row: pd.Series) -> str:
#     # Filter columns that are related to IK2D data and exist in the row
#     ik2d_columns = [col for col in row.index if "IK2D" in col and pd.notna(row[col])]

#     # Map columns to sources by extracting the prefix before '_IK2D'
#     sources = {col.split("_")[0] for col in ik2d_columns}

#     # Check if any of the values are the same across different sources, consolidate them
#     unique_ik2ds = {row[col] for col in ik2d_columns}
#     if len(unique_ik2ds) == 1:
#         # All values are the same, include all sources
#         return "|".join(sorted(sources))

#     # Return sources as sorted string joined by '|'
#     return "|".join(sorted(sources))


# def determine_source(row: pd.Series) -> str:
#     # Filter columns that are related to IK2D data and have non-null values
#     ik2d_columns = [col for col in row.index if "IK2D" in col and pd.notna(row[col])]

#     # Extract the source prefixes from the column names
#     sources = {col.split("_")[0] for col in ik2d_columns}

#     # Extract unique IK2D values from the filtered columns, after standardizing them
#     unique_ik2ds = {str(row[col]).strip().lower() for col in ik2d_columns}

#     # If there is only one unique value, all sources agree on the same IK2D data
#     if len(unique_ik2ds) == 1:
#         # Print the row where IK2D values are matching
#         print(f"Row with matching IK2D values: {row.name}")
#         print(f"IK2D Values: {unique_ik2ds}")

#         # Return all sources joined by '|'
#         return "|".join(sorted(sources))

#     # Return sorted sources as a string joined by '|'
#     return "|".join(sorted(sources))

# # Function to determine the source based on non-null IK2D values
# def determine_source(row, ik2d_columns):
#     sources = []
#     for col in ik2d_columns:
#         if pd.notna(row[col]):
#             # Extract the source name from the column name
#             source = col.split('_')[0]
#             sources.append(source)
#     # Sort sources alphabetically and join with '|'
#     return '|'.join(sorted(sources))


def process_IK2D_sources(df: DataFrame) -> DataFrame:
    def process_row(row: Series) -> str:
        sources = {col.replace("_IK2D", ""): row[col] for col in row.index if col.endswith("_IK2D")}
        non_na_sources = {k: v for k, v in sources.items() if pd.notna(v)}

        values_to_sources: dict[str, list[str]] = {}
        for source, value in non_na_sources.items():
            if value in values_to_sources:
                values_to_sources[value].append(source)
            else:
                values_to_sources[value] = [source]

        matched_groups = []
        for _value, source_list in values_to_sources.items():
            matched_groups.append("|".join(sorted(source_list)))

        sources_str = " & ".join(sorted(matched_groups)) if matched_groups else ""

        return sources_str

    df["sources_IK2D"] = df.apply(process_row, axis=1)
    return df


def process_npc_pathway_sources(df: DataFrame) -> DataFrame:
    def process_row(row: Series) -> str:
        sources = {col.replace("_npc_pathway", ""): row[col] for col in row.index if col.endswith("_npc_pathway")}
        non_na_sources = {k: v for k, v in sources.items() if pd.notna(v)}

        values_to_sources: dict[str, list[str]] = {}
        for source, value in non_na_sources.items():
            if value in values_to_sources:
                values_to_sources[value].append(source)
            else:
                values_to_sources[value] = [source]

        matched_groups = []
        for _value, source_list in values_to_sources.items():
            matched_groups.append("|".join(sorted(source_list)))

        sources_str = " & ".join(sorted(matched_groups)) if matched_groups else ""

        return sources_str

    df["sources_npc_pathway"] = df.apply(process_row, axis=1)
    return df


def process_npc_superclass_sources(df: DataFrame) -> DataFrame:
    def process_row(row: Series) -> str:
        sources = {col.replace("_npc_superclass", ""): row[col] for col in row.index if col.endswith("_npc_superclass")}
        non_na_sources = {k: v for k, v in sources.items() if pd.notna(v)}

        values_to_sources: dict[str, list[str]] = {}
        for source, value in non_na_sources.items():
            if value in values_to_sources:
                values_to_sources[value].append(source)
            else:
                values_to_sources[value] = [source]

        matched_groups = []
        for _value, source_list in values_to_sources.items():
            matched_groups.append("|".join(sorted(source_list)))

        sources_str = " & ".join(sorted(matched_groups)) if matched_groups else ""

        return sources_str

    df["sources_npc_superclass"] = df.apply(process_row, axis=1)
    return df


def process_npc_class_sources(df: DataFrame) -> DataFrame:
    def process_row(row: Series) -> str:
        sources = {col.replace("_npc_class", ""): row[col] for col in row.index if col.endswith("_npc_class")}
        non_na_sources = {k: v for k, v in sources.items() if pd.notna(v)}

        values_to_sources: dict[str, list[str]] = {}
        for source, value in non_na_sources.items():
            if value in values_to_sources:
                values_to_sources[value].append(source)
            else:
                values_to_sources[value] = [source]

        matched_groups = []
        for _value, source_list in values_to_sources.items():
            matched_groups.append("|".join(sorted(source_list)))

        sources_str = " & ".join(sorted(matched_groups)) if matched_groups else ""

        return sources_str

    df["sources_npc_class"] = df.apply(process_row, axis=1)
    return df


# Function to count the sources
def count_sources(source_str: str) -> int:
    if source_str:
        # Count unique source names (they are | separated)
        return len(set(source_str.split("|")))
    return 0


def table_pruner(df: pd.DataFrame, columns: list, remove: bool = False) -> pd.DataFrame:
    """
    Function to remove or keep only specified columns from a DataFrame.

    Args:
        df (pandas.DataFrame): Input DataFrame.
        columns (list): list of columns to either remove or keep.
        remove (bool): If True, removes specified columns. If False, keeps only specified columns.

    Returns:
        pandas.DataFrame: DataFrame after columns have been either removed or retained.
    """
    if remove:
        # Drop specified columns and return the DataFrame
        return df.drop(columns=columns, axis=1)
    else:
        # Keep only specified columns and return the DataFrame
        return df[columns]


def load_configuration(config_filename: str) -> dict[str, Any]:
    """
    Function to load configuration from a JSON file.

    Args:
        config_filename (str): Filename of the configuration file to load.

    Returns:
        dict[str, Any]: Configuration dictionary.
    """
    package = "met_annot_unifier.config"

    # New way to access resources using importlib.resources
    resource_path = resources.files(package) / config_filename
    print(f"Resource path: {resource_path}")
    with resource_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    # current_path = Path(__file__).resolve()
    # print(f"Current file path: {current_path}")
    # print(f"Current working directory: {Path.cwd()}")

    # Cast the loaded config to dict[str, Any] to satisfy type checkers
    return cast(dict[str, Any], config)
