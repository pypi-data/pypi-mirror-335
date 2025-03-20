"""Tests for the @infest decorator."""

import os
import inspect
import glob
from unittest.mock import patch
import pytest

from ratpack.infest import infest, RAT_REGISTRY
from tests.conftest import count_actual_rat_files


def test_basic_functionality(temp_test_dir, clean_registry):
    """Test 1.1: Verify that the decorator creates rat files when a decorated function is called."""
    # Create a simple decorated function
    @infest()
    def simple_function():
        """A simple test function."""
        return "Function result"
    
    # Initial state - no rats
    initial_rats, initial_burrows = count_actual_rat_files(temp_test_dir)
    assert initial_rats == 0
    assert initial_burrows == 0
    
    # Call the function from the temp directory
    original_dir = os.getcwd()
    try:
        os.chdir(temp_test_dir)
        result = simple_function()
        
        # Verify the function's return value is unchanged
        assert result == "Function result"
        
        # Verify rats were created
        rats, burrows = count_actual_rat_files(os.getcwd())
        assert rats > 0
    finally:
        os.chdir(original_dir)


def test_infestation_level_parameter(temp_test_dir, clean_registry):
    """Test 1.2: Verify that the infestation_level parameter affects the number of rats created."""
    # Create functions with different infestation levels
    @infest(infestation_level=1)
    def low_infestation():
        return "Low"
    
    @infest(infestation_level=3)
    def medium_infestation():
        return "Medium"
    
    @infest(infestation_level=5)
    def high_infestation():
        return "High"
    
    # Call each function and count rats
    original_dir = os.getcwd()
    try:
        os.chdir(temp_test_dir)
        
        # Test low infestation
        low_infestation()
        low_rats, _ = count_actual_rat_files(os.getcwd())
        
        # Clear for next test
        for rat_file in glob.glob("*.rat"):
            os.remove(rat_file)
        for burrow_dir in glob.glob("rat_burrow_*"):
            for rat_file in glob.glob(os.path.join(burrow_dir, "*.rat")):
                os.remove(rat_file)
            os.rmdir(burrow_dir)
        RAT_REGISTRY.clear()
        
        # Test medium infestation
        medium_infestation()
        medium_rats, _ = count_actual_rat_files(os.getcwd())
        
        # Clear for next test
        for rat_file in glob.glob("*.rat"):
            os.remove(rat_file)
        for burrow_dir in glob.glob("rat_burrow_*"):
            for rat_file in glob.glob(os.path.join(burrow_dir, "*.rat")):
                os.remove(rat_file)
            os.rmdir(burrow_dir)
        RAT_REGISTRY.clear()
        
        # Test high infestation
        high_infestation()
        high_rats, _ = count_actual_rat_files(os.getcwd())
        
        # Higher infestation levels should generally create more rats
        # Note: Due to random factors, we can't guarantee exact numbers
        # but the trend should be that higher levels create more rats on average
        assert low_rats > 0
        assert medium_rats >= low_rats
        assert high_rats >= medium_rats
        
    finally:
        os.chdir(original_dir)


def test_rat_types_parameter(temp_test_dir, clean_registry):
    """Test 1.3: Verify that the rat_types parameter controls which types of rats are created."""
    # Create a function with specific rat types
    specific_rat_type = "sewer_rat"
    
    @infest(rat_types=[specific_rat_type])
    def specific_rats():
        return "Only sewer rats"
    
    # Call the function from the temp directory
    original_dir = os.getcwd()
    try:
        os.chdir(temp_test_dir)
        specific_rats()
        
        # Verify that only rats of the specified type were created
        # Check each rat file
        for rat_file in glob.glob("*.rat"):
            assert specific_rat_type in rat_file
                
        # Check rats in burrows
        for burrow_dir in glob.glob("rat_burrow_*"):
            for rat_file in glob.glob(os.path.join(burrow_dir, "*.rat")):
                assert specific_rat_type in rat_file
    finally:
        os.chdir(original_dir)


@patch('random.random')
def test_burrow_probability_parameter(mock_random, temp_test_dir, clean_registry):
    """Test 1.4: Verify that the burrow_probability parameter affects burrow creation."""
    # Test with 0.0 probability - should never create burrows
    mock_random.return_value = 0.5  # Will be compared with burrow_probability
    
    @infest(burrow_probability=0.0)
    def no_burrows():
        return "No burrows"
    
    # Test with 1.0 probability - should always create burrows
    @infest(burrow_probability=1.0)
    def all_burrows():
        return "All burrows"
    
    # Call functions from the temp directory
    original_dir = os.getcwd()
    try:
        os.chdir(temp_test_dir)
        
        # Test with 0.0 probability
        no_burrows()
        _, zero_prob_burrows = count_actual_rat_files(os.getcwd())
        
        # Clear for next test
        for rat_file in glob.glob("*.rat"):
            os.remove(rat_file)
        for burrow_dir in glob.glob("rat_burrow_*"):
            for rat_file in glob.glob(os.path.join(burrow_dir, "*.rat")):
                os.remove(rat_file)
            os.rmdir(burrow_dir)
        RAT_REGISTRY.clear()
        
        # Test with 1.0 probability
        all_burrows()
        _, all_prob_burrows = count_actual_rat_files(os.getcwd())
        
        # Verify burrow creation based on probability
        assert zero_prob_burrows == 0  # No burrows with 0.0 probability
        assert all_prob_burrows > 0     # Should have burrows with 1.0 probability
        
    finally:
        os.chdir(original_dir)


def test_function_wrapping(clean_registry):
    """Test 1.5: Verify that the decorator properly preserves function metadata."""
    # Create a function with docstring and annotations
    @infest()
    def test_function(param1: str, param2: int = 0) -> str:
        """This is a test function with annotations.
        
        Args:
            param1: First parameter
            param2: Second parameter
            
        Returns:
            A string result
        """
        return f"{param1} - {param2}"
    
    # Verify that metadata is preserved
    assert test_function.__name__ == "test_function"
    assert "This is a test function with annotations" in test_function.__doc__
    
    # Verify annotations are preserved
    annotations = test_function.__annotations__
    assert annotations.get("param1") == str
    assert annotations.get("param2") == int
    assert annotations.get("return") == str
    
    # Verify the function signature is preserved
    signature = inspect.signature(test_function)
    parameters = signature.parameters
    
    assert "param1" in parameters
    assert "param2" in parameters
    assert parameters["param2"].default == 0 