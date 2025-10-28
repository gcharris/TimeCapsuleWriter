"""
Tests for snapshot.py module
"""

import os
import pytest
import shutil
from pathlib import Path
import sys

# Import functions from snapshot.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from snapshot import save_existing_output, MODE_DIRS

@pytest.fixture
def setup_sample_dirs(tmpdir):
    """Set up sample directories for testing."""
    # Create base samples directory
    samples_dir = tmpdir.mkdir("samples")
    
    # Create mode subdirectories
    for mode_dir in MODE_DIRS.values():
        samples_dir.mkdir(mode_dir)
    
    # Create a sample output file
    output_file = tmpdir.join("test_output.txt")
    with open(output_file, 'w') as f:
        f.write("This is a test story output.")
    
    return {
        "samples_dir": str(samples_dir),
        "output_file": str(output_file)
    }

def test_save_existing_output(setup_sample_dirs, monkeypatch):
    """Test saving an existing output file as a sample."""
    # Mock the current directory to be the tmpdir
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(setup_sample_dirs["samples_dir"]))
    
    # Create a namespace object to simulate args
    class Args:
        def __init__(self):
            self.input = setup_sample_dirs["output_file"]
            self.model = "TestModel"
            self.mode = "single"
            self.seed = 42
    
    # Call the function
    try:
        save_existing_output(Args())
        
        # Check that the file was copied with the right name
        expected_dir = os.path.join("samples", MODE_DIRS["single"])
        files = os.listdir(expected_dir)
        
        assert any(f.startswith("TestModel_single_42_") for f in files)
        
        # Check content was preserved
        sample_file = [os.path.join(expected_dir, f) for f in files if f.startswith("TestModel_single_42_")][0]
        with open(sample_file, 'r') as f:
            content = f.read()
        assert content == "This is a test story output."
        
    finally:
        # Restore original directory
        os.chdir(original_dir)
