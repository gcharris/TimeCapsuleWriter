"""
Utilities for managing character profiles in TimeCapsuleWriter.

This module provides functions to load, format, and integrate character
profiles into the generation process.
"""

import os
import glob
from typing import Dict, List, Optional, Union

import config

def load_text_file(file_path: str) -> str:
    """
    Load text content from a file.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        The text content of the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {e}")

def list_available_characters() -> List[str]:
    """
    List all available character profile names.
    
    Returns:
        List of character names (without file extensions).
    """
    character_files = glob.glob(os.path.join(config.CHARACTERS_DIR, "*.md"))
    return [os.path.splitext(os.path.basename(f))[0] for f in character_files]

def load_character_profile(character_name: str) -> Optional[str]:
    """
    Load a character profile by name.
    
    Args:
        character_name: Name of the character (filename without extension).
        
    Returns:
        Character profile text or None if not found.
    """
    file_path = os.path.join(config.CHARACTERS_DIR, f"{character_name}.md")
    
    try:
        return load_text_file(file_path)
    except Exception as e:
        print(f"Error loading character profile '{character_name}': {e}")
        return None

def format_character_for_prompt(character_profile: str) -> str:
    """
    Format a character profile for insertion into a prompt.
    
    Args:
        character_profile: Raw character profile text.
        
    Returns:
        Formatted character profile for prompting.
    """
    lines = character_profile.strip().split("\n")
    
    # Extract the character name from the header if available
    character_name = "the character"
    if lines and lines[0].startswith("# "):
        character_name = lines[0].replace("# ", "").replace(" Character Profile", "").strip()
    
    formatted = f"## Character: {character_name}\n\n"
    
    # Process the sections, skipping the title
    current_section = None
    for line in lines[1:]:
        if line.startswith("## "):
            current_section = line.replace("##", "").strip()
            formatted += f"### {current_section}:\n"
        elif line.startswith("- "):
            # Convert bullet points to more compact format
            formatted += f"{line.strip()}\n"
        elif line.strip() and current_section:
            formatted += f"{line.strip()}\n"
    
    return formatted

def integrate_characters_with_prompt(prompt: str, character_names: Union[str, List[str]]) -> str:
    """
    Integrate one or more character profiles into a generation prompt.
    
    Args:
        prompt: Original generation prompt.
        character_names: Character name(s) to include.
        
    Returns:
        Enhanced prompt with character information.
    """
    if isinstance(character_names, str):
        character_names = [character_names]
    
    character_section = "## Characters\n\n"
    
    for name in character_names:
        profile = load_character_profile(name)
        if profile:
            character_section += format_character_for_prompt(profile) + "\n\n"
    
    # Add instruction to use these characters
    usage_guide = (
        "Incorporate these characters into your story, respecting their traits, "
        "background, and mannerisms. You may adapt minor details as needed for "
        "the narrative, but maintain the essential character as described.\n\n"
    )
    
    # Insert the character section between the persona and the story prompt
    if "Write a Victorian-era" in prompt:
        parts = prompt.split("Write a Victorian-era", 1)
        enhanced_prompt = parts[0] + character_section + usage_guide + "Write a Victorian-era" + parts[1]
    else:
        # If we can't find the expected marker, append to the end
        enhanced_prompt = prompt + "\n\n" + character_section + usage_guide
    
    return enhanced_prompt
