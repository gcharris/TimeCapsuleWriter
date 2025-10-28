# Character Profiles in TimeCapsuleWriter

Character profiles provide a way to enhance your generated stories with consistent, well-defined characters. This document explains how to use and create character profiles.

## Using Character Profiles

Character profiles can be used with any generation mode by adding the `--characters` argument:

```bash
# Single-pass generation with a clerk character
python main.py --characters clerk

# Beat-by-beat generation with multiple characters
python main.py --outline_file beats.yaml --characters clerk governess

# Logline generation with a character
python main.py --logline "A mystery unfolds in London" --characters governess
```

To see all available character profiles:

```bash
python main.py --list_characters
```

## How Character Profiles Work

When you include character profiles:

1. The specified profiles are loaded from the `prompts/characters/` directory
2. The profiles are formatted into a concise format suitable for prompting
3. The formatted profiles are integrated into the generation prompt
4. The model is instructed to incorporate these characters into the story

Character profiles are only injected into the prompt once (for single-pass stories) or at the beginning of each beat (for beat-by-beat stories), ensuring that the character details remain consistent throughout the narrative.

## Creating Custom Character Profiles

You can create your own character profiles by adding Markdown files to the `prompts/characters/` directory. Each profile should follow this structure:

```markdown
# Character Name Character Profile

## Basic Information
- Name: [Full name]
- Age: [Age]
- Occupation: [Job or role]
- Class: [Social class]

## Physical Appearance
- [Description of appearance]
- [Notable features]
- [Clothing style]

## Speech and Mannerisms
- [How they speak]
- [Characteristic gestures or habits]
- [Verbal tics or patterns]

## Character Traits
- [Key personality traits]
- [Strengths]
- [Weaknesses]

## Background
- [Relevant history]
- [Education]
- [Formative experiences]

## Relationships
- [Family connections]
- [Friends or allies]
- [Enemies or rivals]

## Worldview
- [Beliefs or values]
- [Political or religious views]
- [Aspirations]

## Conflicts and Motivations
- [Internal conflicts]
- [External conflicts]
- [Primary motivations]
```

### Tips for Effective Character Profiles

1. **Be Specific**: Include concrete details rather than abstract qualities
2. **Stay Period-Appropriate**: Ensure all details are consistent with Victorian era (1855-1875)
3. **Include Flaws**: Well-rounded characters have weaknesses and conflicts
4. **Consider Class Context**: Victorian society was highly stratified by class
5. **Add Distinctive Features**: Give each character memorable traits that distinguish them

## Example Usage

Here's an example of how character profiles enhance generation:

```
# Without character profile
python main.py --seed 42

# With character profile
python main.py --seed 42 --characters clerk
```

The second command will produce a story that incorporates the clerk character, with consistent traits, background, and mannerisms as defined in the profile.
