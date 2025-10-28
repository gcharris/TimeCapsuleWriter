# Model Comparison Tool

The model comparison tool allows you to generate the same story with multiple models and save the results in markdown format for easy comparison.

## Usage

```bash
# Basic usage with default models
python model_comparison.py --prompt "A clerk discovers a mysterious letter"

# Compare specific models
python model_comparison.py --models haykgrigo3/TimeCapsuleLLM microsoft/phi-3-mini-4k-instruct

# Use a specific seed for reproducibility
python model_comparison.py --seed 42 --prompt "A ghost story set in Yorkshire"

# Add character profiles
python model_comparison.py --characters clerk --prompt "A mysterious package arrives"

# Save to a specific directory
python model_comparison.py --output_dir custom_comparisons/test1
```

## Output

The tool creates the following files in the output directory (default: `comparisons/`):

1. **Individual model files**: One markdown file per model with:
   - Story metadata
   - Performance metrics
   - The generated text

2. **Comparison summary**: A markdown file with:
   - Side-by-side metrics comparison
   - Links to individual model outputs

## Available Options

| Option | Description |
|--------|-------------|
| `--models` | Space-separated list of models to compare |
| `--prompt` | Story concept or prompt |
| `--title` | Story title (defaults to prompt if not provided) |
| `--persona` | Path to persona prompt file |
| `--characters` | Space-separated list of character profiles to include |
| `--seed` | Random seed for reproducibility |
| `--max_new_tokens` | Maximum number of tokens to generate (default: 450) |
| `--output_dir` | Directory to save comparison results (default: "comparisons") |

## Metrics

The tool collects the following metrics for each model:

- **Generation time**: Time taken to generate the story (seconds)
- **Memory used**: Additional memory used during generation (MB)
- **Tokens per second**: Generation speed
- **Victorian term count**: Number of Victorian-era terms used
- **Word count**: Total words in the generated story
- **Average word length**: For style analysis
- **Sentence count**: Number of sentences
- **Average sentence length**: For style analysis

## Examples

### Comparing Model Versions

```bash
# Compare different versions of TimeCapsuleLLM
python model_comparison.py --models haykgrigo3/TimeCapsuleLLM haykgrigo3/TimeCapsuleLLM-medium haykgrigo3/TimeCapsuleLLM-small
```

### Using Character Profiles with Multiple Models

```bash
# Compare how different models handle the same character profile
python model_comparison.py --models haykgrigo3/TimeCapsuleLLM microsoft/phi-3-mini-4k-instruct --characters governess --prompt "A mysterious figure appears at the manor window"
```

## Integration with Other Tools

The model comparison tool works well with other TimeCapsuleWriter tools:

- Use `bench_models.py` for detailed performance benchmarking
- Use `snapshot.py` to save selected outputs to the samples directory
