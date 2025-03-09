"""
Model configuration for AI-based log analysis
"""
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(override=True)

# Configure logging
logger = logging.getLogger(__name__)

# Define available models
GEMINI_MODELS = [
    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "description": "Fast, efficient model for quick analysis"},
    {"id": "gemini-2.0-flash-lite", "name": "Gemini 2.0 Flash Lite", "description": "Lightweight version for basic analysis"},
    {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "Balanced performance model"},
    {"id": "gemini-1.5-flash-8b", "name": "Gemini 1.5 Flash 8B", "description": "Compact model for simple analysis"}
]

# Default model
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash-lite"

def get_gemini_model(model_id=None):
    """Try to get a specific Gemini model or fall back to alternatives"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error("Google API key not found")
        raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
        
    genai.configure(api_key=api_key)
    
    # Use specified model ID or default
    model_id_to_use = model_id or DEFAULT_GEMINI_MODEL
    
    try:
        logger.info(f"Attempting to use Gemini model: {model_id_to_use}")
        model = genai.GenerativeModel(model_name=model_id_to_use)
        # Test the model with a simple prompt
        test_response = model.generate_content("Test")
        logger.info(f"Successfully connected to model: {model_id_to_use}")
        return model
    except Exception as e:
        logger.warning(f"Failed to use specified model {model_id_to_use}: {str(e)}")
        
        # Try to fall back to other models if the specified one fails
        fallback_models = [m["id"] for m in GEMINI_MODELS if m["id"] != model_id_to_use]
        
        for fallback_id in fallback_models:
            try:
                logger.info(f"Trying fallback model: {fallback_id}")
                model = genai.GenerativeModel(model_name=fallback_id)
                test_response = model.generate_content("Test")
                logger.info(f"Successfully connected to fallback model: {fallback_id}")
                return model
            except Exception as fallback_error:
                logger.warning(f"Failed to use fallback model {fallback_id}: {str(fallback_error)}")
                continue
        
        # If we get here, we couldn't find any working model
        raise Exception("Could not find any working Gemini model")

def analyze_with_gemini(log_data, model_id=None):
    """Analyze log data using Google Gemini"""
    try:
        # Get the model
        model = get_gemini_model(model_id)
        
        # Create the prompt
        prompt = f"""
        You are a network security expert analyzing log data. Please provide a detailed explanation of the following network log:
        
        {log_data}
        
        In your analysis, include:
        1. What type of attack or anomaly is shown in the log
        2. Explanation of each field in the log
        3. The severity and potential impact of this activity
        4. Recommended actions to mitigate this type of attack
        5. Any additional context that would help understand this security event
        """
        
        # Generate the response
        response = model.generate_content(prompt)
        
        return {
            "analysis": response.text,
            "model_used": model_id or DEFAULT_GEMINI_MODEL,
            "provider": "gemini"
        }
    except Exception as e:
        logger.error(f"Error in Gemini analysis: {str(e)}")
        return {
            "analysis": f"Error analyzing log with Gemini: {str(e)}",
            "model_used": "error",
            "provider": "gemini"
        }
