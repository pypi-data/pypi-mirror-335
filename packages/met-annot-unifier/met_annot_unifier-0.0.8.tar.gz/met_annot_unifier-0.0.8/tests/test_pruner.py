from io import StringIO

import pandas as pd
import pytest
from click.testing import CliRunner

from met_annot_unifier.cli import cli


# Utility function to create a sample DataFrame
def create_sample_dataframe():
    data = {
        "gnps_SpectrumID": [1, 2, 3],
        "sirius_SMILES": ["C10H20O", "C15H24O3", "C20H40O2"],
        "isdb_structure_nameTraditional": ["Compound1", "Compound2", "Compound3"],
        "RetentionTime": [5.1, 10.2, 15.3],
    }
    return pd.DataFrame(data)


# Fixture to use a temporary directory provided by pytest
@pytest.fixture
def temp_dir(tmpdir):
    return tmpdir


def test_prune_valid_inputs_keep(temp_dir):
    df = create_sample_dataframe()
    input_file = temp_dir.join("input.csv")
    output_file = temp_dir.join("output.csv")
    df.to_csv(input_file, index=False, sep="\t")

    runner = CliRunner()
    result = runner.invoke(
        cli, ["prune-table", "--input-file", str(input_file), "--list-columns", "test", "-o", str(output_file)]
    )

    print(result.output)

    assert result.exit_code == 0
    assert "Pruned data saved to" in result.output
    output_df = pd.read_csv(output_file, sep="\t")
    assert "gnps_SpectrumID" in output_df.columns
    assert "sirius_SMILES" in output_df.columns
    assert "isdb_structure_nameTraditional" not in output_df.columns


def test_prune_valid_inputs_remove(temp_dir):
    df = create_sample_dataframe()
    input_file = temp_dir.join("input.csv")
    output_file = temp_dir.join("output.csv")
    df.to_csv(input_file, index=False, sep="\t")

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["prune-table", "--remove", "--input-file", str(input_file), "--list-columns", "test", "-o", str(output_file)],
    )

    print(result.output)

    assert result.exit_code == 0
    assert "Pruned data saved to" in result.output
    output_df = pd.read_csv(output_file, sep="\t")
    assert "gnps_SpectrumID" not in output_df.columns
    assert "sirius_SMILES" not in output_df.columns
    assert "isdb_structure_nameTraditional" in output_df.columns


def test_prune_non_existent_columns(temp_dir):
    df = create_sample_dataframe()
    input_file = temp_dir.join("input.csv")
    output_file = temp_dir.join("output.csv")
    df.to_csv(input_file, index=False, sep="\t")

    runner = CliRunner()
    result = runner.invoke(
        cli, ["prune-table", "--input-file", str(input_file), "--list-columns", "nonexistent", "-o", str(output_file)]
    )

    print(result.output)
    print(result.exception)
    print(result.exit_code)

    # print(result.output)
    # assert "Error: 'nonexistent' is not a valid key in the configuration." in result.output
    assert result.exit_code != 0


def test_no_output_path(temp_dir):
    df = create_sample_dataframe()
    input_file = temp_dir.join("input.csv")
    df.to_csv(input_file, index=False, sep="\t")

    runner = CliRunner()
    result = runner.invoke(cli, ["prune-table", "--input-file", str(input_file), "--list-columns", "test"])

    assert result.exit_code == 0
    output_df = pd.read_csv(StringIO(result.output), sep="\t")
    assert "gnps_SpectrumID" not in output_df.columns


# Add more tests as needed for various other cases
