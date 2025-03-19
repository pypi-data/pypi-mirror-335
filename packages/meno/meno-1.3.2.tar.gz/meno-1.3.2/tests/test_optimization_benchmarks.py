"""Tests for optimization benchmark functionality."""

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

from optimization_benchmarks import (
    create_benchmark_dataset,
    get_memory_usage,
    benchmark_memory_optimizations,
    benchmark_deduplication,
    benchmark_incremental_updates,
    plot_benchmark_results
)


class TestOptimizationBenchmarks:
    """Tests for optimization benchmark utilities."""

    @pytest.fixture
    def small_dataset(self):
        """Create a very small dataset for quick benchmark testing."""
        return create_benchmark_dataset(
            num_documents=50,  # Small number for tests
            num_duplicates=20, 
            words_per_doc=30,
            seed=42
        )

    def test_create_benchmark_dataset(self):
        """Test creation of benchmark datasets."""
        # Create dataset with specific parameters
        dataset = create_benchmark_dataset(
            num_documents=20,
            num_duplicates=10,
            words_per_doc=15,
            seed=42
        )
        
        # Check dataset dimensions
        assert len(dataset) == 30  # 20 documents + 10 duplicates
        
        # Check required columns
        assert "text" in dataset.columns
        assert "id" in dataset.columns
        assert "topic" in dataset.columns
        assert "is_duplicate" in dataset.columns
        
        # Check duplicate distribution
        duplicates = dataset[dataset["is_duplicate"] == True]
        assert len(duplicates) == 10

    def test_get_memory_usage(self):
        """Test memory usage measurement function."""
        memory = get_memory_usage()
        
        # Memory should be a positive number
        assert memory > 0
        
        # Create a large array to increase memory usage
        large_array = np.zeros((1000, 1000))
        
        # Memory should still be measurable
        memory_after = get_memory_usage()
        assert memory_after > 0

    def test_benchmark_memory_optimizations(self, small_dataset):
        """Test memory optimization benchmarking with a small dataset."""
        # Run benchmark with minimal settings
        results = benchmark_memory_optimizations(
            dataset=small_dataset.head(10),  # Very small subset
            batch_size=5                     # Small batch size
        )
        
        # Check results structure
        assert isinstance(results, pd.DataFrame)
        assert "configuration" in results.columns
        assert "time_seconds" in results.columns
        assert "memory_mb" in results.columns
        assert "embedding_size_mb" in results.columns
        assert "precision" in results.columns
        
        # Check that all configurations were tested
        configs = [
            "Baseline (float32)",
            "Half Precision (float16)",
            "Memory Mapped (float32)",
            "Combined Optimizations",
            "8-bit Quantization"
        ]
        
        for config in configs:
            assert config in results["configuration"].values

    def test_benchmark_deduplication(self, small_dataset):
        """Test deduplication benchmarking with a small dataset."""
        # Run benchmark with minimal settings
        results = benchmark_deduplication(
            dataset=small_dataset.head(20)  # Very small subset
        )
        
        # Check results structure
        assert isinstance(results, pd.DataFrame)
        assert "deduplication" in results.columns
        assert "time_seconds" in results.columns
        assert "memory_mb" in results.columns
        assert "documents_processed" in results.columns
        
        # Check that both enabled and disabled were tested
        assert "Enabled" in results["deduplication"].values
        assert "Disabled" in results["deduplication"].values
        
        # With deduplication, processed documents should be fewer
        docs_with_dedup = results[results["deduplication"] == "Enabled"]["documents_processed"].iloc[0]
        docs_without_dedup = results[results["deduplication"] == "Disabled"]["documents_processed"].iloc[0]
        assert docs_with_dedup <= docs_without_dedup

    def test_benchmark_incremental_updates(self, small_dataset):
        """Test incremental update benchmarking with a small dataset."""
        # Create initial and update datasets
        initial_data = small_dataset.head(15)
        update_data1 = small_dataset.iloc[15:20].copy()
        update_data2 = small_dataset.iloc[20:25].copy()
        update_datasets = [update_data1, update_data2]
        
        # Run benchmark with minimal settings
        results = benchmark_incremental_updates(
            initial_dataset=initial_data,
            update_datasets=update_datasets
        )
        
        # Check results structure
        assert isinstance(results, pd.DataFrame)
        assert "update_mode" in results.columns
        assert "avg_update_time" in results.columns
        assert "avg_stability" in results.columns
        
        # Check that all update modes were tested
        modes = ["incremental", "partial_retrain", "full_retrain"]
        for mode in modes:
            assert mode in results["update_mode"].values

    def test_plot_benchmark_results(self, small_dataset, tmp_path):
        """Test plotting benchmark results."""
        # Create simple benchmark results
        memory_results = pd.DataFrame({
            "configuration": ["Config1", "Config2", "Config3", "Config4", "Config5"],
            "memory_mb": [500, 400, 450, 350, 300],
            "time_seconds": [10, 8, 9, 7, 6],
            "embedding_size_mb": [200, 150, 180, 140, 120],
            "precision": ["float32", "float16", "float32", "float16", "int8"],
            "memory_mapped": [False, False, True, True, True],
            "quantized": [False, False, False, False, True]
        })
        
        dedup_results = pd.DataFrame({
            "deduplication": ["Disabled", "Enabled"],
            "time_seconds": [15, 10],
            "memory_mb": [600, 400],
            "documents_processed": [50, 40]
        })
        
        incremental_results = pd.DataFrame({
            "update_mode": ["incremental", "partial_retrain", "full_retrain"],
            "avg_update_time": [5, 8, 12],
            "avg_stability": [0.9, 0.7, 0.5],
            "total_update_time": [10, 16, 24],
            "stability_scores": [[0.9, 0.8], [0.7, 0.6], [0.5, 0.4]],
            "update_times": [[4, 6], [7, 9], [11, 13]]
        })
        
        # Create output directory
        output_dir = tmp_path / "benchmark_plots"
        output_dir.mkdir()
        
        # Generate plots
        result = plot_benchmark_results(
            memory_results=memory_results,
            dedup_results=dedup_results,
            incremental_results=incremental_results,
            output_dir=output_dir
        )
        
        # Check that plots were created
        assert (output_dir / "memory_optimization_benchmark.png").exists()
        assert (output_dir / "deduplication_benchmark.png").exists()
        assert (output_dir / "incremental_learning_benchmark.png").exists()
        assert (output_dir / "combined_optimization_benchmark.png").exists()
        
        # Function should return True on success
        assert result is True