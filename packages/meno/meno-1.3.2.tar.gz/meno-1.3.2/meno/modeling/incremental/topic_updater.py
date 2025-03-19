"""
Module for incremental topic model updating.

This module provides functionality for updating topic models with new documents
without requiring full retraining, implementing various incremental learning
approaches for topic modeling.
"""

import logging
import pickle
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine

from ..bertopic_model import BERTopicModel
from ..base import BaseTopicModel
from ..embeddings import DocumentEmbedding


logger = logging.getLogger(__name__)


class ModelUpdateMetadata:
    """Class to track model update history and metadata."""
    
    def __init__(self):
        self.updates = []
        self.initial_training_date = datetime.now().isoformat()
        self.total_documents_processed = 0
        self.update_type_history = {}
        
    def record_update(self, 
                      num_documents: int, 
                      update_type: str,
                      topic_stability: float,
                      execution_time: float):
        """Record a model update event.
        
        Parameters
        ----------
        num_documents : int
            Number of documents in this update
        update_type : str
            Type of update ("incremental", "partial_retrain", "full_retrain")
        topic_stability : float
            Measure of topic stability (0-1, higher is more stable)
        execution_time : float
            Time taken for the update in seconds
        """
        update_info = {
            "timestamp": datetime.now().isoformat(),
            "num_documents": num_documents,
            "update_type": update_type,
            "topic_stability": topic_stability,
            "execution_time": execution_time
        }
        self.updates.append(update_info)
        self.total_documents_processed += num_documents
        
        # Update type counting
        if update_type not in self.update_type_history:
            self.update_type_history[update_type] = 0
        self.update_type_history[update_type] += 1
        
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the model update history.
        
        Returns
        -------
        Dict[str, Any]
            Summary of the model's update history
        """
        return {
            "initial_training_date": self.initial_training_date,
            "total_documents_processed": self.total_documents_processed,
            "number_of_updates": len(self.updates),
            "update_type_counts": self.update_type_history,
            "average_topic_stability": np.mean([u["topic_stability"] for u in self.updates]) if self.updates else None,
            "last_update": self.updates[-1] if self.updates else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary for serialization.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the metadata
        """
        return {
            "initial_training_date": self.initial_training_date,
            "total_documents_processed": self.total_documents_processed,
            "updates": self.updates,
            "update_type_history": self.update_type_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelUpdateMetadata':
        """Create a ModelUpdateMetadata instance from a dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing metadata
            
        Returns
        -------
        ModelUpdateMetadata
            New instance with the loaded data
        """
        metadata = cls()
        metadata.initial_training_date = data.get("initial_training_date", datetime.now().isoformat())
        metadata.total_documents_processed = data.get("total_documents_processed", 0)
        metadata.updates = data.get("updates", [])
        metadata.update_type_history = data.get("update_type_history", {})
        return metadata


class TopicUpdater:
    """Class for incrementally updating topic models with new documents."""
    
    def __init__(self, 
                 model: BaseTopicModel,
                 update_history: Optional[ModelUpdateMetadata] = None):
        """Initialize the TopicUpdater.
        
        Parameters
        ----------
        model : BaseTopicModel
            The topic model to update
        update_history : Optional[ModelUpdateMetadata], optional
            Existing update history, by default None
        """
        self.model = model
        self.update_history = update_history or ModelUpdateMetadata()
        self._validate_model()
        
    def _validate_model(self):
        """Verify the model supports incremental updates."""
        if not isinstance(self.model, BERTopicModel):
            logger.warning(
                f"Model type {type(self.model).__name__} may not fully support incremental updates. "
                "Only BERTopicModel is guaranteed to work with all update modes."
            )
            # In the future, could add checks for other model types that support updates
            
    def _calculate_topic_similarity(self, 
                                   original_topics: Dict[int, List[str]], 
                                   updated_topics: Dict[int, List[str]]) -> float:
        """Calculate similarity between original and updated topics.
        
        Parameters
        ----------
        original_topics : Dict[int, List[str]]
            Original topic-word mappings
        updated_topics : Dict[int, List[str]]
            Updated topic-word mappings
            
        Returns
        -------
        float
            Similarity score (0-1, higher is more similar)
        """
        # For topics that exist in both, compare word overlap
        similarity_scores = []
        
        # Get intersection of topic IDs
        common_topic_ids = set(original_topics.keys()) & set(updated_topics.keys())
        
        if not common_topic_ids:
            return 0.0  # No common topics
            
        for topic_id in common_topic_ids:
            original_words = set(original_topics[topic_id])
            updated_words = set(updated_topics[topic_id])
            
            # Calculate Jaccard similarity (set overlap)
            if original_words or updated_words:
                jaccard = len(original_words & updated_words) / len(original_words | updated_words)
                similarity_scores.append(jaccard)
                
        if not similarity_scores:
            return 0.0
            
        return np.mean(similarity_scores)
    
    def update_model(self,
                    documents: List[str],
                    document_ids: Optional[List[str]] = None,
                    embeddings: Optional[np.ndarray] = None,
                    update_mode: str = "incremental",
                    preserve_topic_ids: bool = True,
                    merge_similar_topics: bool = False,
                    similarity_threshold: float = 0.7,
                    sample_original_docs: bool = False,
                    sample_ratio: float = 0.1,
                    verbose: bool = False,
                    **kwargs) -> Tuple[BaseTopicModel, Dict[str, Any]]:
        """Update the topic model with new documents.
        
        Parameters
        ----------
        documents : List[str]
            New documents to update the model with
        document_ids : Optional[List[str]], optional
            IDs for the new documents, by default None
        embeddings : Optional[np.ndarray], optional
            Pre-computed embeddings for documents, by default None
        update_mode : str, optional
            Mode for update:
            - "incremental": Update topic representations without retraining
            - "partial_retrain": Retrain using new documents + sample of original
            - "full_retrain": Retrain from scratch with all documents
            By default "incremental"
        preserve_topic_ids : bool, optional
            Whether to preserve existing topic IDs, by default True
        merge_similar_topics : bool, optional
            Whether to merge similar topics after update, by default False
        similarity_threshold : float, optional
            Threshold for topic similarity when merging, by default 0.7
        sample_original_docs : bool, optional
            Whether to include a sample of original documents (for partial_retrain),
            by default False
        sample_ratio : float, optional
            Ratio of original documents to sample, by default 0.1
        verbose : bool, optional
            Whether to print verbose output, by default False
        **kwargs : optional
            Additional arguments for model-specific update behavior
            
        Returns
        -------
        Tuple[BaseTopicModel, Dict[str, Any]]
            Updated model and update statistics
        """
        if not documents:
            logger.warning("No documents provided for update, returning model unchanged")
            return self.model, {"success": False, "reason": "No documents provided"}
            
        start_time = time.time()
        
        # Save original topic information for comparison
        original_topic_info = None
        if hasattr(self.model, 'topic_representations_'):
            original_topic_info = self.model.topic_representations_.copy()
            
        # Document IDs handling
        if document_ids is None:
            # Create sequential IDs based on how many docs we've already processed
            base_id = self.update_history.total_documents_processed
            document_ids = [f"doc_{base_id + i}" for i in range(len(documents))]
        
        # Different update strategies
        if update_mode == "incremental":
            result = self._incremental_update(
                documents=documents,
                document_ids=document_ids,
                embeddings=embeddings,
                preserve_topic_ids=preserve_topic_ids,
                **kwargs
            )
        elif update_mode == "partial_retrain":
            result = self._partial_retrain(
                documents=documents,
                document_ids=document_ids, 
                embeddings=embeddings,
                sample_original_docs=sample_original_docs,
                sample_ratio=sample_ratio,
                **kwargs
            )
        elif update_mode == "full_retrain":
            result = self._full_retrain(
                new_documents=documents,
                new_document_ids=document_ids,
                new_embeddings=embeddings,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown update_mode: {update_mode}. "
                             "Expected 'incremental', 'partial_retrain', or 'full_retrain'")
        
        # Optional topic merging if requested
        if merge_similar_topics and hasattr(self.model, 'topic_representations_'):
            self._merge_similar_topics(similarity_threshold)
            
        # Calculate topic stability
        topic_stability = 0.0
        if original_topic_info is not None and hasattr(self.model, 'topic_representations_'):
            topic_stability = self._calculate_topic_similarity(
                original_topic_info, 
                self.model.topic_representations_
            )
        
        # Record update in history
        execution_time = time.time() - start_time
        self.update_history.record_update(
            num_documents=len(documents),
            update_type=update_mode,
            topic_stability=topic_stability,
            execution_time=execution_time
        )
        
        # Compile stats
        update_stats = {
            "success": True,
            "update_mode": update_mode,
            "num_documents": len(documents),
            "execution_time": execution_time,
            "topic_stability": topic_stability,
            "model_specific_results": result
        }
        
        if verbose:
            logger.info(f"Model updated with {len(documents)} documents using {update_mode} mode")
            logger.info(f"Topic stability: {topic_stability:.2f}")
            logger.info(f"Update took {execution_time:.2f} seconds")
            
        return self.model, update_stats
    
    def _incremental_update(self,
                           documents: List[str],
                           document_ids: List[str],
                           embeddings: Optional[np.ndarray] = None,
                           preserve_topic_ids: bool = True,
                           **kwargs) -> Dict[str, Any]:
        """Update topic model incrementally without full retraining.
        
        Parameters
        ----------
        documents : List[str]
            New documents to update with
        document_ids : List[str]
            IDs for the new documents
        embeddings : Optional[np.ndarray], optional
            Pre-computed embeddings for documents, by default None
        preserve_topic_ids : bool, optional
            Whether to preserve existing topic IDs, by default True
        **kwargs : optional
            Additional arguments for model-specific update behavior
            
        Returns
        -------
        Dict[str, Any]
            Update statistics
        """
        result = {}
        
        # Handle BERTopic model
        if isinstance(self.model, BERTopicModel):
            # Get or create embeddings
            if embeddings is None:
                embeds = self.model.embedding_model.embed_documents(documents)
            else:
                embeds = embeddings
                
            # Get document-topic assignments 
            doc_topics, _ = self.model.transform(documents, embeds)
            
            # Update topics with new documents
            self.model.update_topics(
                documents=documents, 
                topics=doc_topics, 
                embeddings=embeds,
                **kwargs
            )
            
            result.update({
                "num_topics_before": len(self.model.topic_sizes_),
                "num_topics_after": len(self.model.topic_sizes_),
                "used_embeddings": embeddings is not None
            })
            
        else:
            # Generic fallback for other model types - less efficient
            logger.warning(f"Full incremental update not available for {type(self.model).__name__}, "
                          "using basic document addition")
            
            # Add documents to model's document store
            if hasattr(self.model, 'documents'):
                # Get or create embeddings
                if embeddings is None and hasattr(self.model, 'embedding_model'):
                    embeds = self.model.embedding_model.embed_documents(documents)
                else:
                    embeds = embeddings
                    
                # Try to infer topics for new documents
                if hasattr(self.model, 'transform'):
                    doc_topics, _ = self.model.transform(documents, embeds)
                    
                    # Extend document storage
                    for i, (doc, doc_id, topic) in enumerate(zip(documents, document_ids, doc_topics)):
                        if isinstance(self.model.documents, pd.DataFrame):
                            # Create new row with appropriate columns
                            if embeds is not None:
                                embedding_col = self.model.documents.columns.intersection(['embedding', 'embeddings']).tolist()
                                if embedding_col:
                                    row_data = {
                                        'document': doc,
                                        'id': doc_id,
                                        'topic': topic,
                                        embedding_col[0]: embeds[i] if embeds is not None else None
                                    }
                                    # Append to the dataframe
                                    self.model.documents = pd.concat([
                                        self.model.documents, 
                                        pd.DataFrame([row_data])
                                    ], ignore_index=True)
            
            result["basic_document_addition"] = True
            
        return result
    
    def _partial_retrain(self,
                        documents: List[str],
                        document_ids: List[str],
                        embeddings: Optional[np.ndarray] = None,
                        sample_original_docs: bool = True,
                        sample_ratio: float = 0.1,
                        **kwargs) -> Dict[str, Any]:
        """Retrain model with new documents and a sample of original documents.
        
        Parameters
        ----------
        documents : List[str]
            New documents to update with
        document_ids : List[str]
            IDs for the new documents
        embeddings : Optional[np.ndarray], optional
            Pre-computed embeddings for documents, by default None
        sample_original_docs : bool, optional
            Whether to include a sample of original documents, by default True
        sample_ratio : float, optional
            Ratio of original documents to sample, by default 0.1
        **kwargs : optional
            Additional arguments for model-specific update behavior
            
        Returns
        -------
        Dict[str, Any]
            Update statistics
        """
        result = {}
        
        # Get sample of original documents if requested
        original_docs = []
        original_embeddings = None
        
        if sample_original_docs and hasattr(self.model, 'documents'):
            # Extract original documents and their embeddings
            if isinstance(self.model.documents, pd.DataFrame):
                # Calculate sample size
                sample_size = int(len(self.model.documents) * sample_ratio)
                if sample_size > 0:
                    # Sample from original documents
                    sample_indices = np.random.choice(
                        len(self.model.documents), 
                        size=min(sample_size, len(self.model.documents)), 
                        replace=False
                    )
                    
                    # Get documents from the sample
                    doc_col = [col for col in self.model.documents.columns if col.lower() in 
                              ['document', 'text', 'content']][0]
                    original_docs = self.model.documents.iloc[sample_indices][doc_col].tolist()
                    
                    # Try to get embeddings if available
                    embedding_cols = [col for col in self.model.documents.columns if col.lower() in 
                                    ['embedding', 'embeddings']]
                    if embedding_cols:
                        # Get embeddings from the sample
                        orig_embeds = self.model.documents.iloc[sample_indices][embedding_cols[0]].tolist()
                        if orig_embeds and hasattr(orig_embeds[0], 'shape'):
                            original_embeddings = np.vstack(orig_embeds)
        
        # Combine new and sampled original documents
        combined_docs = original_docs + documents
        combined_ids = ([f"orig_{i}" for i in range(len(original_docs))] + 
                        document_ids)
        
        # Combine embeddings if both are available
        combined_embeddings = None
        if embeddings is not None and original_embeddings is not None:
            combined_embeddings = np.vstack([original_embeddings, embeddings])
        elif embeddings is not None:
            combined_embeddings = embeddings
            
        # Handle BERTopic model using its update capabilities
        if isinstance(self.model, BERTopicModel):
            # Get or create embeddings for combined docs
            if combined_embeddings is None:
                combined_embeds = self.model.embedding_model.embed_documents(combined_docs)
            else:
                combined_embeds = combined_embeddings
                
            # Get current topic representations for reference
            original_topics = None
            if hasattr(self.model, 'topic_representations_'):
                original_topics = self.model.topic_representations_.copy()
                
            # Update model with all documents
            self.model.update_topics(
                documents=combined_docs,
                embeddings=combined_embeds,
                vectorizer_model="default",  # Use existing vectorizer
                ctfidf_model="default",      # Use existing ctfidf model
                representation_model="default",  # Use existing representation model
                calculate_probabilities=kwargs.get("calculate_probabilities", False)
            )
            
            result.update({
                "num_original_docs_used": len(original_docs),
                "percent_original_data": len(original_docs) / (len(self.model.documents) or 1) * 100,
                "total_docs_for_update": len(combined_docs)
            })
            
        else:
            # Generic fallback for other model types
            logger.warning(f"Partial retrain not optimized for {type(self.model).__name__}, "
                          "applying basic update")
            
            # Add documents to model's document store
            if hasattr(self.model, 'documents'):
                # Skip original docs if we can't properly retrain
                # and just add the new ones
                self._incremental_update(
                    documents=documents,
                    document_ids=document_ids,
                    embeddings=embeddings,
                    **kwargs
                )
                
                result["applied_basic_update"] = True
                
        return result
    
    def _full_retrain(self,
                     new_documents: List[str],
                     new_document_ids: List[str],
                     new_embeddings: Optional[np.ndarray] = None,
                     **kwargs) -> Dict[str, Any]:
        """Fully retrain model with all documents.
        
        Parameters
        ----------
        new_documents : List[str]
            New documents to add
        new_document_ids : List[str]
            IDs for the new documents
        new_embeddings : Optional[np.ndarray], optional
            Pre-computed embeddings for new documents, by default None
        **kwargs : optional
            Additional arguments for model-specific behavior
            
        Returns
        -------
        Dict[str, Any]
            Update statistics
        """
        result = {}
        
        # Extract all original documents and embeddings
        original_docs = []
        original_ids = []
        original_embeddings = None
        
        if hasattr(self.model, 'documents'):
            # Extract original documents
            if isinstance(self.model.documents, pd.DataFrame):
                # Get documents
                doc_col = [col for col in self.model.documents.columns if col.lower() in 
                          ['document', 'text', 'content']][0]
                original_docs = self.model.documents[doc_col].tolist()
                
                # Get IDs
                id_col = [col for col in self.model.documents.columns if col.lower() in 
                         ['id', 'document_id']][0]
                original_ids = self.model.documents[id_col].tolist()
                
                # Try to get embeddings if available
                embedding_cols = [col for col in self.model.documents.columns if col.lower() in 
                                ['embedding', 'embeddings']]
                if embedding_cols:
                    # Check if embeddings are stored directly
                    orig_embeds = self.model.documents[embedding_cols[0]].tolist()
                    if orig_embeds and hasattr(orig_embeds[0], 'shape'):
                        original_embeddings = np.vstack(orig_embeds)
        
        # Combine all documents
        all_docs = original_docs + new_documents
        all_ids = original_ids + new_document_ids
        
        # Combine embeddings if both are available
        all_embeddings = None
        if new_embeddings is not None and original_embeddings is not None:
            all_embeddings = np.vstack([original_embeddings, new_embeddings])
        
        # Handle BERTopic model
        if isinstance(self.model, BERTopicModel):
            # Save original settings
            original_settings = {}
            for key, value in self.model.__dict__.items():
                if key in ['embedding_model', 'umap_model', 'hdbscan_model', 
                          'vectorizer_model', 'ctfidf_model']:
                    original_settings[key] = value
            
            # Create and fit a new model instance with same parameters
            if all_embeddings is None:
                # Need to create embeddings for all documents
                all_embeddings = self.model.embedding_model.embed_documents(all_docs)
                
            # Fit model with all data
            self.model.fit(
                documents=all_docs,
                embeddings=all_embeddings,
                **kwargs
            )
            
            # Store original document IDs if needed
            if hasattr(self.model, 'documents') and isinstance(self.model.documents, pd.DataFrame):
                id_col = [col for col in self.model.documents.columns if col.lower() in 
                         ['id', 'document_id']][0]
                self.model.documents[id_col] = all_ids
            
            result.update({
                "num_original_docs": len(original_docs),
                "num_new_docs": len(new_documents),
                "total_docs": len(all_docs)
            })
            
        else:
            # Generic fallback for other model types
            logger.warning(f"Full retrain not implemented for {type(self.model).__name__}, "
                          "using incremental update")
            
            # Fall back to incremental update
            self._incremental_update(
                documents=new_documents,
                document_ids=new_document_ids,
                embeddings=new_embeddings,
                **kwargs
            )
            
            result["used_fallback_incremental"] = True
        
        return result
    
    def _merge_similar_topics(self, similarity_threshold: float = 0.7) -> None:
        """Merge topics that are very similar to each other.
        
        Parameters
        ----------
        similarity_threshold : float, optional
            Threshold for considering topics as similar, by default 0.7
        """
        # Verify model has topic representations
        if not hasattr(self.model, 'topic_representations_') or not self.model.topic_representations_:
            logger.warning("Cannot merge topics - no topic representations available")
            return
            
        # Only BERTopic models fully support this operation
        if not isinstance(self.model, BERTopicModel):
            logger.warning(f"Topic merging not implemented for {type(self.model).__name__}")
            return
            
        # Create similarity matrix between topics
        topic_ids = list(self.model.topic_representations_.keys())
        topic_words = [self.model.topic_representations_[topic] for topic in topic_ids]
        
        # Convert words to sets for faster comparison
        topic_word_sets = [set(words) for words in topic_words]
        
        # Find pairs of similar topics
        merge_candidates = []
        for i, topic_i in enumerate(topic_ids):
            for j, topic_j in enumerate(topic_ids[i+1:], i+1):
                # Skip if either topic is -1 (noise)
                if topic_i == -1 or topic_j == -1:
                    continue
                    
                # Calculate Jaccard similarity
                words_i = topic_word_sets[i]
                words_j = topic_word_sets[j]
                
                if words_i and words_j:  # Skip empty topics
                    similarity = len(words_i.intersection(words_j)) / len(words_i.union(words_j))
                    
                    if similarity >= similarity_threshold:
                        merge_candidates.append((topic_i, topic_j, similarity))
        
        # Sort by similarity (highest first)
        merge_candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Keep track of topics already merged
        merged_topics = set()
        topic_mapping = {}
        
        # Process merge candidates
        for topic_i, topic_j, similarity in merge_candidates:
            # Skip if either topic has already been merged
            if topic_i in merged_topics or topic_j in merged_topics:
                continue
                
            # Choose larger topic as the one to keep
            size_i = self.model.topic_sizes_.get(topic_i, 0)
            size_j = self.model.topic_sizes_.get(topic_j, 0)
            
            if size_i >= size_j:
                keep, remove = topic_i, topic_j
            else:
                keep, remove = topic_j, topic_i
                
            # Mark as merged and record mapping
            merged_topics.add(remove)
            topic_mapping[remove] = keep
        
        # Apply topic merging if any candidates were found
        if topic_mapping:
            if hasattr(self.model, 'merge_topics'):
                # Use BERTopic's built-in merge_topics function
                self.model.merge_topics(self.model.documents, topic_mapping)
                logger.info(f"Merged {len(topic_mapping)} similar topics")
            else:
                logger.warning("Model doesn't support topic merging")
    
    def save(self, path: str) -> None:
        """Save the updater's state and metadata.
        
        Parameters
        ----------
        path : str
            Path to save the data
        """
        # Create a dictionary with all the data to save
        save_data = {
            "update_history": self.update_history.to_dict(),
            # Don't save the model - that should be done separately
        }
        
        with open(path, 'wb') as f:
            pickle.dump(save_data, f)
            
    @classmethod
    def load(cls, path: str, model: BaseTopicModel) -> 'TopicUpdater':
        """Load a TopicUpdater from a file.
        
        Parameters
        ----------
        path : str
            Path to the saved updater data
        model : BaseTopicModel
            Topic model to use with the updater
            
        Returns
        -------
        TopicUpdater
            Loaded TopicUpdater instance
        """
        with open(path, 'rb') as f:
            save_data = pickle.load(f)
            
        # Recreate update history
        update_history = ModelUpdateMetadata.from_dict(save_data["update_history"])
        
        # Create and return the updater
        return cls(model=model, update_history=update_history)