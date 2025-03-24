"""
Jobrex Client - Python client for the Jobrex API.

This package provides a simple interface to interact with the Jobrex API,
which offers AI-powered recruitment services including resume parsing,
job matching, and more.
"""

__version__ = "0.1.0a2" 
from .client import ResumesClient, JobsClient

__all__ = ["ResumesClient", "JobsClient"]
