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
        prompt = f"""Extract verifiable factual claims from this statement:
        Statement: {statement}
        
        Requirements:
        - Only extract claims that can be verified
        - Focus on numerical claims and specific facts
        - Ignore opinions and subjective statements
        """
        
        try:
            response = self.llm(prompt)
            # Process response to extract claims
            claims = [line.strip() for line in response.split('\n') if line.strip()]
            return claims
        except Exception:
            return []

    def _verify_claim(self, claim: str) -> Dict:
        """Verify a single claim"""
        prompt = f"""Verify this claim based on general knowledge:
        Claim: {claim}
        
        Provide:
        1. Verification status (Verified/Unverified/Misleading)
        2. Confidence level (0-1)
        3. Reasoning
        4. Any necessary corrections
        """
        
        try:
            response = self.llm(prompt)
            verification = self._parse_verification_response(response)
            
            # Store in memory
            self._store_verification_result(claim, verification)
            
            return verification
        except Exception as e:
            return {
                'status': 'Error',
                'confidence': 0.0,
                'reason': str(e)
            }

    def _aggregate_verification_results(self, results: List[Dict]) -> Dict:
        """Aggregate multiple verification results"""
        if not results:
            return {
                'overall_accuracy': 'Unknown',
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
                'claim': result.get('claim', ''),
                'status': result['status'],
                'confidence': result['confidence'],
                'reason': result.get('reason', '')
            })
        
        overall_accuracy = sum(accuracy_scores) / len(accuracy_scores)
        
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
