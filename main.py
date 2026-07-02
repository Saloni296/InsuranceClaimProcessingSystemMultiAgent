"""
Main Execution Script - Demonstrates the complete Multi-Agent Insurance Processing System

Architecture:
    Supervisor Agent (Oversight)
        ↓
    Orchestrator Agent (Coordination)
        ↓
    Bronze → Silver → Gold Agents (Processing Pipeline)
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Import agents
from agents.bronze_agent import BronzeAgent
from agents.silver_agent import SilverAgent
from agents.gold_agent import GoldAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.supervisor_agent import SupervisorAgent


def load_claims(file_path: str) -> list:
    """Load sample claims from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['claims']


def print_section_header(title: str, char: str = "=") -> None:
    """Print formatted section header"""
    width = 70
    print(f"\n{char*width}")
    print(f"{title.center(width)}")
    print(f"{char*width}\n")


def print_claim_summary(claim_result: dict) -> None:
    """Print formatted claim processing summary"""
    print(f"\n{'-'*70}")
    print(f"Claim ID: {claim_result['claim_id']}")
    print(f"Pipeline Status: {claim_result['pipeline_status']}")
    print(f"Final Decision: {claim_result['final_decision']}")
    
    if claim_result['pipeline_status'] == 'SUCCESS':
        print(f"Approved Amount: ${claim_result.get('approved_amount', 0):.2f}")
        print(f"Patient Responsibility: ${claim_result.get('patient_responsibility', 0):.2f}")
        print(f"Confidence Score: {claim_result.get('confidence', 0):.2%}")
        if claim_result.get('missing_documents'):
            print("Missing Documents:")
            for md in claim_result.get('missing_documents', []):
                print(f"  - {md}")
        if claim_result.get('follow_up_questions'):
            print("Follow-up Questions:")
            for q in claim_result.get('follow_up_questions', []):
                print(f"  - {q}")
    else:
        print(f"Reason: {claim_result.get('reason', 'N/A')}")
    
    print(f"{'-'*70}")


def print_batch_summary(batch_result: dict) -> None:
    """Print formatted batch processing summary"""
    summary = batch_result['batch_summary']
    
    print_section_header("BATCH PROCESSING SUMMARY", "=")
    print(f"Batch ID: {batch_result['batch_id']}")
    print(f"Total Claims: {batch_result['total_claims']}")
    print(f"Successful Pipeline: {summary['successful_pipeline']}/{batch_result['total_claims']}")
    print(f"Success Rate: {summary['pipeline_success_rate']:.2%}")
    print()
    print(f"Approvals: {summary['approvals']['approved']}")
    print(f"Denials: {summary['approvals']['denied']}")
    print(f"Partial Approvals: {summary['approvals']['partial']}")
    print(f"With Review: {summary['approvals']['with_review']}")
    print()
    print(f"Total Approved Amount: ${summary['financial_summary']['total_approved_amount']:.2f}")
    print(f"Average Claim Amount: ${summary['financial_summary']['avg_claim_amount']:.2f}")


def print_supervision_report(supervision_report: dict) -> None:
    """Print formatted supervision report"""
    print_section_header("SUPERVISOR REPORT", "*")
    
    batch = supervision_report['batch_results']
    analysis = supervision_report['oversight_analysis']
    
    print(f"Batch ID: {supervision_report['batch_id']}")
    print(f"Timestamp: {supervision_report['supervision_timestamp']}")
    print()
    
    print("Performance Metrics:")
    perf = analysis['performance_metrics']
    print(f"  - Pipeline Success Rate: {perf['pipeline_success_rate']:.2%}")
    print(f"  - Approval Rate: {perf['approval_rate']:.2%}")
    print(f"  - Denial Rate: {perf['denial_rate']:.2%}")
    print(f"  - Manual Review Rate: {perf['manual_review_rate']:.2%}")
    print()
    
    print("SLA Compliance:")
    for metric, status in analysis['sla_compliance'].items():
        print(f"  - {metric}: {status}")
    print()
    
    print("Quality Assessment:")
    for metric, status in analysis['quality_assessment'].items():
        print(f"  - {metric}: {status}")
    print()
    
    if supervision_report['escalations']:
        print(f"Escalations Found: {len(supervision_report['escalations'])}")
        for esc in supervision_report['escalations'][:3]:  # Show first 3
            print(f"  - Claim {esc['claim_id']}: Level {esc['escalation_level']}")
        print()
    
    if supervision_report['conflicts']:
        print(f"Conflicts Detected: {len(supervision_report['conflicts'])}")
        for conf in supervision_report['conflicts'][:2]:  # Show first 2
            print(f"  - Claim {conf['claim_id']}: {conf['conflict_type']}")
        print()
    
    if supervision_report['interventions']:
        print(f"Interventions Recommended: {len(supervision_report['interventions'])}")
        for interv in supervision_report['interventions']:
            print(f"  - {interv['type']} (Priority: {interv['priority']})")
        print()
    
    print("Supervisor Recommendation:")
    rec = supervision_report['supervisor_recommendation']
    print(f"  Status: {rec['status']}")
    print(f"  Action: {rec['primary_action']}")


def print_health_report(health_report: dict) -> None:
    """Print formatted system health report"""
    print_section_header("SYSTEM HEALTH REPORT", "#")
    
    health = health_report['system_health']
    metrics = health_report['pipeline_metrics']
    oversight = health_report['oversight_summary']
    
    print(f"Report Timestamp: {health_report['report_timestamp']}")
    print()
    
    print("System Status:")
    print(f"  Overall Status: {health['status']}")
    print(f"  Success Rate: {health['overall_success_rate']:.2%}")
    print(f"  Batches Supervised: {health['batches_supervised']}")
    print()
    
    print("Pipeline Metrics:")
    print(f"  Total Processed: {metrics['total_claims_processed']}")
    print(f"  Successful: {metrics['successful']}")
    print(f"  Failed: {metrics['failed']}")
    print(f"  Overall Success Rate: {metrics['success_rate']:.2%}")
    print()
    
    print("Stage Failures:")
    for stage, count in metrics['stage_failures'].items():
        print(f"  - {stage.upper()}: {count}")
    print()
    
    print("Oversight Summary:")
    print(f"  Total Escalations: {oversight['total_escalations']}")
    print(f"  Total Conflicts: {oversight['total_conflicts']}")
    print(f"  Total Interventions: {oversight['total_interventions']}")
    print()
    
    if health_report['critical_issues']:
        print("Critical Issues:")
        for issue in health_report['critical_issues']:
            print(f"  - {issue}")
        print()
    
    if health_report['recommendations']:
        print("Recommendations:")
        for rec in health_report['recommendations']:
            print(f"  - {rec}")
        print()


def main():
    """Main execution function"""
    
    print_section_header("INSURANCE CLAIM PROCESSING SYSTEM", "#")
    print("Multi-Agent Architecture: Orchestrator + Bronze/Silver/Gold + Supervisor")
    print()
    
    # Initialize agents
    print("Initializing agents...")
    bronze_agent = BronzeAgent()
    silver_agent = SilverAgent()
    gold_agent = GoldAgent()
    orchestrator_agent = OrchestratorAgent(bronze_agent, silver_agent, gold_agent)
    supervisor_agent = SupervisorAgent(orchestrator_agent)
    print("[OK] All agents initialized\n")
    
    # Load claims (prefer GenAI sample if present)
    claims_file = Path(__file__).parent / "sample_claims_genai.json"
    if not claims_file.exists():
        claims_file = Path(__file__).parent / "sample_claims.json"
    if not claims_file.exists():
        print(f"[ERROR] Claims file not found: {claims_file}")
        sys.exit(1)

    # Support both formats: genai file is a list, legacy sample_claims.json has {'claims': [...]}
    if claims_file.name == 'sample_claims_genai.json':
        # Support BOM in JSON by using utf-8-sig
        with open(claims_file, 'r', encoding='utf-8-sig') as f:
            claims = json.load(f)
    else:
        claims = load_claims(str(claims_file))

    print(f"[OK] Loaded {len(claims)} claims from {claims_file.name}\n")
    
    # Process single claim (optional - for demo)
    print_section_header("PROCESSING INDIVIDUAL CLAIMS", "-")
    
    sample_claim = claims[0]
    print(f"Processing first claim: {sample_claim['claim_id']}")
    result = orchestrator_agent.orchestrate_claim(sample_claim)
    print_claim_summary(result)
    
    # Process batch with supervision
    print_section_header("BATCH PROCESSING WITH SUPERVISION", "=")
    
    supervision_report = supervisor_agent.supervise_batch(claims)
    
    # Print reports
    print_batch_summary(supervision_report['batch_results'])
    print_supervision_report(supervision_report)
    
    # Generate health report
    print_section_header("FINAL SYSTEM HEALTH CHECK", "#")
    
    health_report = supervisor_agent.generate_health_report()
    print_health_report(health_report)
    
    # Save results to file
    output_file = Path(__file__).parent / "processing_results.json"
    results_summary = {
        'execution_timestamp': datetime.now().isoformat(),
        'batch_results': supervision_report['batch_results'],
        'supervision_analysis': supervision_report,
        'system_health': health_report
    }
    
    with open(output_file, 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"\n[OK] Results saved to {output_file.name}")
    print_section_header("EXECUTION COMPLETE", "=")


if __name__ == "__main__":
    main()
