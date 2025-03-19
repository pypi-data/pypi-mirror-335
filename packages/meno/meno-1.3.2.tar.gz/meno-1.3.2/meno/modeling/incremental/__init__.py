"""
Incremental topic modeling module.

This module provides functionality for incremental learning in topic modeling,
allowing models to be updated with new documents without full retraining.
"""

from .topic_updater import TopicUpdater, ModelUpdateMetadata

__all__ = ["TopicUpdater", "ModelUpdateMetadata"]