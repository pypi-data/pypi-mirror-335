"""Tests for the visualize_infestation function."""

import os
import pytest

from ratpack.infest import visualize_infestation
from tests.conftest import create_test_rats, create_test_rat


def test_text_output_format(temp_test_dir, clean_registry):
    """Test 4.1: Verify that visualize_infestation() with output_format="text" produces correct output."""
    # Create a controlled set of rats
    rat_count = 5
    create_test_rats(temp_test_dir, count=rat_count)
    
    # Get the text visualization
    visualization = visualize_infestation(temp_test_dir, output_format="text")
    
    # Verify the visualization contains expected information
    assert "Rat Infestation Report" in visualization
    assert f"Total rats: {rat_count}" in visualization
    assert "Rats by type" in visualization
    
    # Verify that the text format doesn't contain ASCII art
    assert "**" not in visualization
    assert "```" not in visualization


def test_ascii_output_format(temp_test_dir, clean_registry):
    """Test 4.2: Verify that visualize_infestation() with output_format="ascii" produces correct output."""
    # Create a controlled set of rats
    rat_count = 5
    create_test_rats(temp_test_dir, count=rat_count)
    
    # Get the ASCII visualization
    visualization = visualize_infestation(temp_test_dir, output_format="ascii")
    
    # Verify the visualization contains expected information
    assert "RAT INFESTATION ALERT" in visualization
    assert f"Total rats: {rat_count}" in visualization
    
    # Verify that ASCII art is included
    assert "⁐̤ᕐᐷ" in visualization  # Eyes in ASCII rat art
    assert "ᘛ" in visualization   # Part of ASCII rat art
    

def test_empty_infestation(temp_test_dir, clean_registry):
    """Test 4.3: Verify behavior when no rats exist."""
    # Ensure no rats exist in the directory
    # (the clean_registry fixture and temporary directory should ensure this)
    
    # Get the visualization
    visualization = visualize_infestation(temp_test_dir)
    
    # Verify the output indicates no infestation
    assert "No rats found" in visualization
    assert "clean" in visualization.lower()
    
    # Verify that stats are not included
    assert "Total rats:" not in visualization


def test_different_infestation_levels(temp_test_dir, clean_registry):
    """Test 4.4: Verify that different infestation levels produce appropriate output."""
    # Test for low infestation level (1-5 rats)
    low_count = 3
    create_test_rats(temp_test_dir, count=low_count)
    low_viz = visualize_infestation(temp_test_dir, output_format="ascii")
    
    # Clear rats for next test
    for rat_file in os.listdir(temp_test_dir):
        if rat_file.endswith(".rat"):
            os.remove(os.path.join(temp_test_dir, rat_file))
    
    # Clean burrows
    for item in os.listdir(temp_test_dir):
        if os.path.isdir(os.path.join(temp_test_dir, item)) and "rat_burrow" in item:
            for rat_file in os.listdir(os.path.join(temp_test_dir, item)):
                os.remove(os.path.join(temp_test_dir, item, rat_file))
            os.rmdir(os.path.join(temp_test_dir, item))
    
    # Test for medium infestation level (6-15 rats)
    medium_count = 10
    create_test_rats(temp_test_dir, count=medium_count)
    medium_viz = visualize_infestation(temp_test_dir, output_format="ascii")
    
    # Clear rats for next test
    for rat_file in os.listdir(temp_test_dir):
        if rat_file.endswith(".rat"):
            os.remove(os.path.join(temp_test_dir, rat_file))
    
    # Clean burrows
    for item in os.listdir(temp_test_dir):
        if os.path.isdir(os.path.join(temp_test_dir, item)) and "rat_burrow" in item:
            for rat_file in os.listdir(os.path.join(temp_test_dir, item)):
                os.remove(os.path.join(temp_test_dir, item, rat_file))
            os.rmdir(os.path.join(temp_test_dir, item))
    
    # Test for high infestation level (16+ rats)
    high_count = 20
    create_test_rats(temp_test_dir, count=high_count)
    high_viz = visualize_infestation(temp_test_dir, output_format="ascii")
    
    # Verify different infestation levels produce different visualizations
    assert low_viz != medium_viz
    assert medium_viz != high_viz
    assert low_viz != high_viz
    
    # Check that rat counts are correctly reflected
    assert f"Total rats: {low_count}" in low_viz
    assert f"Total rats: {medium_count}" in medium_viz
    assert f"Total rats: {high_count}" in high_viz 