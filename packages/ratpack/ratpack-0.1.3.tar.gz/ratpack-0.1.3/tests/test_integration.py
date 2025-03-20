"""Integration tests for the RatPack package."""

import os
import pytest

from ratpack.infest import infest, count_rats, exterminate, visualize_infestation
from tests.conftest import count_actual_rat_files


def test_full_workflow(temp_test_dir, clean_registry):
    """Test 5.1: Verify the entire workflow from infestation to extermination."""
    # Create a decorated function that will create rats
    @infest(infestation_level=3, rat_types=["sewer_rat", "brown_rat"])
    def create_infestation():
        return "Infestation created"
    
    # Change to the test directory and call the function to create rats
    original_dir = os.getcwd()
    try:
        os.chdir(temp_test_dir)
        
        # Create the infestation
        create_infestation()
        
        # Check the infestation with count_rats
        stats = count_rats(os.getcwd())
        assert stats["total_rats"] > 0
        
        # Visualize the infestation
        visualization = visualize_infestation(os.getcwd())
        assert "Rat Infestation Report" in visualization
        assert f"Total rats: {stats['total_rats']}" in visualization
        
        # Exterminate the rats
        extermination_stats = exterminate(os.getcwd())
        assert extermination_stats["rats_removed"] == stats["total_rats"]
        
        # Verify all rats are gone
        remaining_rats, _ = count_actual_rat_files(os.getcwd())
        assert remaining_rats == 0
        
        # Check that visualization now shows no infestation
        post_extermination_viz = visualize_infestation(os.getcwd())
        assert "No rats found" in post_extermination_viz
        
    finally:
        os.chdir(original_dir)


def test_multiple_decorators(temp_test_dir, clean_registry):
    """Test 5.2: Verify behavior when multiple functions are decorated."""
    # Create multiple decorated functions with different parameters
    @infest(infestation_level=1, rat_types=["sewer_rat"])
    def low_infestation():
        return "Low infestation with sewer rats"
    
    @infest(infestation_level=3, rat_types=["brown_rat"])
    def medium_infestation():
        return "Medium infestation with brown rats"
    
    @infest(infestation_level=5, rat_types=["black_rat"])
    def high_infestation():
        return "High infestation with black rats"
    
    # Change to the test directory and run the functions
    original_dir = os.getcwd()
    try:
        os.chdir(temp_test_dir)
        
        # Create a low infestation
        low_infestation()
        low_stats = count_rats(os.getcwd())
        
        # Verify rats were created according to function parameters
        assert low_stats["total_rats"] > 0
        assert low_stats["rats_by_type"]["sewer_rat"] > 0
        assert low_stats["rats_by_type"]["brown_rat"] == 0
        assert low_stats["rats_by_type"]["black_rat"] == 0
        
        # Exterminate all rats before next test
        exterminate(os.getcwd())
        
        # Create a medium infestation
        medium_infestation()
        medium_stats = count_rats(os.getcwd())
        
        # Verify rats were created according to function parameters
        assert medium_stats["total_rats"] > 0
        assert medium_stats["rats_by_type"]["sewer_rat"] == 0
        assert medium_stats["rats_by_type"]["brown_rat"] > 0
        assert medium_stats["rats_by_type"]["black_rat"] == 0
        
        # Exterminate all rats before next test
        exterminate(os.getcwd())
        
        # Create a high infestation
        high_infestation()
        high_stats = count_rats(os.getcwd())
        
        # Verify rats were created according to function parameters
        assert high_stats["total_rats"] > 0
        assert high_stats["rats_by_type"]["sewer_rat"] == 0
        assert high_stats["rats_by_type"]["brown_rat"] == 0
        assert high_stats["rats_by_type"]["black_rat"] > 0
        
        # Compare infestation levels
        assert high_stats["total_rats"] > medium_stats["total_rats"]
        assert medium_stats["total_rats"] > low_stats["total_rats"]
        
    finally:
        os.chdir(original_dir) 