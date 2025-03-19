# Fuzzy Deduplication in Meno

This document explains how to use fuzzy matching for document deduplication in Meno, allowing the identification and handling of near-duplicate documents for more efficient topic modeling.

## Overview

While Meno's built-in deduplication feature handles exact document duplicates, many real-world datasets contain near-duplicate documents that differ slightly but represent the same content:

- Documents with minor formatting differences
- Comments or annotations added to otherwise identical text
- Versioned documents with small updates
- Content with slight rephrasing or word substitutions

Fuzzy deduplication extends Meno's capabilities to identify these near-duplicate documents, providing:

1. More efficient processing by removing conceptually redundant content
2. More accurate topic models by preventing near-duplicate content from skewing topic distributions
3. Better resource usage when working with noisy datasets

## Quick Start

```python
from meno import MenoWorkflow
from meno.examples.fuzzy_deduplication_example import fuzzy_deduplicate

# Prepare your dataset
import pandas as pd
data = pd.read_csv("your_dataset.csv")

# Apply fuzzy deduplication
deduplicated_data, duplicate_map, fuzzy_groups = fuzzy_deduplicate(
    data, 
    text_column="text",
    threshold=0.85  # Similarity threshold (0-1)
)

# Run topic modeling on deduplicated data
workflow = MenoWorkflow()
workflow.load_data(
    data=deduplicated_data, 
    text_column="text"
)
workflow.preprocess_documents()
results = workflow.discover_topics(method="bertopic", num_topics="auto")

# Map topics back to full dataset
# Create a mapping from index to topic
index_to_topic = dict(zip(results['original_index'], results['topic']))

# Apply to original dataset
topics_for_all = []
for idx in data['original_index']:
    if idx in index_to_topic:
        # This document was kept in the deduplicated set
        topics_for_all.append(index_to_topic[idx])
    else:
        # This document was removed as a duplicate - get topic from its representative
        rep_idx = duplicate_map[idx]
        topics_for_all.append(index_to_topic[rep_idx])

data['topic'] = topics_for_all
```

## How It Works

Fuzzy deduplication uses the SequenceMatcher algorithm from Python's difflib to calculate text similarity ratios between documents:

1. Each document is compared with others to find similarity above a threshold (e.g., 85%)
2. Documents are grouped into similarity clusters
3. For each cluster, one representative document is kept and others are marked as duplicates
4. Topic modeling is performed only on the unique documents
5. Topic assignments are mapped back to all documents based on their representatives

## Key Parameters

When using the `fuzzy_deduplicate` function:

- `data`: Your dataset as a pandas DataFrame
- `text_column`: The column containing the document text
- `threshold`: Similarity threshold (0.0-1.0) where 1.0 means identical
  - 0.85-0.90: Detects documents with minor differences
  - 0.70-0.85: More aggressive deduplication, may group similar but distinct texts
  - 0.90-1.0: Conservative approach, only very similar documents are deduplicated

## Understanding the Results

The `fuzzy_deduplicate` function returns three elements:

1. `deduplicated_data`: DataFrame with only unique representative documents
2. `duplicate_map`: Dictionary mapping removed documents to their representatives
3. `fuzzy_groups`: List of DataFrames, each containing a group of similar documents

You can analyze these groups to understand what types of near-duplicates exist in your dataset.

## Performance Considerations

Fuzzy deduplication requires pairwise comparisons between documents, which can be computationally expensive for large datasets. Consider these optimization strategies:

- Apply to smaller datasets (< 10,000 documents) or use sampling for initial analysis
- Use exact deduplication first, then apply fuzzy deduplication to the remaining documents
- Implement batched processing for very large collections
- Consider preprocessing/normalizing text before comparison (lowercasing, removing punctuation)

## Example Use Cases

### Customer Feedback Analysis

Customer feedback often contains near-duplicates from different channels or with minor variations:

```python
# Identify feedback clusters
deduplicated_feedback, duplicate_map, feedback_groups = fuzzy_deduplicate(
    customer_feedback, 
    text_column="feedback_text",
    threshold=0.85
)

# Analyze representative feedback only
workflow.load_data(data=deduplicated_feedback, text_column="feedback_text")
```

### Document Collections

Document repositories often contain versioned documents with minor changes:

```python
# Find near-duplicate documents
deduplicated_docs, duplicate_map, doc_groups = fuzzy_deduplicate(
    document_collection, 
    text_column="content",
    threshold=0.90  # Higher threshold for more conservative grouping
)

# For each group, keep only the latest version
for group in doc_groups:
    # Sort by timestamp
    latest = group.sort_values('timestamp', ascending=False).iloc[0]
    print(f"Found {len(group)} versions of document: {latest['title']}")
```

### Survey Responses

Open-ended survey responses often contain near-identical answers:

```python
# Group similar responses
deduplicated_responses, duplicate_map, response_groups = fuzzy_deduplicate(
    survey_data, 
    text_column="response",
    threshold=0.80  # Lower threshold for more aggressive grouping
)

# Count how many respondents gave similar answers
for i, group in enumerate(response_groups):
    if len(group) > 3:  # Only look at common responses
        print(f"Response pattern {i+1} ({len(group)} respondents): {group.iloc[0]['response'][:100]}...")
```

## Visualizing Fuzzy Duplicate Groups

Meno provides utilities to visualize and analyze fuzzy duplicate groups:

```python
from meno.examples.fuzzy_deduplication_example import visualize_duplicate_groups

# Visualize duplicate distribution and topic consistency
visualize_duplicate_groups(
    data_with_topics,  # Your data with topic assignments
    fuzzy_groups,      # Groups from fuzzy_deduplicate
    output_dir="./visualizations"  # Optional output directory
)
```

## Integration with Other Optimizations

Fuzzy deduplication combines well with Meno's other optimization features:

```python
# Combine with memory optimization and incremental learning
from meno import MenoWorkflow
from meno.examples.fuzzy_deduplication_example import fuzzy_deduplicate
from meno.modeling.incremental import TopicUpdater

# Step 1: Deduplicate data
deduplicated_data, duplicate_map, _ = fuzzy_deduplicate(data, "text", threshold=0.85)

# Step 2: Create memory-optimized workflow
workflow = MenoWorkflow(
    config_overrides={
        "modeling": {
            "embeddings": {
                "precision": "float16",
                "use_mmap": True
            }
        }
    }
)

# Step 3: Process initial batch
workflow.load_data(data=deduplicated_data, text_column="text")
workflow.preprocess_documents()
workflow.discover_topics(method="bertopic", num_topics="auto")

# Step 4: Set up incremental learning for updates
model = workflow.modeler.model
updater = TopicUpdater(model=model)

# Step 5: Apply the same process to new data batches
# ... (process new data with fuzzy deduplication and incremental updates)
```

## Conclusion

Fuzzy deduplication enhances Meno's ability to handle real-world datasets by identifying and managing near-duplicate documents. By using this feature, you can:

1. Process data more efficiently
2. Create more accurate topic models 
3. Identify document clusters and patterns
4. Better understand content variations in your dataset

For more detailed examples and implementations, see `examples/fuzzy_deduplication_example.py` in the Meno repository.