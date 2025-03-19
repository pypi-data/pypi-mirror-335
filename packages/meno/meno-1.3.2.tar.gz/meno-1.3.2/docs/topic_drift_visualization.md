# Topic Drift Visualization in Meno

This document explains how to visualize and monitor topic drift over time when using incremental learning in Meno.

## Overview

When using Meno's incremental learning capabilities to update topic models with new data, the topics themselves may evolve or "drift" over time. Understanding this drift is crucial for:

1. Monitoring topic stability and consistency
2. Identifying emerging themes and concepts
3. Tracking changes in document-topic distributions
4. Validating the effectiveness of incremental updates

Meno provides specialized visualizations to help track and analyze topic drift in models that evolve over time.

## Quick Start

```python
from meno import MenoWorkflow
from meno.modeling.incremental import TopicUpdater
from meno.examples.optimized_incremental_workflow import visualize_topic_drift

# Create and train initial model
workflow = MenoWorkflow()
workflow.load_data(data=initial_data, text_column="text")
workflow.preprocess_documents()
workflow.discover_topics(method="bertopic", num_topics="auto")

# Get the model and create a topic updater
model = workflow.modeler.model
topic_updater = TopicUpdater(model=model)

# Perform incremental updates
for update_batch in update_batches:
    update_docs = update_batch["text"].tolist()
    update_ids = update_batch["id"].tolist()
    
    # Update model
    model, stats = topic_updater.update_model(
        documents=update_docs,
        document_ids=update_ids,
        update_mode="incremental"
    )

# Generate visualizations
visualize_topic_drift(
    topic_updater=topic_updater,
    model=model,
    output_dir="./drift_visualizations"
)
```

## Key Visualizations

Meno provides several visualizations for understanding topic drift:

### 1. Topic Stability Over Time

This line chart shows how topic stability (similarity between topic representations before and after updates) changes with each model update:

```python
# Generate stability chart
plt.figure(figsize=(10, 6))
    
# Extract data from update history
timestamps = [i for i in range(1, len(update_history.updates) + 1)]
stability = [u["topic_stability"] for u in update_history.updates]
    
plt.plot(timestamps, stability, marker='o', linestyle='-')
plt.xlabel('Update Number')
plt.ylabel('Topic Stability (0-1)')
plt.title('Topic Stability Over Time')
```

### 2. Topic Similarity Heatmap

This interactive heatmap shows similarity relationships between topics, helping identify which topics are closely related:

```python
from meno.visualization.enhanced_viz.interactive_viz import create_topic_similarity_heatmap

# Generate heatmap
fig = create_topic_similarity_heatmap(
    model, 
    min_topic=-1,  # Include noise topic
    return_figure=True
)

# Save as interactive HTML
fig.write_html("topic_similarity_heatmap.html")
```

### 3. Topic Size Evolution

This chart shows how the size of topics (number of documents assigned) changes over time:

```python
# Top topics by size
topic_sizes = {k: v for k, v in model.topic_sizes_.items() if k != -1}
top_topics = sorted(topic_sizes.items(), key=lambda x: x[1], reverse=True)[:10]

# Plot sizes
plt.figure(figsize=(12, 6))
plt.bar(range(len(top_topics)), [t[1] for t in top_topics])
plt.xticks(range(len(top_topics)), [str(t[0]) for t in top_topics])
plt.xlabel('Topic ID')
plt.ylabel('Number of Documents')
plt.title('Top Topics by Size')
```

### 4. Word Distribution Changes

These visualizations show how the key words in each topic have evolved:

```python
# For top topics
for topic_id in top_topic_ids:
    words = model.topic_representations_[topic_id]
    plt.figure(figsize=(10, 4))
    plt.barh(range(len(words)), [1] * len(words))
    plt.yticks(range(len(words)), words)
    plt.title(f'Topic {topic_id} Word Distribution')
```

## Understanding Topic Stability Metrics

Topic stability is measured on a scale from 0 to 1:

- **1.0**: Topics are completely stable (identical before and after update)
- **0.8-0.9**: High stability - topics evolved slightly but core concepts remain
- **0.5-0.7**: Moderate stability - significant evolution in topics
- **< 0.5**: Low stability - major shifts in topic structure

Different update modes have different stability characteristics:
- **Incremental updates**: Typically maintain higher stability
- **Partial retraining**: Balanced approach with moderate stability
- **Full retraining**: May result in lower stability but potentially better quality

## Example: Tracking Emerging Topics

This example shows how to identify newly emerging topics after incremental updates:

```python
# Get initial topics
initial_topics = model.get_topic_info()
initial_topic_ids = set(initial_topics['Topic'].values)

# Perform incremental update
model, stats = topic_updater.update_model(
    documents=new_docs,
    document_ids=new_ids,
    update_mode="incremental"
)

# Get updated topics
updated_topics = model.get_topic_info()
updated_topic_ids = set(updated_topics['Topic'].values)

# Find new topics
new_topic_ids = updated_topic_ids - initial_topic_ids
print(f"New topics: {new_topic_ids}")

# Examine words in new topics
for topic_id in new_topic_ids:
    words = model.topic_representations_[topic_id]
    print(f"New topic {topic_id}: {', '.join(words[:10])}")
```

## Advanced: Temporal Topic Evolution

For more advanced visualization of topic evolution over time, Meno provides specialized plots:

```python
from meno.visualization.enhanced_viz.comparative_viz import create_topic_evolution_chart

# Create time-based comparison
evolution_chart = create_topic_evolution_chart(
    model,
    time_periods=["2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4"],
    document_dates=dates,  # List of dates for each document
    top_n_topics=5
)
```

## Integrating With Other Optimizations

Topic drift visualization integrates well with Meno's other optimization features:

```python
# Complete workflow example
from meno import MenoWorkflow
from meno.modeling.incremental import TopicUpdater
from meno.examples.optimized_incremental_workflow import visualize_topic_drift

# Create memory-optimized workflow
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

# Load deduplicated data
workflow.load_data(data=deduplicated_data, text_column="text", deduplicate=True)
workflow.preprocess_documents()
workflow.discover_topics(method="bertopic", num_topics="auto")

# Set up for incremental updates
model = workflow.modeler.model
topic_updater = TopicUpdater(model=model)

# Process updates
for update_batch in update_batches:
    # Deduplicate update batch
    update_batch_deduped = update_batch.drop_duplicates(subset=["text"])
    
    # Update model
    model, stats = topic_updater.update_model(
        documents=update_batch_deduped["text"].tolist(),
        document_ids=update_batch_deduped["id"].tolist(),
        update_mode="incremental"
    )
    
    # After each update, you can visualize current state
    current_stability = stats["topic_stability"]
    print(f"Update stability: {current_stability:.2f}")

# Generate comprehensive visualizations at the end
visualize_topic_drift(topic_updater, model, "./output_visualizations")
```

## Practical Applications

### Content Trend Analysis

Tracking how topics evolve over time can reveal trends in content:

```python
# Create time periods for analysis
time_periods = [
    {"start": "2022-01-01", "end": "2022-03-31", "name": "Q1"},
    {"start": "2022-04-01", "end": "2022-06-30", "name": "Q2"},
    {"start": "2022-07-01", "end": "2022-09-30", "name": "Q3"},
    {"start": "2022-10-01", "end": "2022-12-31", "name": "Q4"}
]

# After incremental updates, analyze dominant topics per period
for period in time_periods:
    # Filter documents for this period
    period_docs = all_documents[
        (all_documents["date"] >= period["start"]) & 
        (all_documents["date"] <= period["end"])
    ]
    
    # Count topics
    topic_counts = period_docs["topic"].value_counts()
    top_topic = topic_counts.index[0]
    
    # Get words for top topic
    topic_words = model.topic_representations_[top_topic]
    
    print(f"{period['name']} dominant topic: {top_topic} ({', '.join(topic_words[:5])})")
```

### Emerging Topic Alerts

Set up alerts for when new topics emerge or existing topics change significantly:

```python
def check_for_significant_changes(previous_model, current_model, threshold=0.5):
    """Detect significant changes in topics."""
    changes = []
    
    # Check existing topics
    for topic_id in previous_model.topic_representations_:
        if topic_id == -1:  # Skip noise topic
            continue
            
        if topic_id in current_model.topic_representations_:
            # Calculate word overlap
            prev_words = set(previous_model.topic_representations_[topic_id])
            curr_words = set(current_model.topic_representations_[topic_id])
            
            overlap = len(prev_words & curr_words) / len(prev_words | curr_words)
            
            if overlap < threshold:
                changes.append({
                    "type": "modified",
                    "topic_id": topic_id,
                    "overlap": overlap,
                    "previous_words": previous_model.topic_representations_[topic_id][:5],
                    "current_words": current_model.topic_representations_[topic_id][:5]
                })
    
    # Check for new topics
    prev_topics = set(previous_model.topic_representations_.keys())
    curr_topics = set(current_model.topic_representations_.keys())
    new_topics = curr_topics - prev_topics
    
    for topic_id in new_topics:
        if topic_id != -1:  # Skip noise topic
            changes.append({
                "type": "new",
                "topic_id": topic_id,
                "words": current_model.topic_representations_[topic_id][:5]
            })
    
    return changes
```

## Conclusion

Topic drift visualization provides critical insights when using incremental learning in Meno. By monitoring how topics evolve, you can:

1. Ensure model stability and consistency over time
2. Detect emerging themes and trends
3. Track the impact of new data on existing topic structures
4. Make informed decisions about when to use different update strategies

These visualizations are especially valuable for ongoing analysis of streaming data, periodic data updates, and longitudinal studies of content evolution.

For complete examples and implementations, see `examples/optimized_incremental_workflow.py` in the Meno repository.