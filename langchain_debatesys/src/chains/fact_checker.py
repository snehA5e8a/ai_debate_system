from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, List
import time

class ClaimExtractor(LLMChain):
    """Chain for extracting verifiable claims"""
    
    def __init__(self, llm):
        prompt = PromptTemplate(
            input_variables=["statement"],
            template="""Extract specific, verifiable factual claims from this statement:
            
            Statement: {statement}
            
            Only include claims that:
            1. Contain specific facts, numbers, or statistics
            2. Make definitive statements about reality
            3. Can be verified through research
            
            Exclude opinions and subjective statements.
            Format each claim on a new line."""
        )
        super().__init__(llm=llm, prompt=prompt)
    
    def extract_claims(self, statement: str) -> List[str]:
        """Extract verifiable claims from a statement"""
        try:
            result = self({"statement": statement})
            claims = [
                claim.strip() for claim in result["text"].split('\n')
                if claim.strip()
            ]
            return claims
        except Exception:
            return []

class ClaimVerifier(LLMChain):
    """Chain for verifying individual claims"""
    
    def __init__(self, llm):
        prompt = PromptTemplate(
            input_variables=["claim"],
            template="""Verify this claim based on general knowledge:
            
            Claim: {claim}
            
            Provide:
            1. Status (Verified/Unverified/Misleading)
            2. Confidence (0-1)
            3. Reasoning
            4. Any necessary corrections
            
            Format as:
            Status: [status]
            Confidence: [score]
            Reasoning: [explanation]
            Corrections: [if any]"""
        )
        super().__init__(llm=llm, prompt=prompt)
        
        self.verified_claims = {}
    
    def verify_claim(self, claim: str) -> Dict:
        """Verify a single claim"""
        # Check if claim was previously verified
        if claim in self.verified_claims:
            return self.verified_claims[claim]
        
        try:
            result = self({"claim": claim})
            verification = self._parse_verification(result["text"])
            self.verified_claims[claim] = verification
            return verification
        except Exception:
            return {
                "status": "Error",
                "confidence": 0.0,
                "reasoning": "Verification failed",
                "corrections": []
            }
    
    def _parse_verification(self, text: str) -> Dict:
        """Parse verification response"""
        lines = text.split('\n')
        result = {
            "status": "Unverified",
            "confidence": 0.0,
            "reasoning": "",
            "corrections": []
        }
        
        for line in lines:
            if line.startswith('Status:'):
                result["status"] = line.split(':', 1)[1].strip()
            elif line.startswith('Confidence:'):
                try:
                    result["confidence"] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('Reasoning:'):
                result["reasoning"] = line.split(':', 1)[1].strip()
            elif line.startswith('Corrections:'):
                corrections = line.split(':', 1)[1].strip()
                if corrections:
                    result["corrections"] = [c.strip() for c in corrections.split(';')]
        
        return result

class FactCheckerChain(LLMChain):
    """Main chain for fact checking"""
    
    def __init__(self, llm, memory=None):
        super().__init__(llm=llm, prompt=None, memory=memory)
        self.extractor = ClaimExtractor(llm)
        self.verifier = ClaimVerifier(llm)
        
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
    
    def check_statement(self, statement: str) -> Dict:
        """Check factual accuracy of a statement"""
        try:
            # Extract claims
            claims = self.extractor.extract_claims(statement)
            
            # Verify each claim
            verification_results = []
            for claim in claims:
                result = self.verifier.verify_claim(claim)
                verification_results.append({
                    "claim": claim,
                    **result
                })
            
            # Aggregate results
            return self._aggregate_results(verification_results)
        except Exception as e:
            return {
                "overall_accuracy": "Error",
                "confidence": 0.0,
                "details": [{"error": str(e)}]
            }
    
    def _aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate verification results"""
        if not results:
            return {
                "overall_accuracy": "Unknown",
                "confidence": 0.0,
                "details": []
            }
        
        # Calculate overall accuracy
        accuracy_scores = []
        for result in results:
            if result["status"] == "Verified":
                accuracy_scores.append(result["confidence"])
            elif result["status"] == "Misleading":
                accuracy_scores.append(result["confidence"] * 0.5)
            else:
                accuracy_scores.append(0.0)
        
        overall_accuracy = sum(accuracy_scores) / len(accuracy_scores)
        
        return {
            "overall_accuracy": self._get_accuracy_label(overall_accuracy),
            "confidence": overall_accuracy,
            "details": results
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