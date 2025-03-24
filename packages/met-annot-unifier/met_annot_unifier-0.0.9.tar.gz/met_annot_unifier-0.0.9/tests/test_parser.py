import numpy as np
import pandas as pd
import pytest

from met_annot_unifier.aligner.parser import (
    extract_feature_id,
    parse_gnps,
    parse_isdb,
    parse_sirius,
    standardize_column_names,
)

# Path to your sample data files
GNPS_SAMPLE_PATH = "tests/data/gnps_output_example.tsv"
SIRIUS_SAMPLE_PATH = "tests/data/sirius_output_example.tsv"
ISDB_SAMPLE_PATH = "tests/data/isdb_output_example.tsv"


def test_parse_gnps():
    # Load the sample GNPS data
    gnps_data = parse_gnps(GNPS_SAMPLE_PATH)

    # Assertions to check if the data is loaded correctly
    assert not gnps_data.empty, "Dataframe is empty"
    assert "#Scan#" in gnps_data.columns, "feature_id column is missing"
    assert "InChIKey-Planar" in gnps_data.columns, "IK2D column is missing"
    # ... add more assertions as needed ...


def test_parse_sirius():
    # Load the sample Sirius data
    sirius_data = parse_sirius(SIRIUS_SAMPLE_PATH)

    # Similar assertions for Sirius data
    assert not sirius_data.empty, "Dataframe is empty"
    assert "mappingFeatureId" in sirius_data.columns, "feature_id column is missing"
    assert "InChIkey2D" in sirius_data.columns, "IK2D column is missing"
    # ... add more assertions as needed ...


def test_parse_isdb():
    # Load the sample ISDB data
    isdb_data = parse_isdb(ISDB_SAMPLE_PATH)

    # Similar assertions for ISDB data
    assert not isdb_data.empty, "Dataframe is empty"
    assert "feature_id" in isdb_data.columns, "feature_id column is missing"
    assert "short_inchikey" in isdb_data.columns, "IK2D column is missing"
    # ... add more assertions as needed ...


def test_successful_column_renaming():
    df = pd.DataFrame({"InChIKey-Planar": [1, 2], "OtherColumn": [3, 4]})
    result = standardize_column_names(df, "InChIKey-Planar", "InChiKey")
    assert "InChiKey" in result.columns
    assert "InChIKey-Planar" not in result.columns


def test_no_change_when_column_missing():
    df = pd.DataFrame({"SomeOtherColumn": [1, 2], "OtherColumn": [3, 4]})
    result = standardize_column_names(df, "InChIKey-Planar", "InChiKey")
    assert "InChiKey" not in result.columns
    assert "InChIKey-Planar" not in result.columns


def test_preservation_of_other_data():
    df = pd.DataFrame({"InChIKey-Planar": [1, 2], "OtherColumn": [3, 4]})
    result = standardize_column_names(df, "InChIKey-Planar", "InChiKey")
    assert all(result["OtherColumn"] == df["OtherColumn"])


def test_typical_use_case():
    df = pd.DataFrame({"FeatureID": ["573_mapp_batch_00020_gf_sirius_58", "574_mapp_batch_00021_gf_sirius_59"]})
    result = extract_feature_id(df, "FeatureID")
    assert list(result["FeatureID"]) == [58, 59]


def test_no_numeric_part():
    df = pd.DataFrame({"FeatureID": ["feature_without_number"]})
    with pytest.raises(ValueError):
        extract_feature_id(df, "FeatureID")


def test_multiple_numeric_parts():
    df = pd.DataFrame({"FeatureID": ["123_456_feature_789"]})
    result = extract_feature_id(df, "FeatureID")
    assert list(result["FeatureID"]) == [789]


def test_empty_string():
    df = pd.DataFrame({"FeatureID": [""]})
    with pytest.raises(ValueError):
        extract_feature_id(df, "FeatureID")


def test_non_string_input():
    df = pd.DataFrame({"FeatureID": [None, 123]})
    result = extract_feature_id(df, "FeatureID")
    assert np.isnan(result["FeatureID"][0]) and result["FeatureID"][1] == 123  # Adjusted expectation
