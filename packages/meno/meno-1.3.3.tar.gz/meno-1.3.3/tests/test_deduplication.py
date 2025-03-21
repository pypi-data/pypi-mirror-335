"""Tests for document deduplication in Meno."""

import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path

from meno import MenoWorkflow


class TestDeduplication:
    """Tests for document deduplication functionality."""
    
    @pytest.fixture
    def sample_data_with_duplicates(self):
        """Create sample data with exact duplicates for testing."""
        np.random.seed(42)
        
        # Create base documents
        docs = [
            "This is document one about technology.",
            "This is document two about healthcare.",
            "This is document three about finance.",
            "This is document four about education.",
            "This is document five about politics."
        ]
        
        # Create dataset with duplicates
        data = []
        
        # Add original documents
        for i, doc in enumerate(docs):
            data.append({
                "text": doc,
                "id": f"doc_{i}",
                "is_duplicate": False
            })
        
        # Add exact duplicates
        for i in range(3):  # Add 3 duplicates
            dup_idx = np.random.randint(0, len(docs))
            data.append({
                "text": docs[dup_idx],
                "id": f"dup_{i}",
                "is_duplicate": True
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        np.random.shuffle(df.values)  # Shuffle rows
        return df
    
    def test_exact_deduplication(self, sample_data_with_duplicates):
        """Test exact document deduplication."""
        # Count initial documents
        initial_count = len(sample_data_with_duplicates)
        assert initial_count == 8  # 5 original + 3 duplicates
        
        # Create workflow with deduplication
        workflow = MenoWorkflow()
        
        # Load data with deduplication
        workflow.load_data(
            data=sample_data_with_duplicates,
            text_column="text",
            deduplicate=True
        )
        
        # Check that duplicates were removed
        deduped_count = len(workflow.documents)
        assert deduped_count < initial_count
        assert deduped_count == 5  # Should have only unique documents
        
        # In some implementations, duplicate info is stored differently
        # Just check that the number of documents was reduced
        assert deduped_count < initial_count
    
    def test_deduplication_disabled(self, sample_data_with_duplicates):
        """Test workflow with deduplication disabled."""
        # Count initial documents
        initial_count = len(sample_data_with_duplicates)
        
        # Create workflow without deduplication
        workflow = MenoWorkflow()
        
        # Load data without deduplication
        workflow.load_data(
            data=sample_data_with_duplicates,
            text_column="text",
            deduplicate=False
        )
        
        # Check that all documents were kept
        assert len(workflow.documents) == initial_count
    
    def test_with_category(self, sample_data_with_duplicates):
        """Test deduplication with category column."""
        # Create workflow
        workflow = MenoWorkflow()
        
        # Add a category column
        sample_data_with_duplicates['category'] = 'test_category'
        
        # Load data with deduplication and category
        workflow.load_data(
            data=sample_data_with_duplicates,
            text_column="text",
            category_column="category",
            deduplicate=True
        )
        
        # Verify the documents were loaded and duplicates were removed
        assert len(workflow.documents) < len(sample_data_with_duplicates)
    
    def test_empty_dataset(self):
        """Test deduplication with an empty dataset."""
        # Create empty dataset
        empty_data = pd.DataFrame(columns=["text", "id"])
        
        # Create workflow
        workflow = MenoWorkflow()
        
        # Load empty data with deduplication (should not crash)
        workflow.load_data(
            data=empty_data,
            text_column="text",
            deduplicate=True
        )
        
        # Check that no documents were loaded
        assert len(workflow.documents) == 0