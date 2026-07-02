"""
Supervisor Agent - Oversees the entire multi-agent pipeline
Monitors performance, handles escalations, resolves conflicts, and generates reports
"""

from typing import Any, Dict, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Supervises and coordinates the multi-agent system"""
    
    def __init__(self, orchestrator_agent):
        self.name = "Supervisor Agent"
        self.orchestrator = orchestrator_agent
        
        self.oversight_metrics = {
            'total_batches_supervised': 0,
            'escalations': [],
            'conflicts': [],
            'interventions': []
        }
        
        # Thresholds for intervention
        self.thresholds = {
            'min_quality_score': 0.75,
            'max_fraud_risk': 0.70,
            'max_failure_rate': 0.20,
            'min_pipeline_success_rate': 0.80
        }
    
    def supervise_batch(self, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Supervise batch processing with oversight
        
        Args:
            claims: Batch of claims to process
            
        Returns:
            Supervised batch results with oversight actions
        """
        print(f"\n{'*'*60}")
        print(f"* SUPERVISOR: Overseeing batch of {len(claims)} claims")
        print(f"{'*'*60}\n")
        
        self.oversight_metrics['total_batches_supervised'] += 1
        
        # Execute batch through orchestrator
        batch_result = self.orchestrator.orchestrate_batch(claims)
        
        # Perform oversight analysis
        oversight_analysis = self._analyze_batch_performance(batch_result)
        
        # Identify escalations
        escalations = self._identify_escalations(batch_result)
        
        # Generate interventions if needed
        interventions = self._generate_interventions(oversight_analysis, escalations)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(batch_result)
        
        # Create final supervision report
        supervision_report = {
            'batch_id': batch_result['batch_id'],
            'supervision_timestamp': datetime.now().isoformat(),
            'batch_results': batch_result,
            'oversight_analysis': oversight_analysis,
            'escalations': escalations,
            'conflicts': conflicts,
            'interventions': interventions,
            'supervisor_recommendation': self._generate_recommendation(oversight_analysis, escalations)
        }
        
        # Store escalations and conflicts for audit
        if escalations:
            self.oversight_metrics['escalations'].extend(escalations)
        if conflicts:
            self.oversight_metrics['conflicts'].extend(conflicts)
        if interventions:
            self.oversight_metrics['interventions'].extend(interventions)
        
        print(f"\n{'~'*60}")
        print(f"~ SUPERVISOR ANALYSIS COMPLETE")
        print(f"~ Escalations: {len(escalations)} | Conflicts: {len(conflicts)} | Interventions: {len(interventions)}")
        print(f"{'~'*60}\n")
        
        return supervision_report
    
    def _analyze_batch_performance(self, batch_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall batch performance against SLAs and thresholds"""
        
        summary = batch_result['batch_summary']
        total = batch_result['total_claims']
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': {
                'pipeline_success_rate': summary['pipeline_success_rate'],
                'approval_rate': summary['approvals']['approved'] / total if total > 0 else 0,
                'denial_rate': summary['approvals']['denied'] / total if total > 0 else 0,
                'partial_approval_rate': summary['approvals']['partial'] / total if total > 0 else 0,
                'manual_review_rate': summary['approvals']['with_review'] / total if total > 0 else 0
            },
            'sla_compliance': {},
            'quality_assessment': {},
            'recommendations': []
        }
        
        # Check SLA compliance
        if summary['pipeline_success_rate'] < self.thresholds['min_pipeline_success_rate']:
            analysis['sla_compliance']['pipeline_success'] = 'FAILED'
            analysis['recommendations'].append(
                f"Pipeline success rate {summary['pipeline_success_rate']:.2%} below threshold "
                f"{self.thresholds['min_pipeline_success_rate']:.2%}"
            )
        else:
            analysis['sla_compliance']['pipeline_success'] = 'PASSED'
        
        # Quality assessment
        avg_quality = sum(
            r.get('processing_stages', {}).get('bronze', {}).get('quality_score', 0)
            for r in batch_result['claim_results']
        ) / total if total > 0 else 0
        
        if avg_quality < self.thresholds['min_quality_score']:
            analysis['quality_assessment']['data_quality'] = 'LOW'
            analysis['recommendations'].append(
                f"Average data quality {avg_quality:.2%} below threshold"
            )
        else:
            analysis['quality_assessment']['data_quality'] = 'ACCEPTABLE'
        
        return analysis
    
    def _identify_escalations(self, batch_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify claims requiring escalation"""
        
        escalations = []
        
        for result in batch_result['claim_results']:
            escalation_reasons = []
            
            # Handle failed claims
            if result.get('pipeline_status') != 'SUCCESS':
                escalation_reasons.append(f"Pipeline failure: {result.get('pipeline_status')}")
            else:
                # Check for high fraud risk
                silver_data = result.get('processing_stages', {}).get('silver')
                if silver_data:
                    fraud_risk = silver_data.get('fraud_risk', 0)
                    if fraud_risk > self.thresholds['max_fraud_risk']:
                        escalation_reasons.append(f"High fraud risk: {fraud_risk:.2%}")
                    
                    # Check for multiple issues found
                    silver_issues = silver_data.get('issues', 0)
                    if silver_issues > 2:
                        escalation_reasons.append(f"Multiple issues found: {silver_issues}")
            
            # Check for manual review recommendations
            if 'REVIEW' in result.get('final_decision', ''):
                escalation_reasons.append(f"Decision: {result.get('final_decision')}")
            
            if escalation_reasons:
                escalations.append({
                    'claim_id': result['claim_id'],
                    'escalation_level': 'HIGH' if result['pipeline_status'] != 'SUCCESS' else 'MEDIUM',
                    'reasons': escalation_reasons,
                    'timestamp': datetime.now().isoformat(),
                    'assigned_to': 'Manual Review Queue'
                })
        
        return escalations
    
    def _detect_conflicts(self, batch_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts or inconsistencies in agent decisions"""
        
        conflicts = []
        
        for result in batch_result['claim_results']:
            conflict_details = []
            
            stages = result.get('processing_stages', {})
            
            # Check for Silver-Gold decision conflicts
            silver_approved = result.get('approved_amount', 0) > 0
            gold_recommendation = result.get('final_decision', '')
            
            if silver_approved and 'DENY' in gold_recommendation:
                conflict_details.append('Silver enriched positive but Gold denied')
            
            # Check for confidence vs decision alignment
            confidence = result.get('confidence', 0)
            if 'WITH_REVIEW' in gold_recommendation and confidence > 0.90:
                conflict_details.append('High confidence but recommending review')
            
            if conflict_details:
                conflicts.append({
                    'claim_id': result['claim_id'],
                    'conflict_type': 'AGENT_DECISION_MISMATCH',
                    'details': conflict_details,
                    'timestamp': datetime.now().isoformat(),
                    'requires_attention': True
                })
        
        return conflicts
    
    def _generate_interventions(self, analysis: Dict[str, Any], escalations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommended interventions based on analysis"""
        
        interventions = []
        
        # Intervention 1: Low pipeline success
        if analysis['sla_compliance'].get('pipeline_success') == 'FAILED':
            interventions.append({
                'type': 'PROCESS_REVIEW',
                'priority': 'HIGH',
                'action': 'Review Bronze and Silver agent configurations',
                'target': 'Pipeline Configuration',
                'estimated_impact': 'Improve pipeline success rate'
            })
        
        # Intervention 2: Low data quality
        if analysis['quality_assessment'].get('data_quality') == 'LOW':
            interventions.append({
                'type': 'DATA_QUALITY_REVIEW',
                'priority': 'MEDIUM',
                'action': 'Enhance Bronze agent validation rules',
                'target': 'Bronze Agent',
                'estimated_impact': 'Improve data quality scores'
            })
        
        # Intervention 3: High escalations
        if len(escalations) > 5:
            interventions.append({
                'type': 'ESCALATION_REVIEW',
                'priority': 'MEDIUM',
                'action': 'Review and tighten escalation thresholds',
                'target': 'Escalation Logic',
                'estimated_impact': 'Reduce manual workload'
            })
        
        return interventions
    
    def _generate_recommendation(self, analysis: Dict[str, Any], escalations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall recommendation for batch"""
        
        if analysis['sla_compliance'].get('pipeline_success') == 'FAILED':
            recommendation = 'BATCH_REVIEW_REQUIRED'
            action = 'Manual review of entire batch recommended'
        elif len(escalations) > len([e for e in escalations if e['escalation_level'] == 'HIGH']) / 2:
            recommendation = 'ESCALATION_THRESHOLD_EXCEEDED'
            action = 'Escalation count high - consider workflow optimization'
        elif analysis['quality_assessment'].get('data_quality') == 'LOW':
            recommendation = 'QUALITY_IMPROVEMENT_NEEDED'
            action = 'Batch quality acceptable but improvements recommended'
        else:
            recommendation = 'APPROVED'
            action = 'Batch meets all SLAs and quality standards'
        
        return {
            'status': recommendation,
            'primary_action': action,
            'timestamp': datetime.now().isoformat(),
            'requires_manual_intervention': recommendation != 'APPROVED'
        }
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report"""
        
        print(f"\n{'='*60}")
        print(f"SUPERVISOR: Generating System Health Report")
        print(f"{'='*60}\n")
        
        orchestrator_metrics = self.orchestrator.get_pipeline_metrics()
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'system_health': {
                'status': 'HEALTHY' if orchestrator_metrics['success_rate'] > 0.95 else 'DEGRADED',
                'overall_success_rate': orchestrator_metrics['success_rate'],
                'batches_supervised': self.oversight_metrics['total_batches_supervised']
            },
            'pipeline_metrics': orchestrator_metrics,
            'oversight_summary': {
                'total_escalations': len(self.oversight_metrics['escalations']),
                'total_conflicts': len(self.oversight_metrics['conflicts']),
                'total_interventions': len(self.oversight_metrics['interventions'])
            },
            'critical_issues': self._identify_critical_issues(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _identify_critical_issues(self) -> List[str]:
        """Identify any critical issues in system"""
        
        issues = []
        metrics = self.orchestrator.get_pipeline_metrics()
        
        if metrics['success_rate'] < 0.80:
            issues.append('Pipeline success rate below 80% threshold')
        
        if metrics['stage_failures'].get('bronze', 0) > 5:
            issues.append('High number of Bronze stage failures')
        
        if len(self.oversight_metrics['escalations']) > 20:
            issues.append('Escalation count exceeds acceptable threshold')
        
        return issues
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for system improvement"""
        
        recommendations = []
        
        if self.oversight_metrics['total_batches_supervised'] > 0:
            escalation_rate = len(self.oversight_metrics['escalations']) / self.oversight_metrics['total_batches_supervised']
            if escalation_rate > 0.15:
                recommendations.append('Review and optimize escalation thresholds')
        
        if len(self.oversight_metrics['conflicts']) > 5:
            recommendations.append('Investigate agent decision conflicts')
        
        if len(self.oversight_metrics['interventions']) > 10:
            recommendations.append('Execute pending process interventions')
        
        recommendations.append('Continue monitoring SLA compliance')
        
        return recommendations
    
    def get_supervision_metrics(self) -> Dict[str, Any]:
        """Get supervision statistics"""
        
        return {
            'agent': self.name,
            'batches_supervised': self.oversight_metrics['total_batches_supervised'],
            'escalations': len(self.oversight_metrics['escalations']),
            'conflicts_detected': len(self.oversight_metrics['conflicts']),
            'interventions_recommended': len(self.oversight_metrics['interventions']),
            'thresholds': self.thresholds
        }

