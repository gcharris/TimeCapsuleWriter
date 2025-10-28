#!/usr/bin/env python3
"""
Snapshot Tool for TimeCapsuleWriter

This script helps maintain a collection of sample outputs from different models and modes.
It can either copy existing output files to the samples directory with proper naming,
or generate new stories and save them directly as samples.

Usage:
    # Save an existing output file as a sample
    python snapshot.py --input outputs/victorian_story_20251028_155517.txt --model "TimeCapsuleLLM" --mode "single" --seed 42
    
    # Generate and save a new single-pass story
    python snapshot.py --generate --model "Phi3Mini" --mode "single" --seed 123
    
    # Generate and save a new beat-by-beat story
    python snapshot.py --generate --model "Mistral7B" --mode "beats" --seed 456 --outline_file beats.yaml
    
    # Generate and save a new logline-to-story
    python snapshot.py --generate --model "TimeCapsuleLLM" --mode "logline" --seed 789 --logline "A ghost haunts an abandoned factory"
"""

import os
import sys
import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Supported modes
VALID_MODES = ["single", "beats", "logline"]

# Directory to story mode mapping
MODE_DIRS = {
    "single": "single_pass",
    "beats": "beat_by_beat",
    "logline": "logline"
}

def save_existing_output(args):
    """
    Save an existing output file as a properly named sample.
    
    Args:
        args: Command line arguments with input, model, mode, and seed
    """
    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    
    # Determine target directory
    if args.mode not in MODE_DIRS:
        print(f"Error: Invalid mode '{args.mode}'. Must be one of: {', '.join(VALID_MODES)}")
        sys.exit(1)
    
    target_dir = os.path.join("samples", MODE_DIRS[args.mode])
    
    # Create target filename
    date_str = datetime.now().strftime("%Y%m%d")
    clean_model = args.model.replace("/", "_").replace("-", "")
    target_file = f"{clean_model}_{args.mode}_{args.seed}_{date_str}.txt"
    target_path = os.path.join(target_dir, target_file)
    
    # Copy the file
    try:
        shutil.copy2(args.input, target_path)
        print(f"Successfully saved sample: {target_path}")
    except Exception as e:
        print(f"Error saving sample: {e}")
        sys.exit(1)

def generate_and_save_sample(args):
    """
    Generate a new story and save it as a sample.
    
    Args:
        args: Command line arguments
    """
    # Build the command for main.py
    cmd = ["python", "main.py", "--seed", str(args.seed)]
    
    # Add model if specified
    if args.model:
        clean_model = args.model
        if "/" not in clean_model and not clean_model.startswith(("facebook/", "microsoft/", "mistralai/")):
            # If it's a shorthand name, map it to full name
            model_map = {
                "TimeCapsuleLLM": "haykgrigo3/TimeCapsuleLLM",
                "Phi3Mini": "microsoft/phi-3-mini-4k-instruct",
                "Mistral7B": "mistralai/Mistral-7B-Instruct-v0.2"
            }
            if clean_model in model_map:
                clean_model = model_map[clean_model]
        
        cmd.extend(["--model", clean_model])
    
    # Add mode-specific parameters
    if args.mode == "beats" and args.outline_file:
        cmd.extend(["--outline_file", args.outline_file])
    elif args.mode == "logline" and args.logline:
        cmd.extend(["--logline", args.logline])
    
    # Add any additional parameters
    if args.temperature:
        cmd.extend(["--temperature", str(args.temperature)])
    
    if args.max_new_tokens:
        cmd.extend(["--max_new_tokens", str(args.max_new_tokens)])
    
    # Run the generation
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running generation: {result.stderr}")
        sys.exit(1)
    
    # Find the generated output
    output_line = None
    for line in result.stdout.splitlines():
        if "Saved output to:" in line:
            output_line = line
            break
    
    if not output_line:
        print("Could not find output file in generation output.")
        print("Generation output:")
        print(result.stdout)
        sys.exit(1)
    
    # Extract the output path and save as a sample
    output_file = output_line.split("Saved output to:")[-1].strip()
    
    # Create arguments for saving this output
    save_args = argparse.Namespace(
        input=output_file,
        model=args.model,
        mode=args.mode,
        seed=args.seed
    )
    
    # Save the output as a sample
    save_existing_output(save_args)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Save TimeCapsuleWriter outputs as named samples")
    
    # Main operation mode
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Path to existing output file to save as a sample")
    group.add_argument("--generate", action="store_true", help="Generate a new story and save as a sample")
    
    # Required metadata
    parser.add_argument("--model", required=True, help="Model name (e.g., 'TimeCapsuleLLM', 'Phi3Mini', 'Mistral7B')")
    parser.add_argument("--mode", required=True, choices=VALID_MODES, help="Generation mode")
    parser.add_argument("--seed", required=True, type=int, help="Random seed used for generation")
    
    # Optional generation parameters
    parser.add_argument("--outline_file", help="Path to YAML outline file (for beats mode)")
    parser.add_argument("--logline", help="Logline for story generation (for logline mode)")
    parser.add_argument("--temperature", type=float, help="Temperature for generation")
    parser.add_argument("--max_new_tokens", type=int, help="Maximum tokens to generate")
    
    args = parser.parse_args()
    
    # Ensure samples directory exists
    os.makedirs("samples", exist_ok=True)
    for mode_dir in MODE_DIRS.values():
        os.makedirs(os.path.join("samples", mode_dir), exist_ok=True)
    
    # Process based on chosen operation
    if args.input:
        save_existing_output(args)
    elif args.generate:
        generate_and_save_sample(args)

if __name__ == "__main__":
    main()
