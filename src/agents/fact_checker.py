from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import numpy as np
from .base_agent import BaseAgent, AgentState, AgentEmotion, Memory, Belief, Goal

class FactCheckerAgent(BaseAgent):
    """Specialized agent for fact checking"""
    def __init__(self, llm):
        super().__init__(name="FactChecker", role="fact_checker", llm=llm)
        self.verified_facts: Dict[str, Dict] = {}
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # Initialize fact-checker specific goals
        self.goals.append(Goal(
            description="Verify factual accuracy",
            priority=0.95,
            progress=0.0
        ))
        self.goals.append(Goal(
            description="Identify misleading statements",
            priority=0.9,
            progress=0.0
        ))

    def _store_verification_result(self, claim: str, verification: Dict) -> None:
        """Store verification result in memory and verified_facts"""
        # Store in verified_facts dictionary
        self.verified_facts[claim] = verification
        
        # Create memory content with all relevant information
        memory_content = (
            f"Verified claim: {claim}\n"
            f"Status: {verification['status']}\n"
            f"Confidence: {verification['confidence']}\n"
            f"Reason: {verification.get('reason', 'No reason provided')}"
        )
        
        # Create context dictionary
        context = {
            'type': 'verification',
            'status': verification['status'],
            'confidence': verification['confidence'],
            'source': 'fact_checker'
        }
        
        # Create a memory entry
        memory = Memory(
            content=memory_content,
            importance=verification['confidence'],
            context=context,
            timestamp=time.time(),
            type='semantic'
        )
        
        # Add to agent's memory
        self.memories.append(memory)
        
        # Update relevant goals
        self._update_verification_goals(verification)
        
    def _update_verification_goals(self, verification: Dict) -> None:
        """Update goal progress based on verification result"""
        # Update "Verify factual accuracy" goal
        if verification['status'] == 'Verified':
            self.goals[0].progress = min(1.0, self.goals[0].progress + 0.1)
        
        # Update "Identify misleading statements" goal
        if verification['status'] == 'Misleading':
            self.goals[1].progress = min(1.0, self.goals[1].progress + 0.1)


    def _parse_verification_response(self, response: str) -> Dict:
        """Parse LLM verification response into structured format"""
        try:
            lines = response.strip().split('\n')
            result = {
                'status': 'Unverified',
                'confidence': 0.0,
                'reason': '',
                'corrections': []
            }
            
            for line in lines:
                line = line.strip()
                # Clean up the line and remove any numbering
                if line.startswith(('1.', '2.', '3.', '4.')):
                    line = line[2:].strip()
                    
                # Parse status
                if 'verified' in line.lower():
                    result['status'] = 'Verified'
                elif 'misleading' in line.lower():
                    result['status'] = 'Misleading'
                elif 'unverified' in line.lower():
                    result['status'] = 'Unverified'
                
                # Parse confidence - look for numbers
                if any(c.isdigit() for c in line):
                    try:
                        # Extract numbers from the line
                        numbers = ''.join([c for c in line if c.isdigit() or c == '.'])
                        confidence = float(numbers)
                        # Normalize to 0-1 range if necessary
                        if confidence > 1:
                            confidence = confidence / 100
                        result['confidence'] = min(1.0, max(0.0, confidence))
                    except ValueError:
                        continue
                
                # Parse reasoning
                if 'reason' in line.lower() or 'reasoning' in line.lower():
                    result['reason'] = line.split(':')[-1].strip()
                
                # Parse corrections
                if 'correct' in line.lower():
                    correction = line.split(':')[-1].strip()
                    if correction:
                        result['corrections'].append(correction)
            
            return result
        except Exception as e:
            return {
                'status': 'Error',
                'confidence': 0.0,
                'reason': f'Failed to parse verification response: {str(e)}'
            }

    def check_statement(self, statement: str) -> Dict:
        """Check factual accuracy of a statement"""
        # Extract claims
        claims = self._extract_claims(statement)
        
        # Verify each claim
        verification_results = []
        for claim in claims:
            # Check if we've verified this claim before
            if claim in self.verified_facts:
                result = self.verified_facts[claim]
            else:
                result = self._verify_claim(claim)
                self.verified_facts[claim] = result
            
            verification_results.append(result)
        
        # Aggregate results
        return self._aggregate_verification_results(verification_results)

    def _extract_claims(self, statement: str) -> List[str]:
        """Extract verifiable claims from statement"""
        prompt = """Extract specific, verifiable factual claims from this statement. Focus on:
        - Statistics and numbers
        - Historical events
        - Awards and achievements
        - Industry facts
        - Specific film references
        
        Format each claim as a separate numbered line.
        Ignore opinions and subjective statements.
        
        Statement: {statement}
        """
        
        try:
            response = self.llm(prompt.format(statement=statement))
            claims = []
            
            for line in response.split('\n'):
                line = line.strip()
                # Remove numbering if present
                if line and any(line.startswith(f"{i}.") for i in range(10)):
                    claim = line[2:].strip()
                else:
                    claim = line
                    
                # Only add non-empty, substantive claims
                if claim and len(claim) > 10 and not any(x in claim.lower() for x in ['example:', 'such as:', 'note:']):
                    claims.append(claim)
            
            return claims
        except Exception as e:
            print(f"Error extracting claims: {e}")  # Debug print
            return []
        
    def _verify_claim(self, claim: str) -> Dict:
        """Verify a single claim"""
        prompt = """Verify this claim based on general knowledge:
        Claim: {claim}
        
        Please provide:
        1. Status: Verified, Misleading, or Unverified
        2. Confidence: A number between 0 and 1
        3. Reason: Brief explanation for the verification status
        4. Sources: Any known references supporting the verification
        
        Response should be clear and specific."""
        
        try:
            response = self.llm(prompt.format(claim=claim))
            verification = self._parse_verification_response(response)
            verification['claim'] = claim
            
            # Store in memory
            self._store_verification_result(claim, verification)
            
            return verification
        except Exception as e:
            print(f"Error verifying claim: {e}")  # Debug print
            return {
                'status': 'Error',
                'confidence': 0.0,
                'reason': str(e),
                'claim': claim
            }


    def check_statement(self, statement: str) -> Dict:
        """Check factual accuracy of a statement"""
        try:
            # Extract claims
            claims = self._extract_claims(statement)
            if not claims:
                return {
                    'overall_accuracy': 'No verifiable claims found',
                    'confidence': 0.0,
                    'details': []
                }
            
            # Verify each claim
            verification_results = []
            for claim in claims:
                print(f"Verifying claim: {claim}")  # Debug print
                # Check if we've verified this claim before
                if claim in self.verified_facts:
                    result = self.verified_facts[claim]
                else:
                    result = self._verify_claim(claim)
                    result['claim'] = claim
                    self.verified_facts[claim] = result
                verification_results.append(result)
            
            return self._aggregate_verification_results(verification_results)
        except Exception as e:
            print(f"Error in check_statement: {e}")  # Debug print
            return {
                'overall_accuracy': 'Error checking statement',
                'confidence': 0.0,
                'details': []
            }
    
    def _aggregate_verification_results(self, results: List[Dict]) -> Dict:
        """Aggregate multiple verification results"""
        if not results:
            return {
                'overall_accuracy': 'No claims verified',
                'confidence': 0.0,
                'details': []
            }
        
        # Calculate overall accuracy
        accuracy_scores = []
        details = []
        
        for result in results:
            if result['status'] == 'Verified':
                accuracy_scores.append(result['confidence'])
            elif result['status'] == 'Misleading':
                accuracy_scores.append(result['confidence'] * 0.5)
            else:
                accuracy_scores.append(0.0)
            
            details.append({
                'claim': result.get('claim', 'Unknown claim'),
                'status': result['status'],
                'confidence': result['confidence'],
                'reason': result.get('reason', '')
            })
        
        overall_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        
        return {
            'overall_accuracy': self._get_accuracy_label(overall_accuracy),
            'confidence': overall_accuracy,
            'details': details
        }
    
    def _get_accuracy_label(self, accuracy_score: float) -> str:
        """Convert accuracy score to label"""
        if accuracy_score >= self.confidence_thresholds['high']:
            return 'Highly Accurate'
        elif accuracy_score >= self.confidence_thresholds['medium']:
            return 'Moderately Accurate'
        elif accuracy_score >= self.confidence_thresholds['low']:
            return 'Low Accuracy'
        else:
            return 'Unverified'
