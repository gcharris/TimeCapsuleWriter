# Model Selection Guide

When using TimeCapsuleWriter, selecting the right model version is crucial for balancing quality against performance on your hardware. Here are recommendations for choosing the appropriate model version:

## Recommended Strategy

1. **Try v1 first** (`haykgrigo3/TimeCapsuleLLM`) 
   - Full version with best Victorian-style prose generation
   - Ideal if your hardware can handle it
   - Use for final, publication-quality generations

2. **If performance issues occur, fallback to v0.5** (`haykgrigo3/TimeCapsuleLLM-medium`)
   - Good balance of quality and performance
   - Still produces solid Victorian-style text
   - Suitable for most short-story work with reasonable performance

3. **Reserve v0 for constrained situations** (`haykgrigo3/TimeCapsuleLLM-small`)
   - Lightweight option for drafting or testing
   - Use on very constrained hardware
   - Acceptable for initial outlines and rough drafts

## Usage Examples

```bash
# Full version (default)
python main.py --seed 42

# Medium version
python main.py --seed 42 --model "haykgrigo3/TimeCapsuleLLM-medium"

# Small version
python main.py --seed 42 --model "haykgrigo3/TimeCapsuleLLM-small"
```

## Other Model Alternatives

If the TimeCapsuleLLM models don't work for your use case, consider these alternatives:

- **Phi-3-mini** (`microsoft/phi-3-mini-4k-instruct`) - Good lightweight alternative
- **Mistral-7B** (`mistralai/Mistral-7B-Instruct-v0.2`) - Larger but potentially higher quality

## Benchmarking

You can use the benchmarking tool to compare model performance on your hardware:

```bash
python bench_models.py --models haykgrigo3/TimeCapsuleLLM haykgrigo3/TimeCapsuleLLM-medium haykgrigo3/TimeCapsuleLLM-small
```

This will provide metrics on generation speed, memory usage, and Victorian-style quality to help you make an informed choice.
