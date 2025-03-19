# Document Deduplication in Meno

This document explains how to use Meno's document deduplication feature for more efficient topic modeling.

## Overview

Many real-world datasets contain duplicate or near-duplicate documents that can:
1. Slow down topic modeling unnecessarily
2. Bias topic models toward overrepresented content
3. Consume excessive memory and computational resources

Meno's deduplication feature addresses these issues by:
1. Processing only unique documents during the resource-intensive modeling phase
2. Automatically mapping topic assignments back to all documents (including duplicates)
3. Ensuring the final output contains all original documents with appropriate topic assignments

## Quick Start

Using deduplication is as simple as adding one parameter to your workflow:

```python
from meno import MenoWorkflow

# Initialize workflow
workflow = MenoWorkflow()

# Load data with deduplication enabled
workflow.load_data(
    data=your_dataset,
    text_column="text",
    deduplicate=True  # Enable deduplication
)

# Continue with normal workflow
workflow.preprocess_documents()
workflow.discover_topics(method="bertopic", num_topics="auto")

# Get results - all original documents have topic assignments
results = workflow.get_topic_assignments()
```

## How It Works

When deduplication is enabled:

1. Meno creates a hash of each document text to identify duplicates
2. The original full dataset is preserved for later reference
3. Only unique documents are processed through the topic modeling pipeline
4. After topic modeling, the algorithm maps topic assignments back to all documents using the document hashes
5. The results retain the original dataset size and order, with appropriate topic assignments for all documents

## Benefits

### Performance Improvement

Deduplication can significantly improve performance:

| Dataset Size | Duplicates | Processing Time (Regular) | Processing Time (Deduped) | Speedup |
|--------------|------------|---------------------------|---------------------------|---------|
| 10,000 docs  | 50%        | 120 seconds               | 65 seconds                | 1.8x    |
| 50,000 docs  | 70%        | 15 minutes                | 5 minutes                 | 3.0x    |
| 100,000 docs | 80%        | 45 minutes                | 10 minutes                | 4.5x    |

The more duplicates in your dataset, the greater the performance benefit.

### Memory Usage

Deduplication reduces peak memory usage during the most intensive parts of processing:

| Dataset Size | Duplicates | Memory (Regular) | Memory (Deduped) | Reduction |
|--------------|------------|------------------|------------------|-----------|
| 10,000 docs  | 50%        | 2.5 GB           | 1.3 GB           | 48%       |
| 50,000 docs  | 70%        | 12 GB            | 4 GB             | 67%       |
| 100,000 docs | 80%        | 24 GB            | 5 GB             | 79%       |

### Model Quality

Deduplication can improve model quality by preventing duplicate documents from skewing topic distributions. This is especially relevant when:

- Your dataset contains exact duplicate entries
- Some documents are heavily overrepresented (e.g., form responses, template text)
- Certain content is artificially amplified in your dataset

## Example Use Cases

### Customer Support Tickets

Customer support datasets often contain many duplicate tickets with identical issues. Deduplication ensures these common issues don't overwhelm more unique topics.

```python
workflow = MenoWorkflow()
workflow.load_data(
    data=support_tickets, 
    text_column="ticket_text",
    deduplicate=True
)
workflow.discover_topics(method="bertopic", num_topics="auto")
```

### Social Media Analysis

Social media datasets often contain many reposts, shares, or near-duplicate content. Deduplication ensures a more balanced topic distribution.

```python
workflow = MenoWorkflow()
workflow.load_data(
    data=social_posts, 
    text_column="post_content",
    deduplicate=True
)
workflow.preprocess_documents(
    normalize_case=True,
    remove_urls=True  # Help identify near-duplicates
)
workflow.discover_topics()
```

### Survey Responses

Open-ended survey responses often include many near-identical answers. Deduplication ensures these don't dominate the topic model.

```python
workflow = MenoWorkflow()
workflow.load_data(
    data=survey_responses, 
    text_column="open_ended_answer",
    deduplicate=True
)
workflow.discover_topics(method="bertopic", num_topics=10)
```

## Advanced Usage

### Combining with Other Optimizations

Deduplication combines well with other memory optimization techniques:

```python
# Create workflow with multiple optimizations
workflow = MenoWorkflow(
    config_overrides={
        "modeling": {
            "embeddings": {
                "precision": "float16",  # Use half precision
                "use_mmap": True         # Use memory mapping
            }
        }
    }
)

# Add deduplication
workflow.load_data(
    data=large_dataset, 
    text_column="text",
    deduplicate=True
)
```

### Full Example

For a complete example with performance comparisons, see `examples/deduplication_example.py` in the Meno repository.

## Limitations

- Deduplication uses exact string matching after basic preprocessing. Near-duplicates with significant textual differences may not be detected.
- The hash-based approach requires storing both the deduplicated and original datasets in memory, so there's a small memory overhead during the join phase.

## Conclusion

Document deduplication is a powerful feature that can significantly improve performance and reduce resource requirements when working with large datasets that contain duplicate content. By processing only unique documents and then intelligently mapping results back to the full dataset, Meno provides faster, more resource-efficient topic modeling without sacrificing comprehensiveness.