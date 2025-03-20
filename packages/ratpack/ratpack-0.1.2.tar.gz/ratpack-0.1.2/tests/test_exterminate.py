"""Tests for the exterminate function."""

import os
import glob
import pytest

from ratpack.infest import exterminate, RAT_REGISTRY
from tests.conftest import create_test_rats, create_test_rat, count_actual_rat_files


def test_basic_extermination(temp_test_dir, clean_registry):
    """Test 3.1: Verify that exterminate() removes rat files."""
    # Create rat files
    rat_count = 5
    create_test_rats(temp_test_dir, count=rat_count)
    
    # Verify rats exist
    assert len(RAT_REGISTRY) > 0
    initial_rats, _ = count_actual_rat_files(temp_test_dir)
    assert initial_rats == rat_count
    
    # Exterminate the rats
    stats = exterminate(temp_test_dir)
    
    # Verify rats are removed
    remaining_rats, _ = count_actual_rat_files(temp_test_dir)
    assert remaining_rats == 0
    assert stats["rats_removed"] == rat_count
    
    # Check that the registry is updated
    assert len(RAT_REGISTRY) == 0


def test_directory_parameter(temp_test_dir, clean_registry):
    """Test 3.2: Verify that the directory parameter limits extermination to a specific directory."""
    # Create a subdirectory
    subdir = os.path.join(temp_test_dir, "subdir")
    os.makedirs(subdir, exist_ok=True)
    
    # Create rats in both directories
    main_rat_count = 3
    subdir_rat_count = 4
    
    create_test_rats(temp_test_dir, count=main_rat_count)
    create_test_rats(subdir, count=subdir_rat_count)
    
    # Exterminate rats only in the subdirectory
    stats = exterminate(subdir)
    
    # Verify only rats in the subdirectory are removed
    main_rats, _ = count_actual_rat_files(temp_test_dir)
    subdir_rats, _ = count_actual_rat_files(subdir)
    
    assert main_rats == main_rat_count
    assert subdir_rats == 0
    assert stats["rats_removed"] == subdir_rat_count


def test_rat_types_parameter(temp_test_dir, clean_registry):
    """Test 3.3: Verify that the rat_types parameter controls which types of rats are removed."""
    # Create rats of specific types
    test_rat_types = ["type_a", "type_b", "type_c"]
    rats_per_type = 2
    
    # Create rats of each type
    for rat_type in test_rat_types:
        for _ in range(rats_per_type):
            create_test_rat(temp_test_dir, rat_type=rat_type)
    
    # Exterminate only one type
    target_type = test_rat_types[0]
    stats = exterminate(temp_test_dir, rat_types=[target_type])
    
    # Verify only the specified type was removed
    for rat_file in glob.glob(os.path.join(temp_test_dir, "*.rat")):
        with open(rat_file, 'r') as f:
            rat_data = f.read()
            assert target_type not in rat_data
    
    # Count remaining rats
    remaining_rats, _ = count_actual_rat_files(temp_test_dir)
    expected_remaining = rats_per_type * (len(test_rat_types) - 1)
    
    assert remaining_rats == expected_remaining
    assert stats["rats_removed"] == rats_per_type


def test_burrows_only_parameter(temp_test_dir, clean_registry):
    """Test 3.4: Verify that the burrows_only parameter controls whether individual rats are removed."""
    # Create both individual rats and rat burrows
    individual_rat_count = 3
    burrow_rat_count = 4
    
    # Create individual rats
    create_test_rats(temp_test_dir, count=individual_rat_count, in_burrow=False)
    
    # Create rats in burrows
    create_test_rats(temp_test_dir, count=burrow_rat_count, in_burrow=True)
    
    # Exterminate only burrows
    stats = exterminate(temp_test_dir, burrows_only=True)
    
    # Verify only burrows were removed
    remaining_rats, remaining_burrows = count_actual_rat_files(temp_test_dir)
    
    assert remaining_rats == individual_rat_count
    assert remaining_burrows == 0
    assert stats["rats_removed"] == burrow_rat_count
    assert stats["burrows_removed"] > 0


def test_dry_run_parameter(temp_test_dir, clean_registry):
    """Test 3.5: Verify that the dry_run parameter prevents actual file removal."""
    # Create rat files
    rat_count = 5
    create_test_rats(temp_test_dir, count=rat_count)
    
    # Verify rats exist
    initial_rats, initial_burrows = count_actual_rat_files(temp_test_dir)
    
    # Exterminate with dry_run=True
    stats = exterminate(temp_test_dir, dry_run=True)
    
    # Verify rats still exist
    remaining_rats, remaining_burrows = count_actual_rat_files(temp_test_dir)
    
    assert remaining_rats == initial_rats
    assert remaining_burrows == initial_burrows
    
    # Verify statistics are still calculated correctly
    assert stats["rats_removed"] == rat_count 