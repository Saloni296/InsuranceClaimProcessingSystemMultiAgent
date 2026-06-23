"""
Gold Agent - Final Processing & Business Logic Tier
Generates approval/denial recommendations, applies coverage limits, and formats output
"""

from typing import Any, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GoldAgent:
    """Handles final processing and business logic application"""
    
    def __init__(self):
        self.name = "Gold Agent"
        self.tier = "GOLD"
        self.processed_count = 0
        self.failed_count = 0
        
        # Coverage limits by service category
        self.coverage_limits = {
            'office_visit': 500.0,
            'emergency': 5000.0,
            'surgery': 50000.0,
            'imaging': 2000.0,
            'lab': 300.0,
            'default': 1000.0
        }
        
        # Annual limits per member
        self.annual_limits = {
            'out_of_pocket_max': 5000.0,
            'deductible': 1000.0
        }
    
    def process(self, silver_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process silver-enriched data through gold tier final processing
        
        Args:
            silver_data: Output from Silver Agent
            
        Returns:
            Final claim decision with approval/denial and payment details
        """
        print(f"\n{'='*60}")
        print(f"[{self.name}] Processing Claim: {silver_data.get('data', {}).get('claim_id', 'UNKNOWN')}")
        print(f"{'='*60}")
        
        if not silver_data.get('success'):
            print(f"✗ Skipping - Silver enrichment failed")
            return {
                'success': False,
                'tier': self.tier,
                'claim_id': silver_data.get('claim_id', 'UNKNOWN'),
                'error': 'Previous stage failed',
                'processing_timestamp': datetime.now().isoformat()
            }
        
        try:
            data = silver_data['data']
            final_data = data.copy()
            
            # 1. Apply coverage limits
            coverage_result = self._apply_coverage_limits(data)
            
            # 2. Calculate patient responsibility
            patient_resp = self._calculate_patient_responsibility(data, coverage_result)
            
            # 3. Generate decision
            decision = self._generate_decision(data, silver_data.get('issues', []), coverage_result)
            
            # 4. Create payment details
            payment_details = self._create_payment_details(data, coverage_result, patient_resp, decision)
            
            # 5. Generate audit trail
            audit_trail = self._generate_audit_trail(data, coverage_result, decision)
            
            self.processed_count += 1
            
            final_data.update({
                'status': 'gold_processed',
                'decision': decision,
                'coverage_analysis': coverage_result,
                'patient_responsibility': patient_resp,
                'payment_details': payment_details,
                'audit_trail': audit_trail,
                'processing_timestamp': datetime.now().isoformat()
            })
            
            print(f"✓ Gold processing PASSED")
            print(f"  - Decision: {decision['recommendation']}")
            print(f"  - Approved Amount: ${payment_details['approved_amount']:.2f}")
            print(f"  - Patient Responsibility: ${patient_resp['total_patient_pay']:.2f}")
            print(f"  - Confidence Score: {decision['confidence_score']:.2%}")
            
            return {
                'success': True,
                'tier': self.tier,
                'data': final_data,
                'decision': decision
            }
            
        except Exception as e:
            self.failed_count += 1
            print(f"✗ Gold processing FAILED: {str(e)}")
            
            return {
                'success': False,
                'tier': self.tier,
                'claim_id': silver_data.get('data', {}).get('claim_id', 'UNKNOWN'),
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def _apply_coverage_limits(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply coverage limits based on service type"""
        service_desc = data['service_description'].lower()
        
        # Determine service category
        if 'surgery' in service_desc or 'replacement' in service_desc:
            category = 'surgery'
        elif 'imaging' in service_desc or 'x-ray' in service_desc:
            category = 'imaging'
        elif 'lab' in service_desc or 'test' in service_desc:
            category = 'lab'
        elif 'emergency' in service_desc:
            category = 'emergency'
        elif 'visit' in service_desc or 'office' in service_desc:
            category = 'office_visit'
        else:
            category = 'default'
        
        limit = self.coverage_limits.get(category, self.coverage_limits['default'])
        
        return {
            'service_category': category,
            'coverage_limit': limit,
            'claimed_amount': data['claim_amount'],
            'amount_within_limit': min(data['claim_amount'], limit),
            'excess_amount': max(0, data['claim_amount'] - limit)
        }
    
    def _calculate_patient_responsibility(self, data: Dict[str, Any], coverage: Dict[str, Any]) -> Dict[str, float]:
        """Calculate patient's financial responsibility"""
        cost_sharing = data['enrichments'].get('cost_sharing', {})
        allowed_amount = coverage['amount_within_limit']
        
        # Apply deductible (simplified - assume $1000 annual deductible)
        deductible_applied = cost_sharing.get('deductible_applies', False)
        deductible_amount = self.annual_limits['deductible'] if deductible_applied else 0
        
        # Apply coinsurance
        coinsurance_pct = cost_sharing.get('coinsurance', 0.20)
        coinsurance_amount = (allowed_amount - deductible_amount) * coinsurance_pct if allowed_amount > deductible_amount else 0
        
        # Cap at out-of-pocket maximum
        total_patient = min(deductible_amount + coinsurance_amount, self.annual_limits['out_of_pocket_max'])
        
        return {
            'deductible': deductible_amount,
            'coinsurance': coinsurance_amount,
            'copay': cost_sharing.get('copay', 0),
            'total_patient_pay': total_patient,
            'insurance_pays': allowed_amount - total_patient
        }
    
    def _generate_decision(self, data: Dict[str, Any], issues: List[str], coverage: Dict[str, Any]) -> Dict[str, Any]:
        """Generate approval or denial decision"""
        
        # Calculate decision factors
        has_critical_issues = len(issues) > 0
        fraud_risk = data['enrichments'].get('fraud_risk_score', 0) > 0.7
        policy_verified = data['enrichments'].get('policy_verified', False)
        service_valid = data['enrichments'].get('service_code_valid', False)
        
        # Decision logic
        if fraud_risk:
            recommendation = 'DENY'
            reason = 'High fraud risk detected'
            confidence = 0.95
        elif not policy_verified:
            recommendation = 'DENY'
            reason = 'Policy verification failed'
            confidence = 0.90
        elif not service_valid:
            recommendation = 'DENY'
            reason = 'Service code not recognized'
            confidence = 0.85
        elif coverage['excess_amount'] > 0:
            recommendation = 'APPROVE_PARTIAL'
            reason = f"Excess amount (${coverage['excess_amount']:.2f}) exceeds coverage limit"
            confidence = 0.80
        elif has_critical_issues:
            recommendation = 'APPROVE_WITH_REVIEW'
            reason = f'Approval with manual review recommended due to {len(issues)} issue(s)'
            confidence = 0.70
        else:
            recommendation = 'APPROVE'
            reason = 'All validations passed'
            confidence = 0.98
        
        return {
            'recommendation': recommendation,
            'reason': reason,
            'confidence_score': confidence,
            'decision_date': datetime.now().isoformat(),
            'requires_manual_review': recommendation in ['DENY', 'APPROVE_WITH_REVIEW', 'APPROVE_PARTIAL']
        }
    
    def _create_payment_details(self, data: Dict[str, Any], coverage: Dict[str, Any], 
                                patient_resp: Dict[str, float], decision: Dict[str, Any]) -> Dict[str, Any]:
        """Create payment instruction details"""
        
        approved_amount = coverage['amount_within_limit'] if decision['recommendation'] != 'DENY' else 0
        
        return {
            'approved_amount': approved_amount,
            'insurance_pays': patient_resp['insurance_pays'],
            'patient_pays': patient_resp['total_patient_pay'],
            'provider_payment': approved_amount - patient_resp['total_patient_pay'],
            'claim_reference': f"REF-{data['claim_id']}-{datetime.now().strftime('%Y%m%d')}",
            'payment_method': 'Electronic Transfer',
            'expected_payment_date': '2024-02-15'
        }
    
    def _generate_audit_trail(self, data: Dict[str, Any], coverage: Dict[str, Any], decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create comprehensive audit trail for compliance"""
        
        return [
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'CLAIM_RECEIVED',
                'actor': 'System',
                'details': f"Claim {data['claim_id']} received from {data['provider_name']}"
            },
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'VALIDATIONS_COMPLETED',
                'actor': 'BronzeAgent',
                'details': 'Data validation completed successfully'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'ENRICHMENT_COMPLETED',
                'actor': 'SilverAgent',
                'details': f"Fraud risk score: {data['enrichments'].get('fraud_risk_score', 0):.2%}"
            },
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'DECISION_MADE',
                'actor': 'GoldAgent',
                'details': f"Decision: {decision['recommendation']} - {decision['reason']}"
            },
            {
                'timestamp': datetime.now().isoformat(),
                'action': 'PAYMENT_APPROVED',
                'actor': 'PaymentProcessor',
                'details': 'Awaiting payment processing'
            }
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent processing statistics"""
        return {
            'agent': self.name,
            'tier': self.tier,
            'processed': self.processed_count,
            'failed': self.failed_count,
            'success_rate': self.processed_count / max(1, self.processed_count + self.failed_count)
        }

