"""
Orchestrator Agent - Coordinates the multi-agent pipeline
Routes claims through Bronze → Silver → Gold tier processing
"""

from typing import Any, Dict, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Orchestrates the claim processing pipeline"""
    
    def __init__(self, bronze_agent, silver_agent, gold_agent):
        self.name = "Orchestrator Agent"
        self.bronze = bronze_agent
        self.silver = silver_agent
        self.gold = gold_agent
        
        self.pipeline_metrics = {
            'total_claims': 0,
            'successful_claims': 0,
            'failed_claims': 0,
            'stage_failures': {
                'bronze': 0,
                'silver': 0,
                'gold': 0
            }
        }
    
    def orchestrate_claim(self, raw_claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute complete claim processing pipeline
        
        Flow: Raw Claim → Bronze → Silver → Gold → Final Output
        
        Args:
            raw_claim: Raw claim data from source system
            
        Returns:
            Complete processing result with final decision
        """
        claim_id = raw_claim.get('claim_id', 'UNKNOWN')
        print(f"\n{'#'*60}")
        print(f"# ORCHESTRATOR: Starting pipeline for claim {claim_id}")
        print(f"{'#'*60}")
        
        self.pipeline_metrics['total_claims'] += 1
        
        # Stage 1: Bronze Agent
        print(f"\n[STAGE 1/3] Bronze Tier - Data Ingestion & Validation")
        bronze_result = self.bronze.process(raw_claim)
        
        if not bronze_result['success']:
            self.pipeline_metrics['failed_claims'] += 1
            self.pipeline_metrics['stage_failures']['bronze'] += 1
            
            return {
                'claim_id': claim_id,
                'pipeline_status': 'FAILED_AT_BRONZE',
                'final_decision': 'DENY',
                'reason': bronze_result['error'],
                'processing_stages': {
                    'bronze': bronze_result,
                    'silver': None,
                    'gold': None
                },
                'completion_timestamp': datetime.now().isoformat()
            }
        
        # Stage 2: Silver Agent
        print(f"\n[STAGE 2/3] Silver Tier - Enrichment & Quality Assurance")
        silver_result = self.silver.process(bronze_result)
        
        if not silver_result['success']:
            self.pipeline_metrics['failed_claims'] += 1
            self.pipeline_metrics['stage_failures']['silver'] += 1
            
            return {
                'claim_id': claim_id,
                'pipeline_status': 'FAILED_AT_SILVER',
                'final_decision': 'DENY',
                'reason': silver_result['error'],
                'processing_stages': {
                    'bronze': bronze_result,
                    'silver': silver_result,
                    'gold': None
                },
                'completion_timestamp': datetime.now().isoformat()
            }
        
        # Stage 3: Gold Agent
        print(f"\n[STAGE 3/3] Gold Tier - Final Processing & Business Logic")
        gold_result = self.gold.process(silver_result)
        
        if not gold_result['success']:
            self.pipeline_metrics['failed_claims'] += 1
            self.pipeline_metrics['stage_failures']['gold'] += 1
            
            return {
                'claim_id': claim_id,
                'pipeline_status': 'FAILED_AT_GOLD',
                'final_decision': 'DENY',
                'reason': gold_result['error'],
                'processing_stages': {
                    'bronze': bronze_result,
                    'silver': silver_result,
                    'gold': gold_result
                },
                'completion_timestamp': datetime.now().isoformat()
            }
        
        # All stages successful
        self.pipeline_metrics['successful_claims'] += 1
        
        final_data = gold_result['data']
        
        print(f"\n{'$'*60}")
        print(f"$ PIPELINE COMPLETE - Claim {claim_id}")
        print(f"$ Status: SUCCESS | Decision: {gold_result['decision']['recommendation']}")
        print(f"{'$'*60}")
        
        return {
            'claim_id': claim_id,
            'pipeline_status': 'SUCCESS',
            'final_decision': gold_result['decision']['recommendation'],
            'reason': gold_result['decision']['reason'],
            'confidence': gold_result['decision']['confidence_score'],
            'approved_amount': final_data['payment_details']['approved_amount'],
            'patient_responsibility': final_data['patient_responsibility']['total_patient_pay'],
            'provider': final_data['provider_name'],
            'processing_stages': {
                'bronze': {
                    'status': bronze_result['success'],
                    'quality_score': bronze_result['data']['data_quality_score']
                },
                'silver': {
                    'status': silver_result['success'],
                    'fraud_risk': silver_result['data']['enrichments']['fraud_risk_score'],
                    'issues': len(silver_result['issues'])
                },
                'gold': {
                    'status': gold_result['success'],
                    'decision': gold_result['decision']['recommendation']
                }
            },
            'audit_trail': final_data['audit_trail'],
            'completion_timestamp': datetime.now().isoformat()
        }
    
    def orchestrate_batch(self, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple claims through the pipeline
        
        Args:
            claims: List of raw claims
            
        Returns:
            Batch processing results
        """
        print(f"\n{'='*60}")
        print(f"ORCHESTRATOR: Batch Processing {len(claims)} claims")
        print(f"{'='*60}\n")
        
        results = {
            'batch_id': f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'total_claims': len(claims),
            'claim_results': [],
            'batch_summary': {}
        }
        
        for claim in claims:
            result = self.orchestrate_claim(claim)
            results['claim_results'].append(result)
        
        # Generate batch summary
        results['batch_summary'] = self._generate_batch_summary(results['claim_results'])
        
        return results
    
    def _generate_batch_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for batch"""
        
        total = len(results)
        successful = sum(1 for r in results if r['pipeline_status'] == 'SUCCESS')
        approved = sum(1 for r in results if r.get('final_decision') == 'APPROVE')
        denied = sum(1 for r in results if r.get('final_decision') == 'DENY')
        partial = sum(1 for r in results if r.get('final_decision') == 'APPROVE_PARTIAL')
        
        total_approved_amount = sum(
            r.get('approved_amount', 0) for r in results 
            if r['pipeline_status'] == 'SUCCESS'
        )
        
        return {
            'processed': total,
            'successful_pipeline': successful,
            'pipeline_success_rate': successful / total if total > 0 else 0,
            'approvals': {
                'approved': approved,
                'denied': denied,
                'partial': partial,
                'with_review': sum(1 for r in results if 'REVIEW' in r.get('final_decision', ''))
            },
            'financial_summary': {
                'total_approved_amount': total_approved_amount,
                'avg_claim_amount': total_approved_amount / approved if approved > 0 else 0
            }
        }
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get overall pipeline statistics"""
        total = self.pipeline_metrics['total_claims']
        
        return {
            'agent': self.name,
            'total_claims_processed': total,
            'successful': self.pipeline_metrics['successful_claims'],
            'failed': self.pipeline_metrics['failed_claims'],
            'success_rate': self.pipeline_metrics['successful_claims'] / total if total > 0 else 0,
            'stage_failures': self.pipeline_metrics['stage_failures'],
            'sub_agent_metrics': {
                'bronze': self.bronze.get_status(),
                'silver': self.silver.get_status(),
                'gold': self.gold.get_status()
            }
        }

