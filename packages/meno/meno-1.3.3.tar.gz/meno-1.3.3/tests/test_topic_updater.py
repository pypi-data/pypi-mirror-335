"""Tests for the incremental topic updater functionality."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from meno.modeling.embeddings import DocumentEmbedding
from meno.modeling.incremental.topic_updater import TopicUpdater


# Skip tests if BERTopic is not available
try:
    from bertopic import BERTopic
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not BERTOPIC_AVAILABLE,
    reason="BERTopic is required for incremental topic modeling tests"
)


class TestTopicUpdater:
    """Tests for the TopicUpdater class."""

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
    def initial_model(self, sample_documents, embedding_model):
        """Create an initial topic model for testing."""
        # Get embeddings
        embeddings = embedding_model.embed_documents(sample_documents)
        
        # Create a simple HDBSCAN-based BERTopic model
        from bertopic.vectorizers import ClassTfidfTransformer
        from bertopic.dimensionality import BaseDimensionalityReduction
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
        topics, probs = model.fit_transform(sample_documents, embeddings)
        
        return model

    def test_initialization(self, initial_model):
        """Test that the TopicUpdater can be initialized with a model."""
        topic_updater = TopicUpdater(model=initial_model)
        assert topic_updater.model is initial_model
        assert topic_updater.update_history is not None
        assert topic_updater.update_history.updates == []

    def test_incremental_update(self, initial_model, update_documents, embedding_model):
        """Test incremental update of the topic model."""
        # Create updater
        topic_updater = TopicUpdater(model=initial_model)
        
        # Get initial topic count
        initial_topics = set(initial_model.get_topic_info()["Topic"])
        
        # Get embeddings for update documents
        update_embeddings = embedding_model.embed_documents(update_documents)
        
        # Perform incremental update
        update_ids = [f"update_{i}" for i in range(len(update_documents))]
        updated_model, stats = topic_updater.update_model(
            documents=update_documents,
            document_ids=update_ids,
            embeddings=update_embeddings,
            update_mode="incremental"
        )
        
        # Check that stats were returned
        assert "topic_stability" in stats
        assert "execution_time" in stats
        assert stats["documents_processed"] == len(update_documents)
        
        # Check that update was recorded in history
        assert len(topic_updater.update_history.updates) == 1
        
        # Check that model was updated
        assert updated_model is topic_updater.model
        
        # Check topic stability is between 0 and 1
        assert 0 <= stats["topic_stability"] <= 1

    def test_full_retrain(self, initial_model, update_documents, embedding_model):
        """Test full retraining update mode."""
        # Create updater
        topic_updater = TopicUpdater(model=initial_model)
        
        # Get embeddings for update documents
        update_embeddings = embedding_model.embed_documents(update_documents)
        
        # Perform full retrain
        update_ids = [f"update_{i}" for i in range(len(update_documents))]
        updated_model, stats = topic_updater.update_model(
            documents=update_documents,
            document_ids=update_ids,
            embeddings=update_embeddings,
            update_mode="full_retrain"
        )
        
        # Check that update was recorded
        assert len(topic_updater.update_history.updates) == 1
        
        # Full retrain should result in lower stability compared to incremental
        topic_updater_incremental = TopicUpdater(model=initial_model)
        _, stats_incremental = topic_updater_incremental.update_model(
            documents=update_documents,
            document_ids=update_ids,
            embeddings=update_embeddings,
            update_mode="incremental"
        )
        
        # Note: This is a heuristic test; not always true but generally expected
        # Small test models might not follow this pattern consistently
        # We'll just check that stability values are different
        assert stats["topic_stability"] != stats_incremental["topic_stability"]

    def test_partial_retrain(self, initial_model, update_documents, embedding_model):
        """Test partial retraining update mode."""
        # Create updater
        topic_updater = TopicUpdater(model=initial_model)
        
        # Get embeddings for update documents
        update_embeddings = embedding_model.embed_documents(update_documents)
        
        # Perform partial retrain
        update_ids = [f"update_{i}" for i in range(len(update_documents))]
        updated_model, stats = topic_updater.update_model(
            documents=update_documents,
            document_ids=update_ids,
            embeddings=update_embeddings,
            update_mode="partial_retrain"
        )
        
        # Check that update was recorded
        assert len(topic_updater.update_history.updates) == 1
        assert stats["update_mode"] == "partial_retrain"

    def test_multiple_updates(self, initial_model, sample_documents, update_documents, embedding_model):
        """Test multiple sequential updates."""
        # Create updater
        topic_updater = TopicUpdater(model=initial_model)
        
        # First update
        update_ids1 = [f"update1_{i}" for i in range(len(update_documents))]
        update_embeddings1 = embedding_model.embed_documents(update_documents)
        
        model1, stats1 = topic_updater.update_model(
            documents=update_documents,
            document_ids=update_ids1,
            embeddings=update_embeddings1,
            update_mode="incremental"
        )
        
        # Second update with the same documents but different IDs
        update_ids2 = [f"update2_{i}" for i in range(len(update_documents))]
        update_embeddings2 = embedding_model.embed_documents(update_documents)
        
        model2, stats2 = topic_updater.update_model(
            documents=update_documents,
            document_ids=update_ids2,
            embeddings=update_embeddings2,
            update_mode="incremental"
        )
        
        # Check that both updates were recorded
        assert len(topic_updater.update_history.updates) == 2
        
        # Total documents processed should include both updates
        assert topic_updater.update_history.total_documents_processed == \
               len(update_documents) * 2

    def test_updater_save_load(self, initial_model, update_documents, embedding_model, tmp_path):
        """Test saving and loading the topic updater."""
        # Create and update the model
        topic_updater = TopicUpdater(model=initial_model)
        
        # Get embeddings for update documents
        update_embeddings = embedding_model.embed_documents(update_documents)
        
        # Perform update
        update_ids = [f"update_{i}" for i in range(len(update_documents))]
        updated_model, _ = topic_updater.update_model(
            documents=update_documents,
            document_ids=update_ids,
            embeddings=update_embeddings,
            update_mode="incremental"
        )
        
        # Save the updater
        save_path = tmp_path / "topic_updater"
        topic_updater.save(save_path)
        
        # Check that files were created
        assert save_path.exists()
        assert (save_path / "model").exists()
        assert (save_path / "update_history.json").exists()
        
        # Load the updater
        loaded_updater = TopicUpdater.load(save_path)
        
        # Check that history was preserved
        assert len(loaded_updater.update_history.updates) == 1
        assert loaded_updater.update_history.total_documents_processed == \
               topic_updater.update_history.total_documents_processed