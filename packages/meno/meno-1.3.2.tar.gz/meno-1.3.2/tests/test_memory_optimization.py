"""Tests for memory optimization in Meno."""

import pytest
import numpy as np
import os
from pathlib import Path
import sys

from meno.modeling.embeddings import DocumentEmbedding


class TestMemoryOptimization:
    """Tests for memory optimization features."""
    
    @pytest.fixture
    def sample_texts(self):
        """Create sample texts for testing."""
        return [
            "This is a document about technology and computers.",
            "Healthcare and medicine are important for public health.",
            "Sports and exercise are good for physical health.",
            "Education and learning are lifelong pursuits.",
            "Politics and government policies affect many aspects of life."
        ]
    
    def test_embedding_precision(self, sample_texts):
        """Test that embeddings can use different precision levels."""
        # Create model with float32 precision
        model_float32 = DocumentEmbedding(
            model_name="all-MiniLM-L6-v2",
            precision="float32"
        )
        
        # Create model with float16 precision
        model_float16 = DocumentEmbedding(
            model_name="all-MiniLM-L6-v2",
            precision="float16"
        )
        
        # Embed documents with both models
        embeddings_float32 = model_float32.embed_documents(sample_texts)
        embeddings_float16 = model_float16.embed_documents(sample_texts)
        
        # Check dtypes
        assert embeddings_float32.dtype == np.float32
        assert embeddings_float16.dtype == np.float16
        
        # Check that dimensions are the same
        assert embeddings_float32.shape == embeddings_float16.shape
        
        # Check that values are similar (allowing for precision differences)
        # Convert both to float64 for comparison
        float32_as_64 = embeddings_float32.astype(np.float64)
        float16_as_64 = embeddings_float16.astype(np.float64)
        
        # Mean absolute difference should be small
        mean_abs_diff = np.abs(float32_as_64 - float16_as_64).mean()
        assert mean_abs_diff < 0.1  # Allow some difference due to precision
    
    def test_memory_mapped_embeddings(self, sample_texts, tmp_path):
        """Test memory-mapped embedding storage."""
        # Skip if numpy doesn't support memory mapping
        try:
            np.memmap
        except AttributeError:
            pytest.skip("NumPy doesn't support memory mapping")
        
        # Create test embeddings
        model = DocumentEmbedding(
            model_name="all-MiniLM-L6-v2",
            use_mmap=True  # Enable memory mapping
        )
        
        # Generate embeddings
        embeddings = model.embed_documents(sample_texts)
        
        # Check that embeddings were created successfully
        assert embeddings.shape[0] == len(sample_texts)
        assert embeddings.shape[1] > 0  # Embedding dimension should be non-zero
        
        # Make sure embeddings are normalized
        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5)
    
    def test_batch_processing(self, sample_texts):
        """Test batch processing of documents."""
        # Create model with batch processing
        model = DocumentEmbedding(
            model_name="all-MiniLM-L6-v2",
            batch_size=2  # Small batch size for testing
        )
        
        # Embed documents
        embeddings = model.embed_documents(sample_texts)
        
        # Check that embeddings have correct shape
        assert embeddings.shape[0] == len(sample_texts)
        assert embeddings.shape[1] > 0  # Embedding dimension should be non-zero
        
        # Validate that embeddings are normalized (unit length)
        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5)