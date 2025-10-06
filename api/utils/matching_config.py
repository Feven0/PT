"""
Configuration for the Structured Question-Answer Matching System

This file contains configuration parameters for the robust matching system
that replaces LLM-based question-answer matching.
"""

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, lightweight sentence transformer
SIMILARITY_THRESHOLD = 0.3  # Minimum cosine similarity for potential matches
RELEVANCE_THRESHOLD = 60   # Minimum relevance score (0-100) for valid matches

# Answer Segmentation Configuration
MIN_ANSWER_LENGTH = 20     # Minimum length for answer segments
MAX_ANSWER_LENGTH = 1000   # Maximum length for answer segments

# Delimiter patterns for answer segmentation
ANSWER_DELIMITERS = [
    r'\.\s+(?=[A-Z])',     # Period followed by capital letter
    r'\.\s*$',             # Period at end of line
    r'\?\s+',              # Question mark
    r'!\s+',               # Exclamation mark
    r'\n\s*\n',            # Double newlines
    r'\.\s*My\s+',         # "My" after period (common in interviews)
    r'\.\s*I\s+',          # "I" after period
    r'\.\s*So\s+',         # "So" after period
    r'\.\s*Well\s+',       # "Well" after period
]

# Text Cleaning Configuration
REMOVE_FILLER_WORDS = True
FILLER_WORDS = ['um', 'uh', 'er', 'ah', 'like', 'you know', 'basically']

# Scoring Configuration
SCORE_RANGES = {
    'very_strong': (90, 100),
    'strong': (80, 89),
    'acceptable': (60, 79),
    'weak': (0, 59)
}

# Fallback Configuration
ENABLE_LLM_FALLBACK = True  # Enable fallback to LLM-based matching
FALLBACK_ON_ERROR = True    # Use fallback when structured matching fails

# Logging Configuration
LOG_MATCHING_DETAILS = True
LOG_SIMILARITY_MATRIX = False  # Can be verbose for large datasets
LOG_SEGMENTATION_DETAILS = True

