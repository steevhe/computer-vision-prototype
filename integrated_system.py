from typing import Dict, Optional, List
from vision_detector import CommunityIssueDetector
from mission_generator import MissionStatementGenerator
from problem_classifier import ProblemClassifier
from config import Config


class AILearningPlatform:
    
    def __init__(self, api_key: Optional[str] = None):
        Config.validate()
        
        self.vision_detector = CommunityIssueDetector(api_key)
        self.mission_generator = MissionStatementGenerator(api_key)
        self.problem_classifier = ProblemClassifier(api_key)
    
    def process_image(self, image_path: str, 
                     domains: Optional[List[str]] = None) -> Dict:
        print("Analyzing image for community issues...")
        
        # Step 1: Detect issues in the image
        vision_result = self.vision_detector.detect_issues(image_path, domains)
        
        if not vision_result['success']:
            return {
                'success': False,
                'error': vision_result.get('error', 'Vision detection failed'),
                'step': 'vision_detection'
            }
        
        print("Issues detected in image")
        print("\nClassifying the detected problems...")
        
        # Step 2: Classify the detected issues
        classification = self.problem_classifier.classify_with_vision_analysis(
            vision_result['analysis']
        )
        
        print(f"Classified as: {classification.get('category', 'Unknown')}")
        
        # Step 3: Extract key problem description for mission generation
        problem_desc = self._extract_problem_description(vision_result['analysis'])

        print("\nGenerating mission statement...")
        
        # Step 4: Generate mission statement
        mission = self.mission_generator.generate_mission_statement(
            problem_desc,
            context=f"Based on visual analysis. Category: {classification.get('category')}"
        )

        print("Mission statement generated")

        return {
            'success': True,
            'image_path': image_path,
            'vision_analysis': vision_result['analysis'],
            'classification': classification,
            'mission_statement': mission,
            'summary': self._create_summary(vision_result, classification, mission)
        }
    
    def process_text_description(self, problem_description: str) -> Dict:
        print("Processing problem description...")
        
        # Step 1: Classify the problem
        classification = self.problem_classifier.classify_problem(problem_description)
        
        if not classification['success']:
            return {
                'success': False,
                'error': classification.get('error', 'Classification failed'),
                'step': 'classification'
            }
        
        print(f"Classified as: {classification['category']}")
        print("\nGenerating mission statement...")
        
        # Step 2: Generate mission statement
        mission = self.mission_generator.generate_mission_statement(
            problem_description,
            context=f"Category: {classification['category']}"
        )
        
        if not mission['success']:
            return {
                'success': False,
                'error': mission.get('error', 'Mission generation failed'),
                'step': 'mission_generation',
                'classification': classification
            }
        
        print("Mission statement generated")
        
        return {
            'success': True,
            'original_description': problem_description,
            'classification': classification,
            'mission_statement': mission,
            'summary': self._create_text_summary(problem_description, classification, mission)
        }
    
    def process_multiple_images(self, image_paths: List[str]) -> List[Dict]:
        results = []
        for i, image_path in enumerate(image_paths, 1):
            print(f"\n{'='*60}")
            print(f"Processing Image {i}/{len(image_paths)}")
            print(f"{'='*60}")
            
            result = self.process_image(image_path)
            results.append(result)
        
        return results
    
    def _extract_problem_description(self, vision_analysis: str) -> str:
        # Look for detected issues section
        if "DETECTED ISSUES:" in vision_analysis:
            start = vision_analysis.find("DETECTED ISSUES:")
            end = vision_analysis.find("VISUAL EVIDENCE:", start)
            if end == -1:
                end = vision_analysis.find("RECOMMENDATIONS:", start)
            if end == -1:
                end = len(vision_analysis)
            
            issues_section = vision_analysis[start:end].strip()
            # Take first few lines as description
            lines = [line.strip() for line in issues_section.split('\n') 
                    if line.strip() and not line.strip().startswith('DETECTED')]
            return ' '.join(lines[:3]) if lines else vision_analysis[:200]
        
        # Fallback: use first 200 characters
        return vision_analysis[:200].strip()
    
    def _create_summary(self, vision_result: Dict, classification: Dict, 
                       mission: Dict) -> str:
        summary = f"""
{'='*70}
                    COMMUNITY ISSUE ANALYSIS SUMMARY
{'='*70}

VISION ANALYSIS:
{'-'*70}
{vision_result['analysis'][:500]}...

CLASSIFICATION:
{'-'*70}
Category: {classification.get('category', 'Unknown')}
Confidence: {classification.get('confidence', 'Unknown')}

MISSION STATEMENT:
{'-'*70}
{mission.get('mission_statement', 'N/A')}

PROBLEM DEFINITION:
{mission.get('problem_definition', 'N/A')}

EXPECTED IMPACT:
{mission.get('expected_impact', 'N/A')}

{'='*70}
"""
        return summary
    
    def _create_text_summary(self, description: str, classification: Dict, 
                           mission: Dict) -> str:
        summary = f"""
{'='*70}
                    PROBLEM ANALYSIS SUMMARY
{'='*70}

ORIGINAL DESCRIPTION:
{'-'*70}
{description}

CLASSIFICATION:
{'-'*70}
Category: {classification.get('category', 'Unknown')}
Confidence: {classification.get('confidence', 'Unknown')}
Reasoning: {classification.get('reasoning', 'N/A')[:200]}

MISSION STATEMENT:
{'-'*70}
{mission.get('mission_statement', 'N/A')}

EXPECTED IMPACT:
{mission.get('expected_impact', 'N/A')}

ACTION STEPS:
{'-'*70}
"""
        for i, step in enumerate(mission.get('action_steps', []), 1):
            summary += f"{i}. {step}\n"
        
        summary += f"\n{'='*70}\n"
        return summary


# Convenience function for quick testing
def analyze_community_issue(source: str, source_type: str = 'auto') -> Dict:
    platform = AILearningPlatform()
    
    # Auto-detect source type
    if source_type == 'auto':
        if (source.startswith('http://') or source.startswith('https://') or 
            source.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))):
            source_type = 'image'
        else:
            source_type = 'text'
    
    if source_type == 'image':
        return platform.process_image(source)
    else:
        return platform.process_text_description(source)
