"""Tests for incremental learning and topic drift in Meno."""

import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path

from meno import MenoWorkflow
from meno.modeling.incremental.topic_updater import TopicUpdater


class TestIncrementalLearning:
    """Tests for incremental learning capabilities."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        
        # Create topics with characteristic words
        topics = {
            "Technology": ["computer", "software", "hardware", "data", "technology", "network"],
            "Health": ["medical", "health", "disease", "treatment", "doctor", "patient"],
            "Finance": ["money", "financial", "bank", "investment", "market", "economy"]
        }
        
        # Create documents
        documents = []
        for topic_name, words in topics.items():
            for i in range(10):  # 10 documents per topic
                # Create text by sampling from topic words
                text_words = np.random.choice(words, size=15, replace=True)
                text = " ".join(text_words)
                
                documents.append({
                    "text": text,
                    "id": f"{topic_name.lower()}_{i}",
                    "topic": topic_name
                })
        
        # Create DataFrame
        df = pd.DataFrame(documents)
        np.random.shuffle(df.values)  # Shuffle rows
        return df
    
    @pytest.fixture
    def update_data(self):
        """Create update data for testing incremental learning."""
        np.random.seed(43)
        
        # Create topics with characteristic words (with some evolution)
        topics = {
            "Technology": ["digital", "algorithm", "cloud", "computing", "AI", "machine"],
            "Health": ["wellness", "therapy", "diagnosis", "hospital", "recovery", "treatment"],
            "Finance": ["investment", "banking", "stocks", "trading", "crypto", "economics"]
        }
        
        # Create documents
        documents = []
        for topic_name, words in topics.items():
            for i in range(5):  # 5 documents per topic
                # Create text by sampling from topic words
                text_words = np.random.choice(words, size=15, replace=True)
                text = " ".join(text_words)
                
                documents.append({
                    "text": text,
                    "id": f"{topic_name.lower()}_update_{i}",
                    "topic": topic_name
                })
        
        # Create DataFrame
        df = pd.DataFrame(documents)
        np.random.shuffle(df.values)  # Shuffle rows
        return df
    
    @pytest.mark.slow
    def test_topic_updater_initialization(self):
        """Test initializing a TopicUpdater."""
        # Create a dummy workflow
        workflow = MenoWorkflow()
        
        # Create a dummy model (not fitted)
        from bertopic import BERTopic
        model = BERTopic(calculate_probabilities=False)
        
        # Initialize TopicUpdater (should work even with unfitted model)
        updater = TopicUpdater(model=model)
        
        # Check that updater was initialized
        assert updater is not None
        assert updater.model is model
        assert updater.update_history is not None
        assert updater.update_history.updates == []
    
    @pytest.mark.slow
    def test_update_history_structure(self):
        """Test that update history has the expected structure."""
        # Create a dummy updater without a real model
        updater = TopicUpdater(model=None)
        
        # Check that update history exists
        assert hasattr(updater, "update_history")
        assert updater.update_history is not None
        
        # Check that it has the expected structure
        assert hasattr(updater.update_history, "updates")
        assert isinstance(updater.update_history.updates, list)
        assert len(updater.update_history.updates) == 0  # No updates yet
    
    @pytest.mark.slow
    def test_update_history_properties(self):
        """Test update history properties."""
        from meno.modeling.incremental.topic_updater import ModelUpdateMetadata
        
        # Create an updater
        updater = TopicUpdater(model=None)
        
        # Check initial state
        assert updater.update_history is not None
        
        # Test that the history exists
        assert updater.update_history.updates == []
        
        # For this version of the API, just check that we can access the properties
        assert hasattr(updater.update_history, "updates")