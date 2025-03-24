from typing import Optional

import pandas as pd


def parse_gnps(file_path: str) -> pd.DataFrame:
    # Read the GNPS output file
    data = pd.read_csv(file_path, sep="\t")
    # Extract necessary columns and any other processing
    return data


def parse_isdb(file_path: str) -> pd.DataFrame:
    # Read the ISDB output file
    data = pd.read_csv(file_path, sep="\t")
    # Extract necessary columns and any other processing
    return data


def parse_sirius(file_path: str) -> pd.DataFrame:
    # Read the Sirius output file
    data = pd.read_csv(file_path, sep="\t")
    # Extract necessary columns and any other processing
    return data


def parse_canopus(file_path: str) -> pd.DataFrame:
    # Read the Canopus output file
    data = pd.read_csv(file_path, sep="\t")
    # Extract necessary columns and any other processing
    return data


def standardize_column_names(df: pd.DataFrame, original_column_name: str, final_column_name: str) -> pd.DataFrame:
    """
    Standardizes the column names of a dataframe.

    Args:
    df (pandas.DataFrame): The dataframe to standardize.
    original_column_name (str): The current name of the column to be standardized.
    final_column_name (str): The final standardized name for the column.

    Returns:
    pandas.DataFrame: The dataframe with standardized column names.

    Example:
    >>> df = pd.DataFrame({'InChIKey-Planar': [1, 2], 'OtherColumn': [3, 4]})
    >>> standardized_df = standardize_column_names(df, 'InChIKey-Planar', 'InChiKey')
    >>> standardized_df.columns
    Index(['InChiKey', 'OtherColumn'], dtype='object')
    """
    standardized_df = df.rename(columns={original_column_name: final_column_name})
    return standardized_df


def extract_feature_id(df: pd.DataFrame, feature_id_column: str) -> pd.DataFrame:
    """
    Extracts the numeric feature ID from a string in the specified column of a dataframe.

    Args:
    df (pandas.DataFrame): The dataframe containing the feature ID strings.
    feature_id_column (str): The name of the column containing the feature ID strings.

    Returns:
    pandas.DataFrame: The dataframe with the feature ID extracted.

    Example:
    >>> df = pd.DataFrame({'FeatureID': ['573_mapp_batch_00020_gf_sirius_58', '574_mapp_batch_00021_gf_sirius_59']})
    >>> cleaned_df = extract_feature_id(df, 'FeatureID')
    >>> cleaned_df['FeatureID']
    0    58
    1    59
    Name: FeatureID, dtype: int64
    """

    def extract_id(feature_string: Optional[str]) -> Optional[int]:
        if isinstance(feature_string, str):
            # Split the string by '_' and extract the last part, then convert to integer
            return int(feature_string.split("_")[-1])
        else:
            # Handle non-string inputs (like None or NaN)
            # You can decide how to handle this - raise an error, return None, or something else
            return feature_string  # or raise ValueError("Invalid feature string")

    df[feature_id_column] = df[feature_id_column].apply(extract_id)
    return df


def prefix_columns(df: pd.DataFrame, prefix: str, exclude_columns: Optional[list] = None) -> pd.DataFrame:
    """
    Prefixes all columns in a dataframe with the specified prefix, excluding specified columns.

    Args:
    df (pandas.DataFrame): The dataframe to modify.
    prefix (str): The prefix to add to the column names.
    exclude_columns (list, optional): list of column names to exclude from prefixing. Defaults to None.

    Returns:
    pandas.DataFrame: The dataframe with prefixed column names.

    Example:
    >>> df = pd.DataFrame({'feature_id': [1, 2], 'data': [3, 4], 'info': [5, 6]})
    >>> prefixed_df = prefix_columns(df, 'gnps_', exclude_columns=['feature_id'])
    >>> prefixed_df.columns
    Index(['feature_id', 'gnps_data', 'gnps_info'], dtype='object')
    """
    if exclude_columns is None:
        exclude_columns = []

    for column in df.columns:
        if column not in exclude_columns:
            df = df.rename(columns={column: f"{prefix}{column}"})
    return df


def add_source_column(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Adds a 'annotation_source' column to a dataframe, labeling all rows with the specified source name.

    Args:
    df (pandas.DataFrame): The dataframe to modify.
    source_name (str): The name of the source to add (e.g., 'GNPS', 'ISDB', 'SIRIUS').

    Returns:
    pandas.DataFrame: The dataframe with the 'annotation_source' column added.
    """
    df["annotation_source"] = source_name
    return df


def process_gnps_data(gnps_file: str) -> pd.DataFrame:
    """
    Reads and processes GNPS data. This function standardizes column names, prefixes them to indicate their source,
    and extracts 'feature_id' and 'IK2D' from the data.

    Args:
    gnps_file (str): File path for the GNPS data in TSV format.

    Returns:
    pandas.DataFrame: A DataFrame with processed GNPS data.

    Example:
    >>> gnps_file = 'path/to/gnps_data.tsv'
    >>> gnps_data = process_gnps_data(gnps_file)
    >>> print(gnps_data.columns)
    Index(['feature_id', 'IK2D', ...], dtype='object')
    """

    # Read and process GNPS data
    gnps_data = pd.read_csv(gnps_file, sep="\t")
    gnps_data = add_source_column(gnps_data, "gnps")
    gnps_data = standardize_column_names(gnps_data, "InChIKey-Planar", "IK2D")
    gnps_data = standardize_column_names(gnps_data, "#Scan#", "feature_id")
    gnps_data = standardize_column_names(gnps_data, "Smiles", "SMILES")
    gnps_data = prefix_columns(gnps_data, "gnps_", exclude_columns=[])
    gnps_data = standardize_column_names(gnps_data, "gnps_IK2D", "IK2D")
    gnps_data = standardize_column_names(gnps_data, "gnps_feature_id", "feature_id")

    return gnps_data


def process_isdb_data(isdb_file: str) -> pd.DataFrame:
    """
    Reads and processes ISDB data. This function standardizes column names, prefixes them to indicate their source,
    and extracts 'feature_id' and 'IK2D' from the data.

    Args:
    isdb_file (str): File path for the ISDB data in TSV format.

    Returns:
    pandas.DataFrame: A DataFrame with processed ISDB data.

    Example:
    >>> isdb_file = 'path/to/isdb_data.tsv'
    >>> isdb_data = process_isdb_data(isdb_file)
    >>> print(isdb_data.columns)
    Index(['feature_id', 'IK2D', ...], dtype='object')
    """

    # Read and process ISDB data
    isdb_data = pd.read_csv(isdb_file, sep="\t")
    isdb_data = add_source_column(isdb_data, "isdb")
    isdb_data = standardize_column_names(isdb_data, "short_inchikey", "IK2D")
    isdb_data = standardize_column_names(isdb_data, "feature_id", "feature_id")
    isdb_data = standardize_column_names(isdb_data, "structure_smiles", "SMILES")
    isdb_data = prefix_columns(isdb_data, "isdb_", exclude_columns=[])
    isdb_data = standardize_column_names(isdb_data, "isdb_IK2D", "IK2D")
    isdb_data = standardize_column_names(isdb_data, "isdb_feature_id", "feature_id")

    return isdb_data


def process_sirius_data(sirius_file: str) -> pd.DataFrame:
    """
    Reads and processes Sirius data. This function standardizes column names, prefixes them to indicate their source,
    and extracts 'feature_id' and 'IK2D' from the data.

    Args:
    sirius_file (str): File path for the Sirius data in TSV format.

    Returns:
    pandas.DataFrame: A DataFrame with processed Sirius data.

    Example:
    >>> sirius_file = 'path/to/sirius_data.tsv'
    >>> sirius_data = process_sirius_data(sirius_file)
    >>> print(sirius_data.columns)
    Index(['feature_id', 'IK2D', ...], dtype='object')
    """

    # Read and process Sirius data
    sirius_data = pd.read_csv(sirius_file, sep="\t")
    sirius_data = add_source_column(sirius_data, "sirius")
    sirius_data = standardize_column_names(sirius_data, "InChIkey2D", "IK2D")
    sirius_data = standardize_column_names(sirius_data, "mappingFeatureId", "feature_id")
    sirius_data = standardize_column_names(sirius_data, "smiles", "SMILES")
    sirius_data = prefix_columns(sirius_data, "sirius_", exclude_columns=[])
    sirius_data = extract_feature_id(sirius_data, "sirius_feature_id")
    sirius_data = standardize_column_names(sirius_data, "sirius_IK2D", "IK2D")
    sirius_data = standardize_column_names(sirius_data, "sirius_feature_id", "feature_id")

    return sirius_data


def process_canopus_data(canopus_file: str) -> pd.DataFrame:
    """
    Reads and processes Canopus data. This function standardizes column names, prefixes them to indicate their source,
    and extracts 'feature_id' from the data.

    Args:
    canopus_file (str): File path for the Canopus data in TSV format.

    Returns:
    pandas.DataFrame: A DataFrame with processed Canopus data.

    Example:
    >>> canopus_file = 'path/to/canopus_data.tsv'
    >>> canopus_data = process_canopus_data(canopus_file)
    >>> print(canopus_data.columns)
    Index(['feature_id', ...], dtype='object')
    """

    # Read and process Canopus data
    canopus_data = pd.read_csv(canopus_file, sep="\t")
    canopus_data = add_source_column(canopus_data, "canopus")
    canopus_data = standardize_column_names(canopus_data, "id", "feature_id")
    canopus_data = prefix_columns(canopus_data, "canopus_", exclude_columns=[])
    canopus_data = extract_feature_id(canopus_data, "canopus_feature_id")
    canopus_data = standardize_column_names(canopus_data, "canopus_feature_id", "feature_id")

    return canopus_data
