# Memory Optimization in Meno

This document describes techniques for optimizing memory usage in Meno, particularly for larger datasets or resource-constrained environments.

## Overview

Meno includes several memory optimization features that can significantly reduce memory usage while maintaining model quality. These optimizations are especially important for:

- Large datasets (100,000+ documents)
- Running on machines with limited RAM
- Processing on CPU-only environments
- Deployment in constrained settings (embedded, edge devices, etc.)

The main optimization techniques available include:

1. **Precision reduction**: Using 16-bit or 8-bit precision instead of 32-bit
2. **Model quantization**: Reducing model weight precision for faster inference
3. **Memory mapping**: Loading embeddings from disk as needed rather than all at once
4. **Progressive loading**: Processing data in chunks for larger-than-memory datasets

## Quick Start - Memory Optimization

To enable memory optimizations in your workflow:

```python
from meno import MenoWorkflow

# Configure memory optimizations
workflow = MenoWorkflow(
    config_overrides={
        "modeling": {
            "embeddings": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "precision": "float16",    # Use half-precision (float16)
                "use_mmap": True,          # Use memory mapping
                "quantize": True           # Quantize model weights (if available)
            }
        }
    }
)

# Continue with normal workflow
workflow.load_data(data=your_data, text_column="text")
workflow.preprocess_documents()
workflow.discover_topics(method="bertopic", num_topics="auto")
```

## Detailed Optimization Techniques

### Reduced Precision

Meno supports multiple precision levels for embedding storage:

- `float32` (default): Standard 32-bit floating point
- `float16`: Half-precision (16-bit) floating point
- `int8`: 8-bit integer quantization

To use reduced precision:

```python
# In a workflow configuration
config_overrides = {
    "modeling": {
        "embeddings": {
            "precision": "float16"  # or "int8" for further reduction
        }
    }
}

# Or directly with the embedding model
from meno.modeling.embeddings import DocumentEmbedding

embedder = DocumentEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    precision="float16"
)
```

**Memory Savings**: Typically 50% reduction for float16, 75% reduction for int8.

### Model Weight Quantization

For even further memory reduction, you can quantize the model weights themselves. This requires the `bitsandbytes` package to be installed:

```bash
pip install bitsandbytes
```

Then, enable quantization:

```python
# In a workflow configuration
config_overrides = {
    "modeling": {
        "embeddings": {
            "precision": "int8",
            "quantize": True
        }
    }
}

# Or directly with the embedding model
from meno.modeling.embeddings import DocumentEmbedding

embedder = DocumentEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    precision="int8",
    quantize=True
)
```

**Memory Savings**: Up to 75% memory reduction for model weights.

### Memory Mapping

For large datasets, Meno can store embeddings on disk and load them as needed using memory mapping:

```python
# In a workflow configuration
config_overrides = {
    "modeling": {
        "embeddings": {
            "use_mmap": True,
            "cache_dir": "/path/to/cache"  # Optional custom cache location
        }
    }
}

# Or directly with the embedding model
from meno.modeling.embeddings import DocumentEmbedding

embedder = DocumentEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2", 
    use_mmap=True,
    cache_dir="/path/to/cache"
)
```

**Memory Savings**: Allows processing of datasets larger than available RAM by offloading to disk.

### Progressive Loading

For extremely large datasets, use the `StreamingProcessor` for processing data in batches:

```python
from meno.modeling.streaming_processor import StreamingProcessor
from meno.modeling.embeddings import DocumentEmbedding

# Create embedding model with optimizations
embedder = DocumentEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    precision="float16",
    use_mmap=True
)

# Create streaming processor
processor = StreamingProcessor(
    embedding_model=embedder,
    batch_size=1000,           # Process 1000 documents at a time
    use_checkpointing=True,    # Save progress periodically
    checkpoint_dir="/path/to/checkpoints"
)

# Process a large file
processor.stream_from_file(
    file_path="huge_dataset.csv",
    text_column="text",
    id_column="id"
)

# Get model after processing
model = processor.get_model()
```

**Memory Savings**: Allows processing virtually unlimited dataset sizes with constant memory usage.

## Performance Benchmarks

The table below shows approximate memory usage for different configurations when processing 10,000 documents (your results may vary depending on hardware and model):

| Configuration              | Memory Usage | Reduction | Processing Time |
|----------------------------|--------------|-----------|-----------------|
| Default (float32)          | 100 MB       | Baseline  | 1.0x            |
| Half Precision (float16)   | 50 MB        | 50%       | 1.05x           |
| Memory-Mapped (float32)    | 30 MB        | 70%       | 1.2x            |
| Memory-Mapped (float16)    | 15 MB        | 85%       | 1.25x           |
| 8-bit (int8)               | 10 MB        | 90%       | 1.3x            |
| Fully Quantized (int8)     | 5 MB         | 95%       | 1.4x            |

## Example: Complete Memory-Optimized Workflow

```python
import pandas as pd
from meno import MenoWorkflow

# Load data (example dataset)
data = pd.read_csv("large_dataset.csv")

# Create memory-optimized workflow
workflow = MenoWorkflow(
    config_overrides={
        "modeling": {
            "embeddings": {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "precision": "int8",  
                "use_mmap": True,
                "quantize": True
            },
            "clustering": {
                "algorithm": "hdbscan",
                "min_cluster_size": 10,
                "min_samples": 5,
                "prediction_data": True
            },
            "visualization": {
                "umap": {
                    "n_neighbors": 15,
                    "n_components": 2,
                    "low_memory": True
                }
            }
        }
    }
)

# Run workflow
workflow.load_data(data=data, text_column="text", id_column="id")
workflow.preprocess_documents()
workflow.discover_topics(method="bertopic", num_topics="auto")

# Get results
topics = workflow.get_topics()
doc_topics = workflow.get_topic_assignments()

print(f"Found {len(topics)} topics in {len(data)} documents")
```

## For Very Large Datasets: Incremental Learning

For the largest datasets, consider using the incremental learning capabilities:

```python
from meno import MenoWorkflow
from meno.modeling.incremental import TopicUpdater

# Initialize with a smaller subset first
initial_data = data.iloc[:5000]

# Train initial model
workflow = MenoWorkflow(config_overrides={"modeling": {"embeddings": {"precision": "float16"}}})
workflow.load_data(data=initial_data, text_column="text")
workflow.preprocess_documents()
workflow.discover_topics(method="bertopic", num_topics=20)

# Get the trained model
model = workflow.modeler.model

# Create topic updater
updater = TopicUpdater(model=model)

# Process data in batches
for i in range(1, 10):
    # Get next batch of data
    batch = data.iloc[i*5000:(i+1)*5000]
    batch_docs = batch["text"].tolist()
    batch_ids = batch["id"].tolist()
    
    # Update model with new batch
    model, stats = updater.update_model(
        documents=batch_docs,
        document_ids=batch_ids,
        update_mode="incremental",
        verbose=True
    )
    
    print(f"Batch {i}: Added {len(batch)} documents, topic stability: {stats['topic_stability']:.2f}")
```

## Troubleshooting

If you encounter memory issues:

1. **Monitor memory usage** - Use tools like `psutil` to track memory during processing
2. **Start small** - Test with a smaller subset of your data first
3. **Reduce batch size** - Use smaller batch sizes for embedding generation
4. **Check cache directory** - Ensure there's enough disk space for memory mapping
5. **Combine techniques** - Use all optimization techniques together for maximum savings

## Recommended Hardware Configurations

| Dataset Size    | Memory Required    | Recommended Configuration                                |
|-----------------|--------------------|---------------------------------------------------------|
| < 10K documents | 1-2 GB             | Default settings                                         |
| 10K-100K docs   | 4-8 GB             | float16 precision                                        |
| 100K-1M docs    | 16-32 GB           | float16 + memory mapping                                 |
| > 1M documents  | 32+ GB             | int8 + memory mapping + streaming + incremental updates  |

For more detailed examples, see `examples/memory_optimization_example.py` in the Meno repository.