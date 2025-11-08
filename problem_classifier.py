from typing import Dict, Optional, List
import google.generativeai as genai
from config import Config


class ProblemClassifier:
    """Classifies community problems into predefined categories"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Config.TEXT_MODEL)
        self.categories = Config.CATEGORIES
    
    def classify_problem(self, problem_description: str, 
                        use_reasoning: bool = True) -> Dict:
        prompt = self._create_classification_prompt(problem_description, use_reasoning)
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Parse the classification
            category, confidence, reasoning = self._parse_classification(result)
            
            return {
                'success': True,
                'problem_description': problem_description,
                'category': category,
                'confidence': confidence,
                'reasoning': reasoning,
                'all_categories': self.categories,
                'full_response': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'problem_description': problem_description
            }
    
    def classify_with_vision_analysis(self, vision_analysis: str) -> Dict:
        prompt = f"""You are an expert classifier that categorizes community problems into 
three domains: Environment, Health, and Education. You provide accurate classifications with clear reasoning.

Based on the following vision analysis of a community problem image, classify the primary problem category:

Vision Analysis:
{vision_analysis}

Classify the primary issue into one of these categories:
- Environment
- Health
- Education

Provide:
1. PRIMARY CATEGORY: [Your classification]
2. CONFIDENCE: [High/Medium/Low]
3. REASONING: [Why this category fits best]

If multiple categories apply, choose the most dominant one."""
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            category, confidence, reasoning = self._parse_classification(result)
            
            return {
                'success': True,
                'category': category,
                'confidence': confidence,
                'reasoning': reasoning,
                'source': 'vision_analysis'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_classification_prompt(self, problem_description: str, 
                                     use_reasoning: bool) -> str:
        categories_desc = self._get_category_descriptions()
        
        prompt = f"""You are an expert classifier that categorizes community problems into three domains: 
Environment, Health, and Education. You provide accurate classifications with clear reasoning.

Classify the following community problem into ONE of these categories:

Categories and their scope:
{categories_desc}

Problem to classify:
"{problem_description}"

Provide your response in this format:

PRIMARY CATEGORY: [Choose: Environment, Health, or Education]
CONFIDENCE: [High, Medium, or Low]
"""
        
        if use_reasoning:
            prompt += "REASONING: [Explain why this category is most appropriate]\n"
        
        prompt += "\nChoose only ONE primary category, even if the problem touches multiple areas."
        
        return prompt
    
    def _get_category_descriptions(self) -> str:
        descriptions = []
        
        for category in self.categories:
            issues = Config.DOMAIN_ISSUES.get(category, [])
            examples = ', '.join(issues[:3])
            descriptions.append(
                f"- {category}: Issues related to {examples}, and similar concerns"
            )
        
        return '\n'.join(descriptions)
    
    def _parse_classification(self, response: str) -> tuple:
        category = None
        confidence = "Unknown"
        reasoning = ""
        
        # Extract category
        for cat in self.categories:
            if cat.lower() in response.lower():
                category = cat
                break
        
        # If no exact match, try to extract from structured response
        if not category:
            if "PRIMARY CATEGORY:" in response or "Category:" in response:
                lines = response.split('\n')
                for line in lines:
                    if "CATEGORY:" in line.upper():
                        for cat in self.categories:
                            if cat.lower() in line.lower():
                                category = cat
                                break
        
        # Default to first match in text if still not found
        if not category:
            category = self.categories[0]  # Default fallback
        
        # Extract confidence
        confidence_keywords = {
            'high': ['high', 'very confident', 'definitely', 'clearly'],
            'medium': ['medium', 'moderate', 'fairly', 'somewhat'],
            'low': ['low', 'uncertain', 'possibly', 'might']
        }
        
        response_lower = response.lower()
        for level, keywords in confidence_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                confidence = level.capitalize()
                break
        
        # Extract reasoning
        reasoning_markers = ['REASONING:', 'Reasoning:', 'because', 'Because']
        for marker in reasoning_markers:
            if marker in response:
                start_idx = response.find(marker)
                reasoning = response[start_idx:].strip()
                break
        
        if not reasoning:
            reasoning = response
        
        return category, confidence, reasoning
    
    def classify_batch(self, problem_descriptions: List[str]) -> List[Dict]:
        results = []
        for description in problem_descriptions:
            result = self.classify_problem(description)
            results.append(result)
        return results


# Convenience function
def classify_community_problem(problem_description: str) -> Dict:
    classifier = ProblemClassifier()
    return classifier.classify_problem(problem_description)
