#!/usr/bin/env python3
"""
NCOS v24 - Helper Utilities
A collection of general-purpose helper classes and functions for configuration,
file handling, and other common tasks.
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Union

class ConfigHelper:
    """
    A utility class for loading and managing configurations from files.
    It supports both YAML and JSON formats and can merge multiple configurations.
    """

    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Loads a configuration from a YAML or JSON file.

        Args:
            file_path: The path to the configuration file.

        Returns:
            A dictionary containing the loaded configuration.

        Raises:
            FileNotFoundError: If the config file is not found.
            ValueError: If the file format is unsupported.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {path}")

        with open(path, 'r') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                try:
                    return yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise ValueError(f"Error parsing YAML file {path}: {e}")
            elif path.suffix.lower() == '.json':
                import json
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Error parsing JSON file {path}: {e}")
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")

    @staticmethod
    def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merges two dictionaries. The 'override' dictionary's values
        take precedence over the 'base' dictionary's values.

        Args:
            base: The base configuration dictionary.
            override: The dictionary with override values.

        Returns:
            The merged dictionary.
        """
        result = base.copy()
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = ConfigHelper.merge_configs(result[key], value)
            else:
                result[key] = value
        return result

class FileHelper:
    """A utility class for common file system operations."""

    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """
        Ensures that a directory exists. If it doesn't, it creates it.

        Args:
            path: The path to the directory.

        Returns:
            A Path object for the directory.
        """
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj
