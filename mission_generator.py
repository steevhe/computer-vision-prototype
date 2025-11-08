from typing import Optional, Dict
import google.generativeai as genai
from config import Config


class MissionStatementGenerator:
    """Converts user problem descriptions into formalized mission statements"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Config.TEXT_MODEL)
    
    def generate_mission_statement(self, problem_description: str, 
                                   context: Optional[str] = None) -> Dict:
        prompt = self._create_mission_prompt(problem_description, context)
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Parse the structured response
            parsed = self._parse_mission_response(result)
            
            return {
                'success': True,
                'original_description': problem_description,
                'mission_statement': parsed.get('mission_statement', result),
                'problem_definition': parsed.get('problem_definition', ''),
                'goal': parsed.get('goal', ''),
                'expected_impact': parsed.get('expected_impact', ''),
                'action_steps': parsed.get('action_steps', []),
                'full_response': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_description': problem_description
            }
    
    def _create_mission_prompt(self, problem_description: str, 
                              context: Optional[str] = None) -> str:
        base_prompt = f"""You are an expert at converting community problems into actionable, 
inspiring mission statements for learning projects. You create clear, motivating statements 
that define the problem, the goal, and the expected impact.

Convert the following community problem description into a formalized, project-oriented mission statement:

Problem Description: "{problem_description}"
"""
        
        if context:
            base_prompt += f"\nAdditional Context: {context}\n"
        
        base_prompt += """
Please provide:

1. MISSION STATEMENT: A clear, inspiring statement (2-3 sentences) that:
   - Defines the core problem
   - States the goal/objective
   - Highlights the expected community impact

2. PROBLEM DEFINITION: A precise definition of the issue (1-2 sentences)

3. GOAL: The specific, measurable outcome we're working toward

4. EXPECTED IMPACT: How this will benefit the community

5. ACTION STEPS: 3-5 key steps to address this problem

Format your response clearly with these headers."""
        
        return base_prompt
    
    def _parse_mission_response(self, response: str) -> Dict:
        parsed = {}
        
        sections = {
            'mission_statement': ['MISSION STATEMENT:', 'Mission Statement:'],
            'problem_definition': ['PROBLEM DEFINITION:', 'Problem Definition:'],
            'goal': ['GOAL:', 'Goal:'],
            'expected_impact': ['EXPECTED IMPACT:', 'Expected Impact:'],
            'action_steps': ['ACTION STEPS:', 'Action Steps:']
        }
        
        for key, headers in sections.items():
            for header in headers:
                if header in response:
                    # Extract text after this header and before the next section
                    start_idx = response.find(header) + len(header)
                    remaining = response[start_idx:]
                    
                    # Find the next header
                    next_header_idx = len(remaining)
                    for other_key, other_headers in sections.items():
                        if other_key != key:
                            for other_header in other_headers:
                                idx = remaining.find(other_header)
                                if idx != -1 and idx < next_header_idx:
                                    next_header_idx = idx
                    
                    content = remaining[:next_header_idx].strip()
                    
                    # Special handling for action steps (convert to list)
                    if key == 'action_steps':
                        steps = [line.strip() for line in content.split('\n') 
                                if line.strip() and (line.strip()[0].isdigit() or 
                                line.strip().startswith('-') or line.strip().startswith('•'))]
                        parsed[key] = steps
                    else:
                        parsed[key] = content
                    break
        
        return parsed
    
    def generate_batch_missions(self, problem_descriptions: list) -> list:
        results = []
        for description in problem_descriptions:
            result = self.generate_mission_statement(description)
            results.append(result)
        return results


# Convenience function
def create_mission_statement(problem_description: str, 
                            context: Optional[str] = None) -> Dict:
    generator = MissionStatementGenerator()
    return generator.generate_mission_statement(problem_description, context)
