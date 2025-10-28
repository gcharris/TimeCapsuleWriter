"""
Tests for config.py module
"""

import os
import pytest
import config

def test_config_values():
    """Test that config has expected values and types."""
    # Test MODEL_ID is a string and matches expected format
    assert isinstance(config.MODEL_ID, str)
    assert "/" in config.MODEL_ID  # Should be in format "org/model"
    
    # Test DEFAULTS dictionary has expected keys and types
    assert isinstance(config.DEFAULTS, dict)
    assert "max_new_tokens" in config.DEFAULTS
    assert "temperature" in config.DEFAULTS
    assert "top_p" in config.DEFAULTS
    assert "repetition_penalty" in config.DEFAULTS
    
    assert isinstance(config.DEFAULTS["max_new_tokens"], int)
    assert isinstance(config.DEFAULTS["temperature"], float)
    assert isinstance(config.DEFAULTS["top_p"], float)
    assert isinstance(config.DEFAULTS["repetition_penalty"], float)
    
    # Test paths are strings
    assert isinstance(config.PROMPTS_DIR, str)
    assert isinstance(config.OUTPUTS_DIR, str)

def test_directory_structure():
    """Test that the directory structure exists as defined in config."""
    # Check that the prompts directory exists
    assert os.path.isdir(config.PROMPTS_DIR), f"Prompts directory {config.PROMPTS_DIR} not found"
    
    # Outputs directory might not exist yet, but it should be creatable
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    assert os.path.isdir(config.OUTPUTS_DIR), f"Outputs directory {config.OUTPUTS_DIR} could not be created"
