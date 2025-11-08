import base64
import os
from typing import Dict, List, Optional
import google.generativeai as genai
from config import Config


class CommunityIssueDetector:
    """Detects community issues in images using Gemini Vision"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Config.VISION_MODEL)
        
    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def detect_issues(self, image_path: str, domains: Optional[List[str]] = None) -> Dict:
        domains = domains or Config.CATEGORIES
        
        # Create the prompt
        prompt = self._create_detection_prompt(domains)
        
        try:
            # Read and prepare the image
            from PIL import Image
            img = Image.open(image_path)
            
            # Call Gemini Vision API
            response = self.model.generate_content([prompt, img])
            
            # Parse the response
            analysis = response.text
            
            return {
                'success': True,
                'analysis': analysis,
                'raw_response': response,
                'domains_analyzed': domains
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'domains_analyzed': domains
            }
    
    def _create_detection_prompt(self, domains: List[str]) -> str:
        domain_examples = []
        for domain in domains:
            if domain in Config.DOMAIN_ISSUES:
                issues = ', '.join(Config.DOMAIN_ISSUES[domain][:3])
                domain_examples.append(f"- {domain}: {issues}, etc.")
        
        examples_text = '\n'.join(domain_examples)
        
        prompt = f"""You are an AI assistant specialized in identifying community issues in images.

Analyze this image and identify any visible community problems in the following domains:
{', '.join(domains)}

For each domain, look for issues such as:
{examples_text}

Please provide:
1. A list of all visible issues identified in the image
2. The domain category for each issue (Environment, Health, or Education)
3. A brief description of each problem
4. The severity level (Low, Medium, High)
5. Specific visual evidence you observed

Format your response as:

DETECTED ISSUES:
[List each issue with its domain, description, and severity]

VISUAL EVIDENCE:
[Describe what you see that indicates these problems]

RECOMMENDATIONS:
[Brief suggestions for addressing the issues]

Be specific and objective in your analysis."""
        
        return prompt
    
    def detect_multiple_images(self, image_paths: List[str], 
                              domains: Optional[List[str]] = None) -> List[Dict]:
        results = []
        for image_path in image_paths:
            result = self.detect_issues(image_path, domains)
            result['image_path'] = image_path
            results.append(result)
        return results


# Convenience function
def detect_community_issue(image_path: str, 
                          domains: Optional[List[str]] = None) -> Dict:
    detector = CommunityIssueDetector()
    return detector.detect_issues(image_path, domains)
