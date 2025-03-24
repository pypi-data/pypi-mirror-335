import pytest
from click.testing import CliRunner

from met_annot_unifier.cli import cli  # Replace with your actual import


def test_cli_align_vertically():
    runner = CliRunner()

    # Test with valid arguments
    result = runner.invoke(
        cli,
        [
            "align-vertically",
            "--gnps-file",
            "tests/data/gnps_output_example_sub.tsv",
            "--sirius-file",
            "tests/data/sirius_output_example_sub.tsv",
            "--isdb-file",
            "tests/data/isdb_output_example_sub.tsv",
            "--output",
            "tests/data/output_sub.tsv",
        ],
    )
    print(result.output)

    # Check if the CLI ran successfully (exit code 0)
    assert result.exit_code == 0
    # Optional: Check specific output message or behavior
    # assert 'Some specific success message' in result.output

    # Test handling of invalid arguments or files
    result_invalid = runner.invoke(
        cli,
        [
            "align-vertically",
            "--gnps-file",
            "nonexistent_file.tsv",
            "--sirius-file",
            "tests/data/sirius_output_example_sub.tsv",
            "--isdb-file",
            "tests/data/isdb_output_example_sub.tsv",
            "--output",
            "tests/data/output_sub.tsv",
        ],
    )

    # Check for correct handling of errors (non-zero exit code)
    assert result_invalid.exit_code != 0
    # Optional: Check specific error message
    # assert 'Error message for invalid file' in result_invalid.output

    # Additional tests for other command line arguments or error cases


def test_cli_align_horizontally():
    runner = CliRunner()

    # Test with valid arguments
    result = runner.invoke(
        cli,
        [
            "align-horizontally",
            "--gnps-file",
            "tests/data/gnps_output_example_sub.tsv",
            "--sirius-file",
            "tests/data/sirius_output_example_sub.tsv",
            "--isdb-file",
            "tests/data/isdb_output_example_sub.tsv",
            "--output",
            "tests/data/output_sub.tsv",
        ],
    )
    print(result.output)

    # Check if the CLI ran successfully (exit code 0)
    assert result.exit_code == 0
    # Optional: Check specific output message or behavior
    # assert 'Some specific success message' in result.output

    # Test handling of invalid arguments or files
    result_invalid = runner.invoke(
        cli,
        [
            "align-horizontally",
            "--gnps-file",
            "nonexistent_file.tsv",
            "--sirius-file",
            "tests/data/sirius_output_example_sub.tsv",
            "--isdb-file",
            "tests/data/isdb_output_example_sub.tsv",
            "--output",
            "tests/data/output_sub.tsv",
        ],
    )

    # Check for correct handling of errors (non-zero exit code)
    assert result_invalid.exit_code != 0
    # Optional: Check specific error message
    # assert 'Error message for invalid file' in result_invalid.output

    # Additional tests for other command line arguments or error cases


# Run the tests
if __name__ == "__main__":
    pytest.main()
