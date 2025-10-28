"""
Pytest configuration file with fixtures and setup.
"""

import os
import sys
import pytest

# Add parent directory to path to allow importing from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_outline():
    """Provide a sample outline dictionary for testing."""
    return {
        "title": "Test Story",
        "setting": "Victorian London",
        "protagonist": "A determined clerk",
        "beats": [
            {
                "name": "Setup",
                "description": "Introduce the protagonist and setting",
                "key_elements": [
                    "Element 1",
                    "Element 2",
                    "Element 3"
                ]
            },
            {
                "name": "Complication",
                "description": "Introduce the central conflict",
                "key_elements": [
                    "Element 1",
                    "Element 2",
                    "Element 3"
                ]
            }
        ]
    }

@pytest.fixture
def temp_output_dir(tmpdir):
    """Create a temporary output directory for testing."""
    output_dir = tmpdir.mkdir("outputs")
    return str(output_dir)

@pytest.fixture
def temp_yaml_file(tmpdir, sample_outline):
    """Create a temporary YAML file with the sample outline."""
    import yaml
    yaml_file = tmpdir.join("test_outline.yaml")
    with open(yaml_file, 'w') as f:
        yaml.dump(sample_outline, f)
    return str(yaml_file)
