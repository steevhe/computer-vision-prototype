from typing import Dict, Optional, List
import google.generativeai as genai
from config import Config


class AIMentor:
    """AI Mentor providing guidance through critical thinking and solution templates"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(Config.TEXT_MODEL)
        self.conversation_history = []
    
    def critical_thinking_mode(self, problem_description: str, 
                              context: Optional[str] = None) -> Dict:
        prompt = self._create_critical_thinking_prompt(problem_description, context)
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Parse the response
            parsed = self._parse_socratic_response(result)
            
            return {
                'success': True,
                'mode': 'Critical Thinking',
                'problem': problem_description,
                'guiding_questions': parsed.get('questions', []),
                'reflection_prompts': parsed.get('reflections', []),
                'challenge_points': parsed.get('challenges', []),
                'next_steps': parsed.get('next_steps', []),
                'full_response': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mode': 'Critical Thinking'
            }
    
    def solution_mode(self, problem_description: str, 
                     template_type: str = 'auto',
                     category: Optional[str] = None) -> Dict:

        # Determine best template if auto
        if template_type == 'auto':
            template_type = self._determine_template_type(problem_description, category)
        
        prompt = self._create_solution_template_prompt(
            problem_description, 
            template_type,
            category
        )
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Parse template response
            parsed = self._parse_template_response(result, template_type)
            
            return {
                'success': True,
                'mode': 'Solution',
                'template_type': template_type,
                'problem': problem_description,
                'template': parsed.get('template', {}),
                'implementation_guide': parsed.get('guide', ''),
                'tips': parsed.get('tips', []),
                'full_response': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mode': 'Solution'
            }
    
    def interactive_mentoring(self, user_message: str, 
                            mode: str = 'critical_thinking') -> Dict:

        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Create context-aware prompt
        prompt = self._create_interactive_prompt(user_message, mode)
        
        try:
            response = self.model.generate_content(prompt)
            mentor_response = response.text
            
            # Add mentor response to history
            self.conversation_history.append({
                'role': 'mentor',
                'content': mentor_response
            })
            
            return {
                'success': True,
                'mode': mode,
                'user_message': user_message,
                'mentor_response': mentor_response,
                'conversation_length': len(self.conversation_history)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'mode': mode
            }
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def _create_critical_thinking_prompt(self, problem_description: str, 
                                        context: Optional[str] = None) -> str:
        """Create prompt for critical thinking mode"""
        prompt = f"""You are a Socratic mentor who guides learners through critical thinking and reflection.
Your role is to ask thought-provoking questions rather than give direct answers.

Problem/Topic: {problem_description}
"""
        
        if context:
            prompt += f"\nContext: {context}\n"
        
        prompt += """
Generate Socratic guidance in this format:

GUIDING QUESTIONS:
[3-5 open-ended questions that help the learner explore the problem deeply]

REFLECTION PROMPTS:
[2-3 prompts that encourage self-reflection and analysis]

CHALLENGE POINTS:
[2-3 challenging perspectives or assumptions to examine]

NEXT STEPS:
[Suggested thinking exercises or exploration activities]

Remember: Ask questions, don't provide solutions. Guide discovery through inquiry.
"""
        
        return prompt
    
    def _create_solution_template_prompt(self, problem_description: str, 
                                        template_type: str,
                                        category: Optional[str] = None) -> str:
        """Create prompt for solution template generation"""
        
        template_instructions = {
            'swot': """
Generate a SWOT Analysis template:

STRENGTHS:
[Internal positive factors]

WEAKNESSES:
[Internal limitations]

OPPORTUNITIES:
[External favorable conditions]

THREATS:
[External challenges]

STRATEGIC INSIGHTS:
[Key takeaways and recommendations]
""",
            'budget': """
Generate a Budget Outline template:

REVENUE/FUNDING SOURCES:
[Expected income or funding]

EXPENSES:
- Personnel
- Materials
- Operations
- Contingency

BUDGET TIMELINE:
[Phased allocation]

COST-SAVING OPPORTUNITIES:
[Ideas for efficiency]
""",
            'action_plan': """
Generate an Action Plan template:

OBJECTIVES:
[Clear, measurable goals]

ACTION ITEMS:
[Step-by-step tasks with timeline]

RESPONSIBLE PARTIES:
[Who does what]

RESOURCES NEEDED:
[What's required]

SUCCESS METRICS:
[How to measure progress]

RISK MITIGATION:
[Potential challenges and solutions]
""",
            'stakeholder': """
Generate a Stakeholder Analysis template:

KEY STAKEHOLDERS:
[List of involved parties]

STAKEHOLDER INTERESTS:
[What each stakeholder cares about]

INFLUENCE LEVEL:
[High/Medium/Low for each]

ENGAGEMENT STRATEGY:
[How to involve each stakeholder]

COMMUNICATION PLAN:
[How and when to communicate]
""",
            'timeline': """
Generate a Project Timeline template:

PHASES:
[Major project phases]

MILESTONES:
[Key achievement points with dates]

DEPENDENCIES:
[What depends on what]

CRITICAL PATH:
[Most time-sensitive activities]

BUFFER TIME:
[Contingency periods]
"""
        }
        
        instruction = template_instructions.get(template_type, template_instructions['action_plan'])
        
        prompt = f"""You are a solution-oriented mentor helping create practical frameworks.

Problem: {problem_description}
"""
        
        if category:
            prompt += f"Category: {category}\n"
        
        prompt += f"""
Template Type: {template_type.upper().replace('_', ' ')}

{instruction}

IMPLEMENTATION GUIDE:
[Step-by-step guide to use this template]

PRACTICAL TIPS:
[3-5 actionable tips for success]

Tailor all sections specifically to the problem described above.
"""
        
        return prompt
    
    def _create_interactive_prompt(self, user_message: str, mode: str) -> str:
        """Create prompt for interactive conversation"""
        
        history_context = ""
        if self.conversation_history:
            history_context = "\nConversation history:\n"
            for entry in self.conversation_history[-4:]:  # Last 4 messages
                role = entry['role'].title()
                history_context += f"{role}: {entry['content']}\n"
        
        if mode == 'critical_thinking':
            system_role = """You are a Socratic mentor. Continue guiding through questions.
Ask probing questions, encourage reflection, challenge assumptions."""
        else:
            system_role = """You are a solution-focused mentor. Provide practical frameworks,
actionable advice, and concrete next steps."""
        
        prompt = f"""{system_role}
{history_context}

User: {user_message}

Mentor response:"""
        
        return prompt
    
    def _determine_template_type(self, problem_description: str, 
                                 category: Optional[str] = None) -> str:
        """Automatically determine best template type"""
        desc_lower = problem_description.lower()
        
        # Keywords for different templates
        if any(word in desc_lower for word in ['budget', 'cost', 'funding', 'money', 'finance']):
            return 'budget'
        elif any(word in desc_lower for word in ['stakeholder', 'community', 'people', 'involve']):
            return 'stakeholder'
        elif any(word in desc_lower for word in ['timeline', 'schedule', 'when', 'deadline']):
            return 'timeline'
        elif any(word in desc_lower for word in ['strength', 'weakness', 'opportunity', 'threat', 'analyze']):
            return 'swot'
        else:
            return 'action_plan'  # Default
    
    def _parse_socratic_response(self, response: str) -> Dict:
        """Parse Socratic questioning response"""
        parsed = {}
        
        sections = {
            'questions': ['GUIDING QUESTIONS:', 'Guiding Questions:'],
            'reflections': ['REFLECTION PROMPTS:', 'Reflection Prompts:'],
            'challenges': ['CHALLENGE POINTS:', 'Challenge Points:'],
            'next_steps': ['NEXT STEPS:', 'Next Steps:']
        }
        
        for key, headers in sections.items():
            for header in headers:
                if header in response:
                    content = self._extract_section_content(response, header, sections)
                    parsed[key] = self._parse_list_items(content)
                    break
        
        return parsed
    
    def _parse_template_response(self, response: str, template_type: str) -> Dict:
        """Parse template response"""
        parsed = {}
        
        # Extract template structure (everything before IMPLEMENTATION GUIDE)
        if 'IMPLEMENTATION GUIDE:' in response:
            template_text = response.split('IMPLEMENTATION GUIDE:')[0]
            guide_and_rest = response.split('IMPLEMENTATION GUIDE:')[1]
            
            parsed['template'] = self._parse_template_structure(template_text, template_type)
            
            if 'PRACTICAL TIPS:' in guide_and_rest:
                guide = guide_and_rest.split('PRACTICAL TIPS:')[0].strip()
                tips = guide_and_rest.split('PRACTICAL TIPS:')[1].strip()
                parsed['guide'] = guide
                parsed['tips'] = self._parse_list_items(tips)
            else:
                parsed['guide'] = guide_and_rest.strip()
                parsed['tips'] = []
        else:
            parsed['template'] = {'raw': response}
            parsed['guide'] = ''
            parsed['tips'] = []
        
        return parsed
    
    def _parse_template_structure(self, template_text: str, template_type: str) -> Dict:
        """Parse template into structured format"""
        lines = template_text.split('\n')
        structure = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a header (all caps with colon)
            if line.isupper() and ':' in line:
                current_section = line.replace(':', '').strip()
                structure[current_section] = []
            elif current_section:
                structure[current_section].append(line)
        
        return structure
    
    def _extract_section_content(self, response: str, header: str, 
                                 all_sections: Dict) -> str:
        """Extract content between section headers"""
        start_idx = response.find(header) + len(header)
        
        # Find next section header
        end_idx = len(response)
        for section_headers in all_sections.values():
            for other_header in section_headers:
                if other_header != header and other_header in response[start_idx:]:
                    idx = response.find(other_header, start_idx)
                    if idx < end_idx:
                        end_idx = idx
        
        return response[start_idx:end_idx].strip()
    
    def _parse_list_items(self, text: str) -> List[str]:
        """Parse text into list items"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Remove bullet points, numbers, dashes
            line = line.lstrip('•-–—*►▪▫').strip()
            if line and line[0].isdigit() and '.' in line[:3]:
                line = line.split('.', 1)[1].strip()
            if line:
                items.append(line)
        return items


# Convenience functions
def get_critical_thinking_guidance(problem: str, context: Optional[str] = None) -> Dict:
    """Get Socratic guidance for critical thinking"""
    mentor = AIMentor()
    return mentor.critical_thinking_mode(problem, context)


def get_solution_template(problem: str, template_type: str = 'auto', 
                          category: Optional[str] = None) -> Dict:
    """Get solution template and framework"""
    mentor = AIMentor()
    return mentor.solution_mode(problem, template_type, category)
