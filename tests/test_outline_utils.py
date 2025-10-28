"""
Tests for outline_utils.py module
"""

import os
import pytest
from outline_utils import (
    load_yaml_outline,
    format_beat_for_prompt,
    get_continuation_text,
    format_story_context
)

def test_load_yaml_outline(temp_yaml_file, sample_outline):
    """Test loading a YAML outline file."""
    loaded_outline = load_yaml_outline(temp_yaml_file)
    assert loaded_outline["title"] == sample_outline["title"]
    assert loaded_outline["setting"] == sample_outline["setting"]
    assert len(loaded_outline["beats"]) == len(sample_outline["beats"])

def test_load_yaml_outline_nonexistent_file():
    """Test loading a non-existent YAML file raises an error."""
    with pytest.raises(ValueError):
        load_yaml_outline("nonexistent_file.yaml")

def test_format_beat_for_prompt(sample_outline):
    """Test formatting a beat for prompting."""
    beat = sample_outline["beats"][0]
    formatted = format_beat_for_prompt(beat)
    
    # Check that the formatted string contains the expected components
    assert beat["name"] in formatted
    assert beat["description"] in formatted
    for element in beat["key_elements"]:
        assert element in formatted

def test_get_continuation_text():
    """Test extracting continuation text from a longer text."""
    test_text = "This is a test sentence. And here is another one. This is the third sentence to include."
    
    # Test with default chars (120)
    continuation = get_continuation_text(test_text)
    assert continuation == test_text  # Full text since it's less than 120 chars
    
    # Test with smaller chars limit
    continuation = get_continuation_text(test_text, chars=20)
    assert len(continuation) <= len(test_text)
    assert continuation.startswith("This is the third")  # Should start at a sentence break
    
    # Test with tiny text
    tiny_text = "Short."
    continuation = get_continuation_text(tiny_text, chars=50)
    assert continuation == tiny_text

def test_format_story_context(sample_outline):
    """Test formatting the complete story context for prompting."""
    # Test first beat (no previous context)
    context = format_story_context(sample_outline, 0)
    assert sample_outline["title"] in context
    assert sample_outline["setting"] in context
    assert sample_outline["protagonist"] in context
    assert sample_outline["beats"][0]["name"] in context
    assert "Previous events" not in context  # No previous events for first beat
    
    # Test second beat (with previous context)
    context = format_story_context(sample_outline, 1)
    assert sample_outline["title"] in context
    assert "Previous events" in context
    assert sample_outline["beats"][0]["description"] in context  # Previous beat description
    assert sample_outline["beats"][1]["name"] in context  # Current beat
    
    # Test with previous text
    context = format_story_context(sample_outline, 1, previous_text="Previously generated text.")
    assert "Previously generated text" in context
