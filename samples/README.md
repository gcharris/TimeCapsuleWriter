# Sample Outputs

This directory contains sample outputs from different models and generation modes in TimeCapsuleWriter.

## Directory Structure

- **single_pass/**: Stories generated in single-pass mode
- **beat_by_beat/**: Stories generated using the beat-by-beat approach
- **logline/**: Stories generated from loglines

## Naming Convention

Files follow this naming convention:

```
{model}_{mode}_{seed}_{date}.txt
```

For example:
- `TimeCapsuleLLM_single_42_20251028.txt`: Single-pass generation with TimeCapsuleLLM using seed 42
- `Phi3Mini_beats_123_20251030.txt`: Beat-by-beat generation with Phi-3-mini using seed 123
- `Mistral7B_logline_456_20251101.txt`: Logline-to-story generation with Mistral-7B using seed 456

## Sample Collection

Use the `snapshot.py` script to easily save your generated stories to the appropriate sample directory:

```bash
# Save a previously generated story
python snapshot.py --input outputs/victorian_story_20251028_155517.txt --model "TimeCapsuleLLM" --mode "single" --seed 42

# Generate and save a new story
python snapshot.py --generate --model "Phi3Mini" --mode "beats" --seed 123 --outline_file beats.yaml
```
