"""Tests for topic drift visualization functionality."""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Skip tests if BERTopic is not available
try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False

# Skip tests if plotly is not available
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from meno.modeling.embeddings import DocumentEmbedding
from meno.modeling.incremental.topic_updater import TopicUpdater
import sys
from pathlib import Path

# Add examples directory to path
examples_path = Path('/Users/srepho/Downloads/ClaudeDev/meno/meno/examples')
if examples_path.exists() and examples_path not in sys.path:
    sys.path.append(str(examples_path))

from optimized_incremental_workflow import visualize_topic_drift


@pytest.mark.skipif(
    not (BERTOPIC_AVAILABLE and PLOTLY_AVAILABLE),
    reason="BERTopic and plotly are required for topic drift visualization tests"
)
class TestTopicDriftVisualization:
    """Tests for topic drift visualization functionality."""

    @pytest.fixture
    def sample_documents(self):
        """Create a sample document set for testing."""
        return [
            "This is a document about artificial intelligence.",
            "Machine learning models can help analyze text data.",
            "Natural language processing is a subfield of AI.",
            "Neural networks are used in deep learning.",
            "Topic modeling can identify themes in document collections.",
            "Transformers have revolutionized NLP tasks.",
            "BERT is a popular language model for embeddings.",
            "Clustering algorithms group similar documents together.",
            "Text classification assigns categories to documents.",
            "Word embeddings represent semantic relationships."
        ]

    @pytest.fixture
    def update_documents(self):
        """Create an update batch of documents for testing."""
        return [
            "GPT models generate human-like text responses.",
            "Fine-tuning adapts pre-trained models to specific tasks.",
            "Sentiment analysis determines emotional tone in text.",
            "Information retrieval systems find relevant documents.",
            "Question answering systems provide precise answers to queries."
        ]

    @pytest.fixture
    def embedding_model(self):
        """Create a small embedding model for testing."""
        return DocumentEmbedding(
            model_name="all-MiniLM-L6-v2",
            device="cpu"
        )

    @pytest.fixture
    def topic_updater_with_history(self, sample_documents, update_documents, embedding_model):
        """Create a topic updater with update history for testing."""
        # Get embeddings
        embeddings_initial = embedding_model.embed_documents(sample_documents)
        
        # Create a simple HDBSCAN-based BERTopic model
        from bertopic.vectorizers import ClassTfidfTransformer
        from sklearn.cluster import KMeans
        from sklearn.feature_extraction.text import CountVectorizer
        
        # Use a simpler configuration for testing
        model = BERTopic(
            nr_topics=5,
            vectorizer_model=CountVectorizer(stop_words="english"),
            ctfidf_model=ClassTfidfTransformer(reduce_frequent_words=True),
            hdbscan_model=KMeans(n_clusters=5, random_state=42),
            embedding_model=None,  # We'll provide embeddings directly
            verbose=False
        )
        
        # Fit the model
        document_ids = [f"doc_{i}" for i in range(len(sample_documents))]
        topics, probs = model.fit_transform(sample_documents, embeddings_initial)
        
        # Create updater
        topic_updater = TopicUpdater(model=model)
        
        # Add multiple updates
        update_modes = ["incremental", "partial_retrain", "full_retrain"]
        
        for i, mode in enumerate(update_modes):
            # Get embeddings for update
            update_embeddings = embedding_model.embed_documents(update_documents)
            
            # Perform update
            update_ids = [f"update{i}_{j}" for j in range(len(update_documents))]
            model, _ = topic_updater.update_model(
                documents=update_documents,
                document_ids=update_ids,
                embeddings=update_embeddings,
                update_mode=mode
            )
        
        return topic_updater

    def test_visualize_topic_drift(self, topic_updater_with_history, tmp_path):
        """Test topic drift visualization."""
        # Create output directory
        output_dir = tmp_path / "topic_drift_viz"
        output_dir.mkdir()
        
        # Generate visualizations
        visualize_topic_drift(
            topic_updater=topic_updater_with_history,
            model=topic_updater_with_history.model,
            output_dir=output_dir
        )
        
        # Check that visualization files were created
        assert (output_dir / "topic_stability_over_time.png").exists()
        assert (output_dir / "topic_similarity_heatmap.html").exists()
        
        # Check that other expected files exist
        assert (output_dir / "topic_sizes.png").exists()
        assert (output_dir / "topic_word_distribution.png").exists()

    def test_topic_stability_calculation(self, topic_updater_with_history):
        """Test that topic stability is correctly calculated in the update history."""
        # Get update history
        history = topic_updater_with_history.update_history
        
        # Check that stability scores are available for all updates
        for update in history.updates:
            assert "topic_stability" in update
            assert 0 <= update["topic_stability"] <= 1  # Stability should be between 0 and 1
        
        # Different update modes should have different stability values
        stability_values = [update["topic_stability"] for update in history.updates]
        update_modes = [update["update_mode"] for update in history.updates]
        
        # Make sure not all stability values are the same
        assert len(set(stability_values)) > 1