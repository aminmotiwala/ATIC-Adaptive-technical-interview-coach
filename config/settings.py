"""
ATIC Configuration Settings
Author: Amin Motiwala

Centralized configuration management for the Adaptive Technical Interview Coach.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ATICSettings:
    """
    Centralized configuration settings for ATIC.
    
    This class manages all configuration parameters including:
    - API credentials and keys
    - Model configurations
    - System limits and timeouts
    - File paths and directories
    - Feature flags
    """
    
    # Project Information
    PROJECT_NAME = "Adaptive Technical Interview Coach"
    PROJECT_VERSION = "1.0.0"
    AUTHOR = "Amin Motiwala"
    
    # Kaggle Competition Details
    KAGGLE_TRACK = "Agents for Good"  # or "Concierge Agents"
    COMPETITION_FOCUS = "Adaptive learning and improving interview outcomes"
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    
    # Model Configuration (Gemini for 5-point bonus)
    DEFAULT_MODEL = "gemini-2.5-flash-lite"
    MODEL_TEMPERATURE = 0.7
    MODEL_MAX_TOKENS = 2048
    MODEL_TIMEOUT_SECONDS = 30
    
    # Code Execution Configuration
    CODE_EXECUTION_TIMEOUT = 10  # seconds
    CODE_EXECUTION_MAX_MEMORY_MB = 128
    SUPPORTED_LANGUAGES = ["python", "java"]
    
    # Search Configuration
    SEARCH_MAX_RESULTS = 10
    SEARCH_TIMEOUT_SECONDS = 10
    SEARCH_RATE_LIMIT_PER_MINUTE = 30
    
    # Session Configuration
    SESSION_MAX_DURATION_MINUTES = 90
    SESSION_QUESTION_TIMEOUT_MINUTES = 15
    MAX_CONCURRENT_SESSIONS = 5
    
    # Memory Bank Configuration
    DATABASE_PATH = Path(__file__).parent.parent / "memory" / "data" / "atic_memory.db"
    BACKUP_INTERVAL_HOURS = 24
    DATA_RETENTION_DAYS = 365
    
    # Difficulty Levels
    DIFFICULTY_LEVELS = {
        "beginner": {
            "complexity_score": 1,
            "time_multiplier": 1.5,
            "hint_availability": "high"
        },
        "intermediate": {
            "complexity_score": 2,
            "time_multiplier": 1.0,
            "hint_availability": "medium"
        },
        "advanced": {
            "complexity_score": 3,
            "time_multiplier": 0.8,
            "hint_availability": "low"
        }
    }
    
    # Performance Scoring Configuration
    SCORING_WEIGHTS = {
        "problem_solving": 0.25,
        "technical_knowledge": 0.20,
        "code_quality": 0.20,
        "communication": 0.15,
        "system_design": 0.15,
        "time_management": 0.05
    }
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_PATH = Path(__file__).parent.parent / "logs" / "atic.log"
    
    # Security Configuration
    ENABLE_CODE_SECURITY_CHECKS = True
    MAX_CODE_LENGTH_CHARS = 5000
    BLOCKED_CODE_PATTERNS = [
        "import os", "import subprocess", "exec(", "eval(",
        "__import__", "open(", "delete", "remove", "Runtime.getRuntime"
    ]
    
    # Feature Flags
    ENABLE_REAL_TIME_SEARCH = True
    ENABLE_CODE_EXECUTION = True
    ENABLE_PERFORMANCE_ANALYTICS = True
    ENABLE_SESSION_RECORDING = True
    ENABLE_ADAPTIVE_DIFFICULTY = True
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """
        Validate the current configuration and return validation results.
        
        Returns:
            Dict containing validation results and any issues found
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "missing_optional": []
        }
        
        # Check required API keys for core functionality
        if not cls.GEMINI_API_KEY:
            validation_results["errors"].append("GEMINI_API_KEY is required for core agent functionality")
            validation_results["is_valid"] = False
        
        # Check optional API keys
        if not cls.GOOGLE_SEARCH_API_KEY:
            validation_results["missing_optional"].append("GOOGLE_SEARCH_API_KEY - Search functionality will be limited")
        
        if not cls.GOOGLE_SEARCH_ENGINE_ID:
            validation_results["missing_optional"].append("GOOGLE_SEARCH_ENGINE_ID - Search functionality will be limited")
        
        # Validate file paths
        try:
            cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            validation_results["warnings"].append(f"Cannot create database directory: {e}")
        
        try:
            cls.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            validation_results["warnings"].append(f"Cannot create log directory: {e}")
        
        return validation_results
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration for ADK agents."""
        return {
            "name": cls.DEFAULT_MODEL,
            "api_key": cls.GEMINI_API_KEY,
            "temperature": cls.MODEL_TEMPERATURE,
            "max_tokens": cls.MODEL_MAX_TOKENS,
            "timeout": cls.MODEL_TIMEOUT_SECONDS
        }


# Create global settings instance
settings = ATICSettings()

# Validate configuration on import
validation_result = settings.validate_configuration()
if not validation_result["is_valid"]:
    print("⚠️ Configuration validation failed. Please check your settings.")
    for error in validation_result["errors"]:
        print(f"❌ {error}")
else:
    print("✅ ATIC configuration validated successfully")