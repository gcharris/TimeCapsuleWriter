"""
Utilities for parsing YAML outlines and preparing prompts.
"""

import os
import yaml
from typing import Dict, List, Any, Optional

def load_yaml_outline(file_path: str) -> Dict[str, Any]:
    """
    Load a YAML outline file.
    
    Args:
        file_path: Path to the YAML outline file.
        
    Returns:
        Dict containing the parsed YAML content.
    """
    try:
        with open(file_path, 'r') as file:
            outline = yaml.safe_load(file)
        return outline
    except Exception as e:
        raise ValueError(f"Error loading YAML outline: {e}")

def format_beat_for_prompt(beat: Dict[str, Any]) -> str:
    """
    Format a single beat into a prompt-ready text block.
    
    Args:
        beat: Dictionary containing beat information.
        
    Returns:
        Formatted string for the beat.
    """
    formatted = f"# {beat['name']}\n\n"
    formatted += f"{beat['description']}\n\n"
    formatted += "Key elements:\n"
    
    for element in beat['key_elements']:
        formatted += f"- {element}\n"
    
    return formatted

def format_story_context(outline: Dict[str, Any], current_beat_idx: int, 
                         previous_text: Optional[str] = None) -> str:
    """
    Format the story context for prompting the model.
    
    Args:
        outline: The complete story outline.
        current_beat_idx: Index of the current beat to generate.
        previous_text: Optional text from previous beats to maintain continuity.
        
    Returns:
        Formatted context string for prompting.
    """
    context = f"# {outline['title']}\n\n"
    context += f"Setting: {outline['setting']}\n"
    context += f"Protagonist: {outline['protagonist']}\n\n"
    
    # Add summary of previous beats
    if current_beat_idx > 0:
        context += "## Previous events:\n"
        for i in range(current_beat_idx):
            context += f"- {outline['beats'][i]['description']}\n"
        context += "\n"
    
    # Add the current beat instructions
    context += "## Current section to write:\n"
    context += format_beat_for_prompt(outline['beats'][current_beat_idx])
    
    # Add previous text if available
    if previous_text:
        context += "\n## Previous text (continue from here):\n"
        context += previous_text
    
    return context

def get_continuation_text(text: str, chars: int = 120) -> str:
    """
    Extract the last portion of generated text to use as continuation.
    
    Args:
        text: The full text of the previous section.
        chars: Number of characters to extract (default 120).
        
    Returns:
        The last portion of the text.
    """
    if len(text) <= chars:
        return text
    
    # Try to find a sentence break near the target length
    start_pos = len(text) - chars
    sentence_breaks = ['.', '!', '?']
    
    # Find the nearest sentence break after start_pos
    for i in range(start_pos, len(text)):
        if text[i] in sentence_breaks and (i + 1 >= len(text) or text[i+1].isspace()):
            start_pos = i + 1
            break
    
    return text[start_pos:].strip()

def generate_beat_prompts(outline_path: str) -> List[str]:
    """
    Generate a list of prompts for each beat in the outline.
    
    Args:
        outline_path: Path to the YAML outline file.
        
    Returns:
        List of formatted prompts, one for each beat.
    """
    outline = load_yaml_outline(outline_path)
    prompts = []
    
    for i in range(len(outline['beats'])):
        prompt = format_story_context(outline, i)
        prompts.append(prompt)
    
    return prompts
