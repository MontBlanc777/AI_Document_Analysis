import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

class Config:
    """Configuration class for the application"""
    
    # API settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # File upload settings
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"))
    
    # Model settings
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-pro-preview-05-06")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))
    TOP_P = float(os.getenv("TOP_P", 0.95))
    TOP_K = int(os.getenv("TOP_K", 40))
    MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", 8192))
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get the model configuration"""
        return {
            "temperature": cls.TEMPERATURE,
            "top_p": cls.TOP_P,
            "top_k": cls.TOP_K,
            "max_output_tokens": cls.MAX_OUTPUT_TOKENS,
        }
    
    @classmethod
    def get_safety_settings(cls) -> list:
        """Get the safety settings for the model"""
        return [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    
    @classmethod
    def validate(cls) -> None:
        """Validate the configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Ensure upload folder exists
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        
        # Ensure log directory exists
        os.makedirs(cls.LOG_DIR, exist_ok=True)