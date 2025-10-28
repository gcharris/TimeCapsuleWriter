#!/usr/bin/env python3
"""
TimeCapsuleWriter - Victorian-style story generator using Hugging Face models
"""

import os
import argparse
import yaml
import time
import random
import torch
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

import config
from outline_utils import (
    load_yaml_outline, 
    format_story_context, 
    get_continuation_text,
    generate_beat_prompts
)
from character_utils import (
    list_available_characters,
    integrate_characters_with_prompt
)

def setup_generator(args, trust_remote_code: bool = False):
    """
    Set up the text generation pipeline.
    
    Args:
        args: Command line arguments.
    
    Returns:
        The text generation pipeline.
    """
    model_id = args.model or config.MODEL_ID
    print(f"Loading model: {model_id}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_remote_code)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=trust_remote_code,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        low_cpu_mem_usage=True
    )
    
    # Set up the generation parameters
    gen_kwargs = {
        "max_new_tokens": args.max_new_tokens or config.DEFAULTS["max_new_tokens"],
        "temperature": args.temperature or config.DEFAULTS["temperature"],
        "top_p": args.top_p or config.DEFAULTS["top_p"],
        "repetition_penalty": args.repetition_penalty or config.DEFAULTS["repetition_penalty"],
        "do_sample": True
    }
    
    # Add seed if provided
    if args.seed is not None:
        print(f"Using seed: {args.seed}")
        torch.manual_seed(args.seed)
        random.seed(args.seed)
        # Remove direct seed from gen_kwargs as some models don't support it
        # The torch and random seeds should still provide determinism
    
    # Create the generator
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        **gen_kwargs
    )
    
    return generator

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

def ensure_dir_exists(directory: str):
    """Ensure the specified directory exists."""
    os.makedirs(directory, exist_ok=True)

def save_output(text: str, filename: str, output_dir: str = config.OUTPUTS_DIR):
    """
    Save the generated text to a file with timestamp.
    
    Args:
        text: The text to save.
        filename: Base name for the output file.
        output_dir: Directory to save the file in.
    
    Returns:
        The path to the saved file.
    """
    ensure_dir_exists(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_filename = filename.replace(" ", "_").replace(",", "").replace(".", "").lower()
    output_path = os.path.join(output_dir, f"{clean_filename}_{timestamp}.txt")
    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)
    
    print(f"Saved output to: {output_path}")
    return output_path

def generate_from_logline(generator, logline: str, outline_instructions: str):
    """
    Generate a story outline from a logline.
    
    Args:
        generator: The text generation pipeline.
        logline: The story logline.
        outline_instructions: The outline instructions text.
        
    Returns:
        The generated outline as a YAML string.
    """
    prompt = f"{outline_instructions}\n\nLogline: \"{logline}\"\n\nGenerate a complete story outline in YAML format:"
    
    response = generator(prompt, return_full_text=False)[0]['generated_text']
    
    # Ensure the response is valid YAML
    try:
        # Try to parse as YAML
        yaml.safe_load(response)
        return response
    except Exception as e:
        print(f"Error parsing generated outline as YAML: {e}")
        print("Trying to clean up the response...")
        
        # Try to extract just the YAML portion
        if "```yaml" in response:
            yaml_part = response.split("```yaml")[1]
            if "```" in yaml_part:
                yaml_part = yaml_part.split("```")[0]
            
            # Try to parse again
            try:
                yaml.safe_load(yaml_part)
                return yaml_part
            except:
                print("Failed to extract valid YAML from response.")
        
        # If we can't get valid YAML, create a basic outline based on the logline
        print("Creating a default YAML outline from the logline")
        title = logline.split('.')[0].strip()
        if 'in' in logline:
            setting = logline.split('in')[1].split('must')[0].strip()
        else:
            setting = "London, 1865"
            
        if 'must' in logline:
            challenge = logline.split('must')[1].strip().rstrip('.')
        else:
            challenge = "complete an important task"
            
        if 'A' in logline and ' ' in logline:
            protagonist = logline.split('A')[1].split('in')[0].strip()
        else:
            protagonist = "diligent clerk"
            
        # Create a simple YAML outline
        default_outline = f"""title: "{title}"
setting: "{setting}"
protagonist: "A {protagonist}"
beats:
  - name: "Setup"
    description: "Establish the protagonist and their normal life"
    key_elements:
      - "Introduce the {protagonist} and their daily routine"
      - "Show the setting of {setting}"
      - "Introduce the task to {challenge}"
  
  - name: "Complication"
    description: "The protagonist faces initial obstacles"
    key_elements:
      - "The {protagonist} begins to {challenge}"
      - "Unexpected difficulties arise"
      - "The stakes become clear"
  
  - name: "Turn"
    description: "The protagonist confronts the main challenge"
    key_elements:
      - "The situation becomes more dangerous"
      - "The {protagonist} must make a crucial decision"
      - "A revelation changes the protagonist's understanding"
  
  - name: "Resolution"
    description: "The story reaches its conclusion"
    key_elements:
      - "The {protagonist} completes or fails their mission"
      - "The consequences of their actions become clear"
      - "The protagonist is changed by the experience"
"""
        # Try to parse this default outline
        try:
            yaml.safe_load(default_outline)
            return default_outline
        except:
            print("Failed to create valid default YAML outline.")
        
        # Return the original response as a last resort
        return response

def generate_single_story(generator, persona: str, seed_scene: str, args):
    """
    Generate a single story from persona and seed scene.
    
    Args:
        generator: The text generation pipeline.
        persona: The persona prompt text.
        seed_scene: The seed scene text.
        args: Command line arguments.
        
    Returns:
        The generated story text.
    """
    prompt = f"{persona}\n\nWrite a Victorian-era short story that begins with the following scene:\n\n{seed_scene}"
    
    # Add character profiles if specified
    if args.characters:
        print(f"Incorporating character profiles: {', '.join(args.characters)}")
        prompt = integrate_characters_with_prompt(prompt, args.characters)
    
    print("Generating story...")
    response = generator(prompt, return_full_text=False)[0]['generated_text']
    
    # Save the output
    output_path = save_output(
        response, 
        filename="Victorian_Story", 
        output_dir=config.OUTPUTS_DIR
    )
    
    return response

def generate_beat_story(generator, outline_path: str, persona: str, args):
    """
    Generate a story by beats from an outline.
    
    Args:
        generator: The text generation pipeline.
        outline_path: Path to the YAML outline file.
        persona: The persona prompt text.
        args: Command line arguments.
        
    Returns:
        A dictionary with individual beats and the complete story.
    """
    outline = load_yaml_outline(outline_path)
    title = outline["title"]
    beats = outline["beats"]
    
    print(f"Generating story '{title}' with {len(beats)} beats...")
    
    # Create a directory for this story
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_title = title.replace(" ", "_").replace(",", "").replace(".", "").lower()
    story_dir = os.path.join(config.OUTPUTS_DIR, f"{clean_title}_{timestamp}")
    ensure_dir_exists(story_dir)
    
    # Generate each beat
    beat_texts = []
    previous_text = None
    
    for i, beat in enumerate(beats):
        beat_name = beat["name"]
        print(f"Generating beat {i+1}/{len(beats)}: {beat_name}...")
        
        # Format the context for this beat
        context = format_story_context(outline, i, previous_text)
        prompt = f"{persona}\n\n{context}\n\nContinue the story from here:"
        
        # Add character profiles if specified
        if args.characters:
            # Only mention for the first beat to avoid repetition
            if i == 0:
                print(f"Incorporating character profiles: {', '.join(args.characters)}")
            prompt = integrate_characters_with_prompt(prompt, args.characters)
        
        # Generate the text
        response = generator(prompt, return_full_text=False)[0]['generated_text']
        beat_texts.append(response)
        
        # Save the individual beat
        beat_filename = f"{i+1:02d}_{beat_name.replace(' ', '_').lower()}"
        beat_path = os.path.join(story_dir, f"{beat_filename}.txt")
        with open(beat_path, 'w', encoding='utf-8') as file:
            file.write(response)
        
        # Get continuation text for the next beat
        previous_text = get_continuation_text(response)
    
    # Combine all beats into a complete story
    complete_story = "\n\n".join(beat_texts)
    
    # Save the complete story
    story_path = os.path.join(story_dir, "complete_story.txt")
    with open(story_path, 'w', encoding='utf-8') as file:
        file.write(complete_story)
    
    print(f"Story generation complete. Saved to: {story_dir}")
    
    return {
        "beats": beat_texts,
        "complete_story": complete_story,
        "output_dir": story_dir
    }

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="TimeCapsuleWriter - Victorian-style story generator")
    
    # Model parameters
    parser.add_argument("--model", help="Hugging Face model ID to use")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    
    # Generation parameters
    parser.add_argument("--max_new_tokens", type=int, help="Maximum number of new tokens to generate")
    parser.add_argument("--temperature", type=float, help="Sampling temperature")
    parser.add_argument("--top_p", type=float, help="Top-p sampling parameter")
    parser.add_argument("--repetition_penalty", type=float, help="Repetition penalty")
    
    # Input files
    parser.add_argument("--persona", help="Path to persona prompt file", default=os.path.join(config.PROMPTS_DIR, "persona_victorian.md"))
    parser.add_argument("--seed_scene", help="Path to seed scene file", default=os.path.join(config.PROMPTS_DIR, "seed_scene.txt"))
    
    # Beat generation options
    parser.add_argument("--outline_file", help="Path to YAML outline file")
    parser.add_argument("--logline", help="Logline to generate a story from")
    
    # Character profiles
    parser.add_argument("--characters", nargs="+", help="Character profiles to include (e.g., clerk, governess)")
    parser.add_argument("--list_characters", action="store_true", help="List available character profiles and exit")
    
    args = parser.parse_args()
    
    # If requested, list available characters and exit
    if args.list_characters:
        characters = list_available_characters()
        print("Available character profiles:")
        for character in sorted(characters):
            print(f"  - {character}")
        return
    
    # Load the persona and seed scene
    persona = load_text_file(args.persona)
    seed_scene = load_text_file(args.seed_scene)
    
    # Set up the generator
    generator = setup_generator(args)
    
    # Determine the generation mode
    if args.logline:
        print(f"Generating outline from logline: {args.logline}")
        outline_instructions = load_text_file(os.path.join(config.PROMPTS_DIR, "outline_instructions.md"))
        outline_yaml = generate_from_logline(generator, args.logline, outline_instructions)
        
        # Save the generated outline
        outline_path = save_output(outline_yaml, "generated_outline", config.OUTPUTS_DIR)
        
        # Generate the story from the outline
        result = generate_beat_story(generator, outline_path, persona, args)
    
    elif args.outline_file:
        print(f"Generating story from outline: {args.outline_file}")
        result = generate_beat_story(generator, args.outline_file, persona, args)
    
    else:
        print("Generating single-pass story from seed scene")
        result = generate_single_story(generator, persona, seed_scene, args)
    
    print("Generation complete!")

if __name__ == "__main__":
    main()
