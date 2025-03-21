"""Tests for fuzzy deduplication functionality."""

import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path

import sys
from pathlib import Path

# Add examples directory to path
examples_path = Path('/Users/srepho/Downloads/ClaudeDev/meno/meno/examples')
if examples_path.exists() and examples_path not in sys.path:
    sys.path.append(str(examples_path))

from fuzzy_deduplication_example import (
    calculate_similarity,
    identify_fuzzy_duplicates,
    fuzzy_deduplicate,
    create_dataset_with_fuzzy_duplicates,
    visualize_duplicate_groups
)


class TestFuzzyDeduplication:
    """Tests for fuzzy deduplication functionality."""

    @pytest.fixture
    def sample_data(self):
        """Create a small dataset with fuzzy duplicates for testing."""
        return create_dataset_with_fuzzy_duplicates(
            num_unique=20,
            duplicates_per_doc=2,
            noise_levels=[0.0, 0.1],
            seed=42
        )

    def test_calculate_similarity(self):
        """Test the text similarity calculation."""
        # Identical texts
        text1 = "This is a test document."
        text2 = "This is a test document."
        assert calculate_similarity(text1, text2) == 1.0

        # Similar texts with minor difference
        text3 = "This is a test document with a small change."
        similarity = calculate_similarity(text1, text3)
        assert 0.7 < similarity < 1.0

        # Very different texts
        text4 = "Completely different content that has nothing in common."
        similarity = calculate_similarity(text1, text4)
        assert similarity < 0.5

    def test_identify_fuzzy_duplicates(self, sample_data):
        """Test identifying fuzzy duplicates in a dataset."""
        # Find groups with high threshold (exact matches only)
        high_threshold_groups = identify_fuzzy_duplicates(
            sample_data, "text", threshold=1.0
        )
        
        # Find groups with moderate threshold
        moderate_threshold_groups = identify_fuzzy_duplicates(
            sample_data, "text", threshold=0.9
        )
        
        # Find groups with low threshold (more matches)
        low_threshold_groups = identify_fuzzy_duplicates(
            sample_data, "text", threshold=0.7
        )
        
        # Verify that lower thresholds find more or equal groups
        assert len(high_threshold_groups) <= len(moderate_threshold_groups)
        assert len(moderate_threshold_groups) <= len(low_threshold_groups)
        
        # Check that at least some fuzzy duplicates were found
        assert len(low_threshold_groups) > 0

    def test_fuzzy_deduplicate(self, sample_data):
        """Test the fuzzy deduplication function."""
        original_size = len(sample_data)
        
        # Apply fuzzy deduplication
        deduplicated_data, duplicate_map, fuzzy_groups = fuzzy_deduplicate(
            sample_data, "text", threshold=0.9
        )
        
        # Verify that deduplication reduced dataset size
        assert len(deduplicated_data) < original_size
        
        # Verify duplicate map size
        expected_removed = original_size - len(deduplicated_data)
        assert len(duplicate_map) == expected_removed
        
        # Verify groups
        assert len(fuzzy_groups) > 0
        
        # Check integrity of duplicate map
        for removed_idx, representative_idx in duplicate_map.items():
            # Representative should be in the deduplicated dataset
            assert representative_idx in deduplicated_data.index
            
            # Removed index should be in the original dataset
            assert removed_idx in sample_data.index

    def test_fuzzy_vs_exact_deduplication(self, sample_data):
        """Test difference between fuzzy and exact deduplication."""
        # Count exact duplicates
        exact_duplicates = sample_data.duplicated(subset=["text"]).sum()
        
        # Apply fuzzy deduplication
        deduplicated_data, _, fuzzy_groups = fuzzy_deduplicate(
            sample_data, "text", threshold=0.85
        )
        
        fuzzy_removed = len(sample_data) - len(deduplicated_data)
        
        # Fuzzy deduplication should find more duplicates than exact
        assert fuzzy_removed >= exact_duplicates
        
        # If we have noise in the test data, fuzzy should find more duplicates
        if 0.1 in sample_data["duplicate_type"].str.contains("fuzzy_0.1").any():
            assert fuzzy_removed > exact_duplicates

    def test_visualization(self, sample_data, tmp_path):
        """Test visualization of duplicate groups."""
        # Apply deduplication
        deduplicated_data, duplicate_map, fuzzy_groups = fuzzy_deduplicate(
            sample_data, "text", threshold=0.85
        )
        
        # Add a topic column for visualization
        sample_data["assigned_topic"] = np.random.randint(0, 5, size=len(sample_data))
        
        # Create visualization in a temporary directory
        output_dir = tmp_path / "viz_output"
        output_dir.mkdir()
        
        # Generate visualization
        visualize_duplicate_groups(sample_data, fuzzy_groups, output_dir)
        
        # Check if the visualization was created
        assert (output_dir / "fuzzy_duplicate_analysis.png").exists()