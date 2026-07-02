"""
Bronze Agent - Data Ingestion & Validation Tier
Performs initial schema validation, data cleansing, and quality checks
"""

from typing import Any, Dict, List
from datetime import datetime
import logging
from agents.llm_agent import llm_agent

logger = logging.getLogger(__name__)


class BronzeAgent:
    """Handles raw claim ingestion and basic validation"""
    
    def __init__(self):
        self.name = "Bronze Agent"
        self.tier = "BRONZE"
        self.processed_count = 0
        self.failed_count = 0
    
    def process(self, raw_claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw claim through bronze tier validation
        
        Returns:
            Dict with validated data or error details
        """
        print(f"\n{'='*60}")
        print(f"[{self.name}] Processing Claim: {raw_claim.get('claim_id', 'UNKNOWN')}")
        print(f"{'='*60}")
        
        errors = []
        warnings = []
        cleaned_data = {}
        
        try:
            # 1. Validate required fields
            required_fields = [
                'claim_id', 'policy_id', 'policy_holder', 'claim_date',
                'service_date', 'provider', 'claim_amount', 'service_code'
            ]
            
            for field in required_fields:
                if field not in raw_claim or raw_claim[field] is None:
                    errors.append(f"Missing required field: {field}")
            
            if errors:
                raise ValueError("Validation failed: " + "; ".join(errors))
            
            # 2. Data type conversion and validation
            try:
                claim_amount = float(raw_claim['claim_amount'])
                if claim_amount <= 0:
                    errors.append("Claim amount must be positive")
            except (ValueError, TypeError):
                errors.append(f"Invalid claim amount: {raw_claim['claim_amount']}")
            
            # 3. Validate dates
            try:
                datetime.strptime(raw_claim['claim_date'], '%Y-%m-%d')
                datetime.strptime(raw_claim['service_date'], '%Y-%m-%d')
            except ValueError as e:
                errors.append(f"Invalid date format: {str(e)}")
            
            # 4. Validate age
            age = raw_claim.get('policy_holder', {}).get('age')
            if age and (age < 0 or age > 150):
                errors.append(f"Invalid age: {age}")
            
            # 5. Check for required nested fields
            if not raw_claim.get('policy_holder', {}).get('name'):
                errors.append("Policy holder name is required")
            
            if not raw_claim.get('provider', {}).get('name'):
                errors.append("Provider name is required")
            
            # 6. Clean diagnosis codes
            diag_codes = raw_claim.get('diagnosis_codes', [])
            if not diag_codes:
                warnings.append("No diagnosis codes provided")
            
            if errors:
                raise ValueError("Validation failed: " + "; ".join(errors))
            
            # 7. Create cleaned record
            cleaned_data = {
                'claim_id': raw_claim['claim_id'],
                'policy_id': raw_claim['policy_id'],
                'policy_holder_name': raw_claim['policy_holder']['name'],
                'policy_holder_age': raw_claim['policy_holder']['age'],
                'member_id': raw_claim['policy_holder']['member_id'],
                'claim_date': raw_claim['claim_date'],
                'service_date': raw_claim['service_date'],
                'provider_name': raw_claim['provider']['name'],
                'provider_id': raw_claim['provider']['id'],
                'claim_amount': claim_amount,
                'service_code': raw_claim['service_code'],
                'service_description': raw_claim['service_description'],
                'diagnosis_codes': diag_codes,
                'status': 'bronze_validated',
                'data_quality_score': self._calculate_quality_score(raw_claim),
                'validation_errors': errors,
                'processing_timestamp': datetime.now().isoformat()
            }

            # Attach OCR texts (if present) and generate an LLM-based incident summary
            ocr_texts = raw_claim.get('ocr_texts', {})
            cleaned_data['ocr_texts'] = ocr_texts
            try:
                incident_summary = llm_agent.summarize_incident(ocr_texts) if ocr_texts else ''
            except Exception:
                incident_summary = ''
            cleaned_data['incident_summary'] = incident_summary
            
            self.processed_count += 1
            
            print(f"[OK] Bronze validation PASSED")
            print(f"  - Quality Score: {cleaned_data['data_quality_score']:.2%}")
            if warnings:
                print(f"  - Warnings: {', '.join(warnings)}")
            
            return {
                'success': True,
                'tier': self.tier,
                'data': cleaned_data,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            self.failed_count += 1
            print(f"[FAIL] Bronze validation FAILED: {str(e)}")
            
            return {
                'success': False,
                'tier': self.tier,
                'claim_id': raw_claim.get('claim_id', 'UNKNOWN'),
                'error': str(e),
                'raw_data': raw_claim,
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def _calculate_quality_score(self, claim: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0-1)
        Based on presence of optional fields and data completeness
        """
        score = 0.8  # Start with 0.8 for passing validation
        
        # Add points for optional but helpful fields
        if claim.get('attachments'):
            score += 0.1
        if claim.get('diagnosis_codes'):
            score += 0.05
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent processing statistics"""
        return {
            'agent': self.name,
            'tier': self.tier,
            'processed': self.processed_count,
            'failed': self.failed_count,
            'success_rate': self.processed_count / max(1, self.processed_count + self.failed_count)
        }
