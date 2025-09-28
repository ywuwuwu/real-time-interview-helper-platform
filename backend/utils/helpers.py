import os
import re
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    """Utilities for processing text"""
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction - in production use NLP libraries
        # Remove common words
