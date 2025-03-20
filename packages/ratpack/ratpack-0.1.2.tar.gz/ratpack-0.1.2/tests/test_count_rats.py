"""Tests for the count_rats function."""

import os
import json
import time
import glob
import pytest

from ratpack.infest import count_rats, RAT_REGISTRY, RAT_TYPES
from tests.conftest import create_test_rat, create_test_rats, count_actual_rat_files


def test_basic_counting(temp_test_dir, clean_registry):
    """Test 2.1: Verify that count_rats() correctly counts all rats in a directory."""
    num_rats = 4
    create_test_rats(temp_test_dir, num_rats)

    print("Files in temp_test_dir:", os.listdir(temp_test_dir)) # Comment out later 

    counted_rats = count_rats(temp_test_dir)
    assert counted_rats["total_rats"] == num_rats, f"Expected {num_rats}, but got {counted_rats['total_rats']}"

def test_directory_parameter(temp_test_dir, clean_registry):
    """Test 2.2: Verify that the directory parameter limits counting to a specific directory."""
    create_test_rats(temp_test_dir, 3)
    # create another directory to test against
    # the other directory has different number of rats
    another_dir = temp_test_dir / "other_dir"
    another_dir.mkdir()
    create_test_rats(another_dir, 2)
    counted_rats = count_rats(temp_test_dir)
    # If get something different from 3
    assert counted_rats["total_rats"] == 3, f"Expected 3, but got {counted_rats['total_rats']}"

    # If get something different from 2
    counted_rats_other = count_rats(another_dir)
    assert counted_rats_other["total_rats"] == 2, f"Expected 2, but got {counted_rats_other['total_rats']}"


def test_include_burrows_parameter(temp_test_dir, clean_registry):
    """Test 2.3: Verify that the include_burrows parameter controls whether rats in burrows are counted."""
    # normal rats
    create_test_rats(temp_test_dir, 3)
    # burrow rats
    create_test_rats(temp_test_dir, 2, in_burrow=True)

    counted_rats_without_burrows = count_rats(temp_test_dir, include_burrows=False)
    assert counted_rats_without_burrows["total_rats"] == 3, f"Expected 3, but got {counted_rats_without_burrows['total_rats']}"

    counted_rats_with_burrows = count_rats(temp_test_dir, include_burrows=True)
    assert counted_rats_with_burrows["total_rats"] == 5, f"Expected 5, but got {counted_rats_with_burrows['total_rats']}"


def test_rat_types_parameter(temp_test_dir, clean_registry):
    """Test 2.4: Verify that the rat_types parameter filters rats by type."""
    """ In New York City, the primary rat species are Brown, black and marsh rats"""
    create_test_rat(temp_test_dir, rat_type="brown_rat")
    create_test_rat(temp_test_dir, rat_type="black_rat")
    create_test_rat(temp_test_dir, rat_type="marsh_rat")
    # outlier, NON-NYC rat that should not be counted:
    create_test_rat(temp_test_dir, rat_type="albino_rat")

    counted_rats = count_rats(temp_test_dir, rat_types=["brown_rat", "black_rat", "marsh_rat"])
    assert counted_rats["total_rats"] == 3, f"Expected 3, but got {counted_rats['total_rats']}"



def test_statistics_accuracy(temp_test_dir, clean_registry):
    """Test 2.5: Verify that the statistics in the return value are accurate."""
    create_test_rats(temp_test_dir, count=10)  # 10 surface rats
    # Create burrowed rats
    create_test_rats(temp_test_dir, count=5, in_burrow=True)  # 5 burrowed rats
    # Run count_rats() and check statistics
    counted_rats = count_rats(temp_test_dir, include_burrows=True)

    assert counted_rats["total_rats"] == 15, f"Expected 15 total rats, but got {counted_rats['total_rats']}"
    assert counted_rats["surface_rats"] == 10, f"Expected 10 surface rats, but got {counted_rats['surface_rats']}"
    assert counted_rats["burrowed_rats"] == 5, f"Expected 5 burrowed rats, but got {counted_rats['burrowed_rats']}"
