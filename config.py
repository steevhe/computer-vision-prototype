import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Google Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Model configurations
    VISION_MODEL = "gemini-2.5-flash"  # Gemini Vision model
    TEXT_MODEL = "gemini-2.5-flash"  # For NLP tasks
    
    # Problem categories
    CATEGORIES = ['Environment', 'Health', 'Education']
    
    # Domain-specific issues
    DOMAIN_ISSUES = {
        'Environment': [
            'littered streets',
            'blocked drainage',
            'deforestation',
            'poor waste disposal',
            'pollution',
            'illegal dumping'
        ],
        'Health': [
            'overcrowded clinics',
            'absence of safety gear',
            'unsanitary public spaces',
            'poor hygiene',
            'medical waste disposal',
            'lack of healthcare facilities'
        ],
        'Education': [
            'overcrowded classrooms',
            'damaged school infrastructure',
            'lack of learning materials',
            'poor facilities',
            'inadequate resources',
            'unsafe school environment'
        ]
    }
    
    # Image upload settings
    MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    @staticmethod
    def validate():
        """Validate that required configuration is present"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
