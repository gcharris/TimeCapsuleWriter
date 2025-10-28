"""
Tests for character_utils.py module
"""

import os
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from character_utils import (
    list_available_characters,
    load_character_profile,
    format_character_for_prompt,
    integrate_characters_with_prompt
)

@pytest.fixture
def mock_character_dir(monkeypatch):
    """Create a temporary directory for test character profiles."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test character profile
        char_file = Path(temp_dir) / "test_character.md"
        with open(char_file, 'w') as f:
            f.write("""# Test Character Profile

## Basic Information
- Name: John Smith
- Age: 40

## Physical Appearance
- Tall and thin
- Always wears a hat
""")
        
        # Override the character directory config
        monkeypatch.setattr(config, "CHARACTERS_DIR", temp_dir)
        
        yield temp_dir

def test_list_available_characters(mock_character_dir):
    """Test listing available characters."""
    characters = list_available_characters()
    assert "test_character" in characters

def test_load_character_profile(mock_character_dir):
    """Test loading a character profile."""
    profile = load_character_profile("test_character")
    assert profile is not None
    assert "John Smith" in profile
    
    # Test loading nonexistent character
    profile = load_character_profile("nonexistent")
    assert profile is None

def test_format_character_for_prompt(mock_character_dir):
    """Test formatting a character profile for prompts."""
    profile = load_character_profile("test_character")
    formatted = format_character_for_prompt(profile)
    
    # Check basic structure
    assert "## Character: Test Character" in formatted
    assert "### Basic Information:" in formatted
    assert "- Name: John Smith" in formatted
    
    # Should be more compact than the original
    assert len(formatted) < len(profile)

def test_integrate_characters_with_prompt():
    """Test integrating character profiles into prompts."""
    original_prompt = "Write a Victorian-era story about London."
    
    # Mock the loading and formatting of characters
    def mock_load_character_profile(name):
        return f"# {name.title()} Profile\n\nTest character content for {name}"
    
    # Patch the functions temporarily
    real_load = character_utils.load_character_profile
    real_format = character_utils.format_character_for_prompt
    
    try:
        character_utils.load_character_profile = mock_load_character_profile
        character_utils.format_character_for_prompt = lambda p: f"Formatted: {p}"
        
        # Test with single character
        result = integrate_characters_with_prompt(original_prompt, "clerk")
        assert "## Characters" in result
        assert "Formatted: # Clerk Profile" in result
        assert "Write a Victorian-era story about London." in result
        
        # Test with multiple characters
        result = integrate_characters_with_prompt(original_prompt, ["clerk", "governess"])
        assert "Formatted: # Clerk Profile" in result
        assert "Formatted: # Governess Profile" in result
    
    finally:
        # Restore original functions
        character_utils.load_character_profile = real_load
        character_utils.format_character_for_prompt = real_format
