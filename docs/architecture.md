# TimeCapsuleWriter Architecture

This document provides an overview of the architecture and design principles of TimeCapsuleWriter.

## Overview

TimeCapsuleWriter is a Python application that uses Hugging Face causal language models to generate Victorian-era prose. The application supports multiple generation modes and is designed to be modular, extensible, and CPU-friendly.

## Core Components

### 1. Configuration (`config.py`)

- Contains all configuration constants and defaults
- Single source of truth for model IDs, generation parameters, and file paths
- Designed for easy modification to swap models or adjust generation parameters

### 2. Core Generation (`main.py`)

- Provides the command-line interface
- Handles setup of the generation pipeline
- Orchestrates the different generation modes
- Manages file input/output operations

### 3. Outline Utilities (`outline_utils.py`)

- Handles YAML outline parsing and processing
- Formats beats for prompts
- Manages continuation between beats for coherent storytelling
- Provides utilities for generating beat prompts

### 4. Benchmarking (`bench_models.py`)

- Tests different models side-by-side
- Measures performance metrics (speed, memory usage)
- Evaluates output quality with basic style metrics
- Saves benchmark results for comparison

### 5. Sample Collection (`snapshot.py`)

- Maintains an organized collection of sample outputs
- Supports both saving existing outputs and generating new ones
- Follows consistent naming conventions for samples

## Data Flow

1. **Single-pass generation**:
   ```
   User Input → Load Model → Generate Text → Save Output
   ```

2. **Beat-by-beat generation**:
   ```
   Load Outline → Process Beat 1 → Generate Text → 
   Extract Continuation → Process Beat 2 → ... →
   Merge Beats → Save Complete Story
   ```

3. **Logline generation**:
   ```
   Logline → Generate Outline → Save Outline →
   Follow Beat-by-beat Generation Flow
   ```

## Extension Points

The architecture is designed with several extension points:

1. **New Generation Modes**: Add new modes by extending the main generation flow
2. **Custom Models**: Change the model by updating the MODEL_ID in config.py
3. **Alternative Prompts**: Add new persona or instruction files in the prompts directory
4. **Output Processing**: Add post-processing to enhance or modify the generated text
5. **Character Profiles**: Incorporate character profiles as additional context for generation

## Directory Structure

- `/`: Root directory with main Python files and configuration
- `/prompts/`: Contains prompt templates and instructions
- `/samples/`: Organized collection of sample outputs
- `/outputs/`: Working directory for generated content
- `/tests/`: Test suite
- `/docs/`: Documentation
- `/.github/`: GitHub-related files (workflows, templates)

## Testing Strategy

The project uses pytest for testing. Tests are structured to cover:

1. Unit tests for individual utility functions
2. Integration tests for end-to-end flows
3. Parametrized tests for different inputs and configurations

## Future Directions

Potential areas for enhancement include:

1. More sophisticated quality evaluation metrics
2. Web interface for story generation
3. Fine-tuning capabilities for custom models
4. Integration with external APIs for image generation or audio narration
5. Advanced storytelling features like character arcs and plot development
