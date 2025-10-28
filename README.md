# TimeCapsuleWriter

A minimal Python project that uses a Hugging Face causal language model to generate Victorian-era prose in the style of 19th-century British authors.

## Features

- **Simple generation**: Just prose generation, no training required
- **Default model**: Uses "haykgrigo3/TimeCapsuleLLM" from Hugging Face (easily swappable)
- **Victorian persona**: Includes detailed Victorian-era literary style guidelines
- **Multiple generation modes**:
  - Single-pass story from seed scene
  - Beat-by-beat generation from YAML outline
  - Auto-generation of outline from a simple logline

## Quick Start

1. Set up a virtual environment:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the generator:

```bash
# Generate a basic story with a specific random seed
python main.py --seed 42

# Generate a story from the included outline file
python main.py --outline_file beats.yaml

# Generate a story from a logline
python main.py --logline "A conscientious clerk in fogbound London must deliver a perilous parcel."
```

## Generation Modes

### Single-pass Story Generation

This mode generates a complete story in one pass, using the Victorian persona and a seed scene:

```bash
python main.py
```

### Beat-by-beat Story Generation

This mode breaks the story into narrative beats, generating each section separately:

1. **From a YAML outline file:**

```bash
python main.py --outline_file beats.yaml
```

2. **From a logline:**

```bash
python main.py --logline "A young governess arrives at a remote estate and discovers her ward is hiding a supernatural secret."
```

## Customization Options

### Using a Different Model

If the default model is too large or slow for your CPU, you can easily swap to a smaller model:

```bash
# Example: Use Phi-3-mini-4k
python main.py --model "microsoft/phi-3-mini-4k-instruct" --seed 42

# Example: Use Mistral-7B
python main.py --model "mistralai/Mistral-7B-Instruct-v0.2" --seed 42
```

### Generation Parameters

Adjust the generation parameters to control the output:

```bash
python main.py --temperature 0.7 --max_new_tokens 600
```

Available parameters:
- `--max_new_tokens`: Maximum length of generated text (default: 450)
- `--temperature`: Controls randomness (default: 0.9, lower = more deterministic)
- `--top_p`: Nucleus sampling parameter (default: 0.95)
- `--repetition_penalty`: Prevents repetition (default: 1.1)
- `--seed`: Random seed for reproducibility

## Project Structure

- `main.py`: Main script with CLI interface
- `config.py`: Configuration settings
- `outline_utils.py`: Utilities for working with beat outlines
- `prompts/`: Directory containing prompt templates
  - `persona_victorian.md`: Victorian literary persona instructions
  - `seed_scene.txt`: Default seed scene for single-pass generation
  - `outline_instructions.md`: Instructions for beat planning
- `beats.yaml`: Example story outline
- `outputs/`: Directory where generated stories are saved

## Note

This project uses transformers and PyTorch to run generation locally on your machine. While Cursor's Claude Agent helped create this code, the actual text generation runs on your local hardware using the specified Hugging Face model.

## License

This project is open source and available under the MIT License.
