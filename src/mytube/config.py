"""Configuration loading utilities for MyTube."""

from pathlib import Path

import yaml


def load_config(config_path: str | Path = None) -> dict:
    """Load configuration from config.yaml.

    Args:
        config_path: Path to config file. If None, searches for config.yaml
                     in the current working directory.

    Returns:
        Configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
    """
    if config_path is None:
        config_path = Path.cwd() / "config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Please copy config.example.yaml to config.yaml and adjust settings."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
