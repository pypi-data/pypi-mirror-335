import logging

import pytest

from stormi.logging import configure_logging


def test_configure_logging_returns_logger():
    """Test that configure_logging returns a Logger instance."""
    logger = configure_logging()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "stormi"


def test_configure_logging_custom_name():
    """Test that configure_logging uses the provided logger name."""
    logger = configure_logging("custom_name")
    assert logger.name == "custom_name"


@pytest.mark.parametrize(
    "level_name,expected_level",
    [
        ("DEBUG", logging.DEBUG),
        ("INFO", logging.INFO),
        ("WARNING", logging.WARNING),
        ("ERROR", logging.ERROR),
        ("CRITICAL", logging.CRITICAL),
    ],
)
def test_configure_logging_respects_environment_variable(
    monkeypatch, level_name, expected_level
):
    """Test that configure_logging respects the STORMI_LOG_LEVEL environment variable."""
    monkeypatch.setenv("STORMI_LOG_LEVEL", level_name)
    logger = configure_logging()
    assert logger.level == expected_level


def test_configure_logging_defaults_to_info_for_invalid_level(monkeypatch):
    """Test that configure_logging defaults to INFO for invalid log levels."""
    monkeypatch.setenv("STORMI_LOG_LEVEL", "INVALID")
    logger = configure_logging()
    assert logger.level == logging.INFO
