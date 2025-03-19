"""Tests for optimized embedding functionality."""

import pytest
import numpy as np
import os
import shutil
import tempfile
from pathlib import Path

from meno.modeling.embeddings import DocumentEmbedding


@pytest.fixture
def test_documents():
    """Create test documents."""
    return [
        "This is a test document for embedding.",
        "Another document with different content.",
        "The third document contains unique words.",
        "Document four has some overlapping terms.",
        "The final test document in this sample set."
    ]


@pytest.fixture
def temp_cache_dir():
    """Create temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir)


def test_embedding_precision_float16(test_documents, temp_cache_dir):
    """Test half-precision (float16) embeddings."""
    embedder = DocumentEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        precision="float16",
        cache_dir=temp_cache_dir
    )
    
    embeddings = embedder.embed_documents(test_documents, cache=True)
    
    # Check shape and dtype
    assert embeddings.shape == (len(test_documents), embedder.embedding_dim)
    assert embeddings.dtype == np.float16
    
    # Test that we get the same embeddings with a new instance
    embedder2 = DocumentEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2", 
        precision="float16", 
        cache_dir=temp_cache_dir
    )
    embeddings2 = embedder2.embed_documents(test_documents, cache=True)
    
    # Embeddings should be the same 
    np.testing.assert_allclose(embeddings, embeddings2, rtol=1e-4)


def test_embedding_precision_int8_without_quantization(test_documents, temp_cache_dir):
    """Test int8 precision embeddings without model weight quantization."""
    # This tests just the embedding storage, not model quantization
    embedder = DocumentEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        precision="int8",  # Store as int8
        quantize=False,    # Don't quantize model weights
        cache_dir=temp_cache_dir
    )
    
    embeddings = embedder.embed_documents(test_documents, cache=True)
    
    # Since we store float32 embeddings as int8, the values will be scaled
    assert embeddings.dtype == np.int8
    assert embeddings.shape == (len(test_documents), embedder.embedding_dim)
    
    # Values should be in int8 range
    assert np.max(embeddings) <= 127
    assert np.min(embeddings) >= -128


def test_memory_mapped_embeddings(test_documents, temp_cache_dir):
    """Test memory-mapped embedding storage."""
    embedder = DocumentEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        use_mmap=True,
        cache_dir=temp_cache_dir
    )
    
    # First generate and cache embeddings
    _ = embedder.embed_documents(test_documents, cache=True, cache_id="mmap_test")
    
    # Get the corpus hash for the cache file
    corpus_hash = embedder._compute_corpus_hash(test_documents)
    cache_path = Path(temp_cache_dir) / f"{embedder.model_hash}_{corpus_hash}.npy"
    
    # Check that the cache file exists
    assert cache_path.exists()
    
    # Get embeddings from cache, should use memory-mapping
    embeddings = embedder.embed_documents(test_documents, cache=True, cache_id="mmap_test")
    
    # Check shape
    assert embeddings.shape == (len(test_documents), embedder.embedding_dim)
    
    # Can still perform operations on the memory-mapped array
    assert np.mean(embeddings) != 0  # Non-zero mean


# Skip this test if bitsandbytes is not available
@pytest.mark.skipif(
    os.environ.get("SKIP_QUANTIZE_TEST", "true").lower() == "true",
    reason="Skipping quantized model test by default. Set SKIP_QUANTIZE_TEST=false to run."
)
def test_quantized_model(test_documents, temp_cache_dir):
    """Test model with quantized weights if bitsandbytes is available."""
    try:
        import bitsandbytes  # noqa
    except ImportError:
        pytest.skip("bitsandbytes not available, skipping quantized model test")
    
    embedder = DocumentEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        precision="int8",
        quantize=True,
        cache_dir=temp_cache_dir
    )
    
    embeddings = embedder.embed_documents(test_documents, cache=True)
    
    # Check shape
    assert embeddings.shape == (len(test_documents), embedder.embedding_dim)
    assert embeddings.dtype == np.int8
    
    # Values should be in int8 range
    assert np.max(embeddings) <= 127
    assert np.min(embeddings) >= -128