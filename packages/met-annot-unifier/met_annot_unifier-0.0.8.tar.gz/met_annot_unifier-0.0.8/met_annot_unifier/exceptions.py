class DataFileError(ValueError):
    """Exception raised when no data files are provided or they are invalid."""

    def __init__(
        self,
        message: str = "At least one data file must be provided. Please ensure that the file paths are correct and point to valid data files. This function cannot operate without input data.",
    ) -> None:
        self.message = message
        super().__init__(self.message)


class ConfigKeyError(KeyError):
    """Exception raised when the specified key is not found in the configuration file."""

    def __init__(self, key: str):
        message = f"Error: '{key}' is not a valid key in the configuration."
        super().__init__(message)
