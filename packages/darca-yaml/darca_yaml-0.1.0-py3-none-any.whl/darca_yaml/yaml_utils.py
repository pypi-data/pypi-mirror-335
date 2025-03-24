"""
yaml_utils.py

Utility module for loading, saving, and validating YAML files.
"""

import yaml
from cerberus import Validator
from darca_exception.exception import DarcaException
from darca_file_utils.file_utils import FileUtils
from darca_log_facility.logger import DarcaLogger

# Logger setup
logger = DarcaLogger(name="yaml_utils").get_logger()


class YamlUtilsException(DarcaException):
    """Custom exception for YAML utility errors."""

    def __init__(self, message, error_code=None, metadata=None, cause=None):
        super().__init__(
            message=message,
            error_code=error_code or "YAML_UTILS_ERROR",
            metadata=metadata,
            cause=cause,
        )


class YamlUtils:
    @staticmethod
    def load_yaml_file(file_path: str) -> dict:
        """
        Load and parse a YAML file.

        Args:
            file_path (str): Path to the YAML file.

        Returns:
            dict: Parsed YAML content.

        Raises:
            YamlUtilsException: On read or parse failure.
        """
        try:
            logger.debug(f"Attempting to read YAML file: {file_path}")
            content = FileUtils.read_file(file_path)
        except Exception as e:
            raise YamlUtilsException(
                message=f"Failed to read YAML file: {file_path}",
                error_code="YAML_FILE_READ_ERROR",
                metadata={"file_path": file_path},
                cause=e,
            )

        try:
            logger.debug(f"Parsing YAML content from: {file_path}")
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise YamlUtilsException(
                message=f"Failed to parse YAML content: {file_path}",
                error_code="YAML_PARSE_ERROR",
                metadata={"file_path": file_path},
                cause=e,
            )

        if not isinstance(data, dict) and data is not None:
            raise YamlUtilsException(
                message=f"Invalid YAML structure (expected dict): {file_path}",
                error_code="YAML_INVALID_STRUCTURE",
                metadata={"file_path": file_path, "type": str(type(data))},
            )

        logger.debug(f"YAML successfully loaded from {file_path}: {data}")
        return data or {}

    @staticmethod
    def save_yaml_file(
        file_path: str, data: dict, validate: bool = False, schema: dict = None
    ) -> bool:
        """
        Save data to a YAML file, with optional validation.

        Args:
            file_path (str): Path to save YAML file.
            data (dict): Data to be saved.
            validate (bool): Whether to validate the data.
            schema (dict): Schema used for validation
                           (required if validate=True).

        Returns:
            bool: True if file saved successfully.

        Raises:
            YamlUtilsException: On validation, serialization, or save failure.
        """
        if validate:
            logger.debug("Validation requested before saving YAML.")
            if not schema:
                raise YamlUtilsException(
                    message="Schema must be provided for YAML validation.",
                    error_code="YAML_VALIDATION_SCHEMA_MISSING",
                    metadata={"file_path": file_path},
                )
            YamlUtils.validate_yaml(data, schema)

        try:
            logger.debug(f"Serializing data to YAML for file: {file_path}")
            yaml_content = yaml.dump(data, sort_keys=False)
        except Exception as e:
            # Catch all exceptions (not just yaml.YAMLError) to ensure robust
            # error handling
            raise YamlUtilsException(
                message="Failed to serialize data to YAML.",
                error_code="YAML_SERIALIZE_ERROR",
                metadata={"file_path": file_path},
                cause=e,
            )

        try:
            return FileUtils.write_file(file_path, yaml_content)
        except Exception as e:
            raise YamlUtilsException(
                message=f"Failed to write YAML file: {file_path}",
                error_code="YAML_FILE_WRITE_ERROR",
                metadata={"file_path": file_path},
                cause=e,
            )

    @staticmethod
    def validate_yaml(data: dict, schema: dict) -> bool:
        """
        Validate YAML content using Cerberus schema.

        Args:
            data (dict): YAML data to validate.
            schema (dict): Cerberus schema definition.

        Returns:
            bool: True if valid.

        Raises:
            YamlUtilsException: If validation fails.
        """
        logger.debug("Validating YAML data with schema.")
        validator = Validator(schema)
        if not validator.validate(data):
            logger.error(f"YAML validation failed: {validator.errors}")
            raise YamlUtilsException(
                message="YAML validation failed.",
                error_code="YAML_VALIDATION_ERROR",
                metadata={"errors": validator.errors},
            )
        logger.debug("YAML validation succeeded.")
        return True
