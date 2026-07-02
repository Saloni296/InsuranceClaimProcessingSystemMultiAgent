"""
Silver Agent - Data Enrichment & Quality Assurance Tier
Performs cross-reference checks, fraud detection, and business rule application
"""

from typing import Any, Dict, List
from datetime import datetime
import logging
from agent import llm_agent

logger = logging.getLogger(__name__)


class SilverAgent:
    """Handles data enrichment and quality assurance"""
    
    def __init__(self):
        self.name = "Silver Agent"
        self.tier = "SILVER"
        self.processed_count = 0
        self.failed_count = 0
        
        # Mock databases
        self.valid_policies = {
            'POL-12345', 'POL-54321', 'POL-99999', 'POL-55555', 'POL-001'
        }
        self.network_providers = {
            'PROV-789', 'PROV-102'  # In-network
        }
        self.valid_service_codes = {
            '99214', '71046', '27447', '99213', '99215'
        }
        # Mock policy texts for LLM policy checks
        self.policy_texts = {
            'POL-12345': 'Standard policy text: includes coverage for office visits and imaging.',
            'POL-001': 'Sample policy text: covers eligible medical services unless explicitly excluded.'
        }
    
    def process(self, bronze_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process bronze-validated data through silver tier enrichment
        
        Args:
            bronze_data: Output from Bronze Agent
            
        Returns:
            Enriched data with additional validations
        """
        print(f"\n{'='*60}")
        print(f"[{self.name}] Processing Claim: {bronze_data.get('data', {}).get('claim_id', 'UNKNOWN')}")
        print(f"{'='*60}")
        
        if not bronze_data.get('success'):
            print(f"✗ Skipping - Bronze validation failed")
            return {
                'success': False,
                'tier': self.tier,
                'claim_id': bronze_data.get('claim_id', 'UNKNOWN'),
                'error': 'Previous stage failed',
                'processing_timestamp': datetime.now().isoformat()
            }
        
        try:
            data = bronze_data['data']
            enriched_data = data.copy()
            enrichments = {}
            issues = []
            
            # 1. Policy verification
            policy_valid = self._verify_policy(data['policy_id'])
            enrichments['policy_verified'] = policy_valid
            if not policy_valid:
                issues.append(f"Policy {data['policy_id']} not found in system")
            
            # 2. Provider network check
            network_status = self._check_provider_network(data['provider_id'])
            enrichments['network_status'] = network_status
            enrichments['cost_sharing'] = self._get_cost_sharing(network_status)
            
            # 3. Service code validation
            service_valid = self._validate_service_code(data['service_code'])
            enrichments['service_code_valid'] = service_valid
            if not service_valid:
                issues.append(f"Service code {data['service_code']} not recognized")
            
            # 4. Age-based coverage check
            age_eligible = self._check_age_eligibility(data['policy_holder_age'])
            enrichments['age_eligible'] = age_eligible
            
            # 5. Fraud pattern detection
            fraud_score = self._detect_fraud_patterns(data)
            enrichments['fraud_risk_score'] = fraud_score
            if fraud_score > 0.7:
                issues.append(f"High fraud risk detected (score: {fraud_score:.2f})")
            
            # 6. Calculate eligible amount
            eligible_amount = self._calculate_eligible_amount(
                data['claim_amount'],
                network_status,
                data['policy_holder_age']
            )
            enrichments['eligible_amount'] = eligible_amount
            
            # 7. Apply business rules
            business_rule_result = self._apply_business_rules(data)
            enrichments['business_rules'] = business_rule_result
            
            self.processed_count += 1
            
            # Optionally run an LLM-based policy coverage check using the incident summary
            policy_text = self.policy_texts.get(data['policy_id'], '')
            try:
                policy_check = llm_agent.check_policy_coverage(data.get('incident_summary', ''), policy_text)
                enrichments['policy_check'] = policy_check
                if not policy_check.get('coverage_match', True):
                    issues.append('Policy coverage mismatch detected by LLM')
            except Exception:
                enrichments['policy_check'] = {'coverage_match': True, 'details': 'LLM check unavailable'}

            enriched_data.update({
                'status': 'silver_enriched',
                'enrichments': enrichments,
                'issues': issues,
                'processing_timestamp': datetime.now().isoformat()
            })
            
            print("[OK] Silver enrichment PASSED")
            print(f"  - Policy Verified: {policy_valid}")
            print(f"  - Network Status: {network_status}")
            print(f"  - Fraud Risk Score: {fraud_score:.2%}")
            print(f"  - Eligible Amount: ${eligible_amount:.2f}")
            if issues:
                print(f"  - Issues Found: {len(issues)}")
            
            return {
                'success': True,
                'tier': self.tier,
                'data': enriched_data,
                'issues': issues
            }
            
        except Exception as e:
            self.failed_count += 1
            print(f"[FAIL] Silver enrichment FAILED: {str(e)}")
            
            return {
                'success': False,
                'tier': self.tier,
                'claim_id': bronze_data.get('data', {}).get('claim_id', 'UNKNOWN'),
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def _verify_policy(self, policy_id: str) -> bool:
        """Verify policy exists in system"""
        return policy_id in self.valid_policies
    
    def _check_provider_network(self, provider_id: str) -> str:
        """Check if provider is in-network or out-of-network"""
        if provider_id in self.network_providers:
            return "IN-NETWORK"
        return "OUT-OF-NETWORK"
    
    def _get_cost_sharing(self, network_status: str) -> Dict[str, float]:
        """Get cost sharing percentages based on network"""
        if network_status == "IN-NETWORK":
            return {
                'coinsurance': 0.20,  # 20% patient pays
                'copay': 30.00,
                'deductible_applies': False
            }
        else:
            return {
                'coinsurance': 0.40,  # 40% patient pays
                'copay': 50.00,
                'deductible_applies': True
            }
    
    def _validate_service_code(self, service_code: str) -> bool:
        """Validate service code exists"""
        return service_code in self.valid_service_codes
    
    def _check_age_eligibility(self, age: int) -> bool:
        """Check age-based coverage eligibility"""
        return 0 < age < 130
    
    def _detect_fraud_patterns(self, data: Dict[str, Any]) -> float:
        """
        Detect potential fraud patterns
        Returns fraud risk score (0-1)
        """
        risk_score = 0.0
        
        # Pattern 1: Unusually high claim amount
        if data['claim_amount'] > 20000:
            risk_score += 0.2
        
        # Pattern 2: Multiple claims on same day
        if data['claim_date'] == data['service_date']:
            risk_score += 0.1
        
        # Pattern 3: Invalid diagnosis codes
        if not data['diagnosis_codes']:
            risk_score += 0.15
        
        # Pattern 4: Service date after claim date (anomaly)
        if data['service_date'] > data['claim_date']:
            risk_score += 0.25
        
        return min(risk_score, 1.0)
    
    def _calculate_eligible_amount(self, claim_amount: float, network_status: str, age: int) -> float:
        """Calculate eligible reimbursement amount"""
        eligible = claim_amount
        
        # Out-of-network gets reduced eligible amount
        if network_status == "OUT-OF-NETWORK":
            eligible *= 0.80  # 80% of submitted amount
        
        # Senior discounts (age 65+)
        if age >= 65:
            eligible *= 1.05  # 5% additional coverage
        
        return eligible
    
    def _apply_business_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules specific to claim type"""
        rules = {
            'applied': [],
            'skipped': []
        }
        
        # Rule 1: Surgery requires pre-auth
        if 'surgery' in data['service_description'].lower() or data['claim_amount'] > 5000:
            rules['applied'].append('Requires pre-authorization review')
        
        # Rule 2: Preventive services (low cost)
        if data['claim_amount'] < 500:
            rules['applied'].append('Preventive care eligible for 100% coverage')
        
        return rules
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent processing statistics"""
        return {
            'agent': self.name,
            'tier': self.tier,
            'processed': self.processed_count,
            'failed': self.failed_count,
            'success_rate': self.processed_count / max(1, self.processed_count + self.failed_count)
        }

