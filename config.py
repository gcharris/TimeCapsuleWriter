"""
Configuration settings for the TimeCapsuleWriter.
"""

# The Hugging Face model ID to use for generation
# Can be easily changed to another compatible model
MODEL_ID = "haykgrigo3/TimeCapsuleLLM"

# Default generation parameters
DEFAULTS = {
    "max_new_tokens": 450, 
    "temperature": 0.9, 
    "top_p": 0.95,
    "repetition_penalty": 1.1
}

# Paths
PROMPTS_DIR = "prompts"
OUTPUTS_DIR = "outputs"
CHARACTERS_DIR = "prompts/characters"
