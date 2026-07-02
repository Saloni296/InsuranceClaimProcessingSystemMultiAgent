# Multi-Agent Insurance Processing System

## Overview

This is a comprehensive multi-agent architecture for processing health insurance claims through multiple quality tiers (Bronze → Silver → Gold) with centralized orchestration and supervision.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERVISOR AGENT                         │
│  (Oversight, Escalation Management, Health Reporting)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│               ORCHESTRATOR AGENT                            │
│    (Coordinates Pipeline, Batch Processing)                │
└──────────────┬──────────────┬───────────────┬───────────────┘
               │              │               │
        ┌──────▼─────┐   ┌────▼─────┐   ┌─────▼─────┐
        │  INGEST    │   │   OCR    │   │   LLM     │
        │  (Upload)  │──▶│ Agent    │──▶│ (Summarize│
        │  Uploads   │   │ Extract) │   │  & Analyze)│
        └────────────┘   └──────────┘   └────────────┘
               │                             │
               └───────────┬─────────────────┘
                           │
                    ┌──────▼────────┐
                    │  BRONZE AGENT │
                    │ Validation &   │
                    │ Attach OCR+LLM  │
                    └──────┬─────────┘
                           │
                    ┌──────▼────────┐
                    │  SILVER AGENT │
                    │ Policy check  │
                    │ Enrichment/QA  │
                    └──────┬─────────┘
                           │
                    ┌──────▼────────┐
                    │  GOLD AGENT   │
                    │ Completeness  │
                    │ Follow-ups &  │
                    │ Final Decision│
                    └───────────────┘
```

## Agent Responsibilities

### 0. Ingest / Upload (Customer)
- **Purpose**: Entry point for customers submitting claims and supporting documents
- **Inputs**: Photos (damage, injuries), Invoices, Signed claim forms, Optional notes
- **Output**: Raw claim package with list of uploaded files and metadata

### OCR Agent
- **Purpose**: Extract structured text from uploaded documents (photos, PDFs)
- **Responsibilities**:
  - Run OCR on images and PDFs
  - Produce cleaned text snippets per file
  - Normalize dates, amounts, provider names when possible
  - Attach OCR outputs to the claim payload for downstream consumption

**Output**: ocr_texts: { filename: extracted_text }

### LLM Agent (Shared)
- **Purpose**: Provide GenAI capabilities used by Bronze/Silver/Gold tiers
- **Responsibilities**:
  - Summarize incident from OCR outputs
  - Compare summarized claim against policy documents
  - Identify missing documents and generate follow-up questions
  - Return structured responses suitable for programmatic decisions

**Output**: incident_summary, policy_check, completeness_assessment

### 1. Bronze Agent - Ingestion, Validation & Summarization
- **Purpose**: Initial validation + attach OCR and LLM-generated summary
- **Responsibilities**:
  - Validate required fields and data types
  - Calculate data quality score and flag basic issues
  - Attach OCR outputs (if present) to the cleaned record
  - Call LLM summarizer with OCR texts to produce incident_summary

**Output**: Validated claim with incident_summary and data quality metrics

### 2. Silver Agent - Policy Coverage Check & Enrichment
- **Purpose**: Enrich claim with policy context and detect anomalies
- **Responsibilities**:
  - Verify policy existence and fetch policy text
  - Use LLM to compare incident_summary against policy text to assess coverage
  - Perform provider network checks and fraud pattern detection
  - Calculate eligible amounts and apply enrichment metadata

**Output**: Enriched claim data including policy_check results and fraud risk

### 3. Gold Agent - Completeness Check, Follow-ups & Decisioning
- **Purpose**: Ensure claim completeness, generate follow-ups, and make final decision
- **Responsibilities**:
  - Use LLM to identify missing documents from OCR outputs (e.g., missing invoice, missing signatures)
  - Generate follow-up questions for the customer to collect missing items or clarifications
  - Apply coverage limits, calculate patient responsibility, and produce approval/denial/partial decisions
  - Produce final audit trail including LLM-assisted rationale

**Output**: Final decision, missing_documents list, follow_up_questions, payment instructions, audit trail

### 4. Orchestrator Agent - Workflow Coordination
- **Purpose**: Coordinate the full GenAI-enhanced pipeline
- **Responsibilities**:
  - Manage pre-processing (OCR), Bronze → Silver → Gold stages
  - Propagate OCR and LLM outputs between stages
  - Handle retries, failures, and stage-specific fallbacks
  - Aggregate metrics and orchestrate batch processing

**Output**: Processed claim with complete stage outputs and follow-ups

### 5. Supervisor Agent - System Oversight
- **Purpose**: Monitor pipeline health, SLA, and guide escalations
- **Responsibilities**:
  - Supervise batch results and identify systemic issues
  - Track SLA compliance and LLM performance signals (e.g., low-confidence summaries)
  - Recommend manual reviews and escalations when LLM or OCR confidence is low
  - Generate health reports and intervention suggestions

**Output**: Supervision reports with actionable interventions and escalations

## Data Flow

### Single Claim Processing (GenAI-enhanced)
```
Customer uploads claim + supporting files (photos, invoices, forms)
    ↓
[Orchestrator] → Pre-stage: OCR Agent extracts text from uploads
    ↓
[Bronze Agent] → Validate data fields; attach OCR texts; call LLM to summarize incident
    ↓ (Success)
[Silver Agent] → Fetch policy text; call LLM to compare summary vs policy; enrich with fraud checks
    ↓ (Success)
[Gold Agent] → Call LLM to identify missing documents and generate follow-ups; apply coverage limits; make decision
    ↓ (Success)
Final Claim Output
    ├─ Decision: APPROVE / DENY / APPROVE_PARTIAL / APPROVE_WITH_REVIEW
    ├─ Approved Amount & Payment Instructions
    ├─ Missing Documents (if any) and Follow-up Questions for Customer
    └─ Audit Trail including LLM-derived rationale
```

### Batch Processing
```
Batch of Raw Claim Packages
    ↓
[Orchestrator] → Run OCR, then process claims through Bronze → Silver → Gold pipeline
    ↓
[Supervisor] → Aggregate results, evaluate SLA & LLM/OCR confidence, identify escalations or systemic issues
    ├─ Performance metrics
    ├─ Identify escalations
    ├─ Detect conflicts
    ├─ Recommend interventions (manual review, retrain prompts, re-run OCR)
    └─ Health status
```

## Key Features

### GenAI Enhancements
- OCR extraction for uploaded photos/PDFs to create machine-readable text
- LLM-based incident summarization to convert multi-file evidence into a concise incident summary
- LLM-grounded policy coverage checks (compare summary to policy text and identify coverage gaps)
- LLM-assisted completeness checks that identify missing documents and generate human-friendly follow-up questions
- Structured LLM outputs to keep decisions auditable and machine-actionable

### Data Quality Scoring (Bronze)
- Base score: 0.8 (for passing validation)
- +0.1 for presence of attachments/OCR outputs
- +0.05 for complete diagnosis codes
- Maximum: 1.0

### Fraud Risk Detection (Silver)
- High claim amounts (>$20,000): +0.2
- Same-day claims: +0.1
- Missing diagnosis codes: +0.15
- Service date after claim date: +0.25
- Threshold for escalation: >0.70

### Coverage Limits (Gold)
- Office Visit: $500
- Emergency: $5,000
- Surgery: $50,000
- Imaging: $2,000
- Lab: $300
- Default: $1,000

### Cost Sharing
- **In-Network**: 20% coinsurance, $30 copay
- **Out-of-Network**: 40% coinsurance, $50 copay, deductible applies

### SLA & Confidence Thresholds
- Minimum pipeline success rate: 80%
- Minimum data quality score: 75%
- Maximum fraud risk: 70%
- Minimum LLM confidence threshold (recommended): 0.7 — below this, flag for manual review
- Acceptable processing time: <5 seconds per claim (excluding OCR/LLM network latency)

## Usage

### Installation
```bash
pip install -r requirements.txt
```

### Running the System
```bash
python main.py
```

### Processing Individual Claim
```python
from bronze_agent import BronzeAgent
from silver_agent import SilverAgent
from gold_agent import GoldAgent
from orchestrator_agent import OrchestratorAgent

# Initialize agents
bronze = BronzeAgent()
silver = SilverAgent()
gold = GoldAgent()
orchestrator = OrchestratorAgent(bronze, silver, gold)

# Process claim
claim = {"claim_id": "CLM-001", ...}
result = orchestrator.orchestrate_claim(claim)
```

### Processing Batch with Supervision
```python
from supervisor_agent import SupervisorAgent

supervisor = SupervisorAgent(orchestrator)
claims = [claim1, claim2, claim3, ...]

# Supervise batch
report = supervisor.supervise_batch(claims)
```

## Output Files

### processing_results.json
Contains:
- Batch processing results
- Individual claim decisions
- Supervision analysis
- System health report

## Metrics & Monitoring

### Pipeline Metrics
- Total claims processed
- Successful claims
- Failed claims
- Success rate by stage

### Supervision Metrics
- Escalations identified
- Conflicts detected
- Interventions recommended
- SLA compliance status

### Financial Metrics
- Total approved amount
- Average claim amount
- Approval rate
- Cost savings vs claims

## Error Handling

### Bronze Stage Failures
- Missing required fields
- Invalid data types
- Invalid dates
- Out-of-range values

**Resolution**: Escalate to manual review

### Silver Stage Failures
- Policy not found
- Service code invalid
- High fraud risk
- Multiple validation issues

**Resolution**: Flag for investigation

### Gold Stage Failures
- Coverage limit exceeded
- Business rule violations
- Decision logic errors

**Resolution**: Manual intervention

## Extensibility

The system is designed to be extended:

### Adding New Service Categories
Modify `gold_agent.py` coverage_limits:
```python
self.coverage_limits = {
    'new_category': 10000.0,
    ...
}
```

### Adding Custom Business Rules
Extend `_apply_business_rules()` in Silver Agent:
```python
def _apply_business_rules(self, data):
    # Add new rules
    rules['new_rule'] = result
```

### Adding New Fraud Patterns
Extend `_detect_fraud_patterns()` in Silver Agent:
```python
# New pattern detection
if condition:
    risk_score += 0.20
```

## Performance Considerations

- **Throughput**: ~1000 claims/minute per instance
- **Processing Time**: ~50ms per claim (3-stage pipeline)
- **Memory**: ~100MB for typical batch of 1000 claims
- **Scalability**: Agents can be parallelized for batch processing

## Security & Compliance

- **Audit Trail**: Complete record of all decisions
- **Data Privacy**: No PII storage in logs
- **Access Control**: Supervisor validates all decisions
- **Compliance**: Tracks rejection reasons for HIPAA compliance

## Future Enhancements

1. **Machine Learning**: Integrate ML models for fraud detection
2. **Real-time Monitoring**: WebSocket-based status updates
3. **Advanced Analytics**: Predictive claim outcomes
4. **Integration APIs**: Connect to external systems
5. **Performance Tuning**: Async processing and caching
6. **Advanced Conflict Resolution**: Intelligent conflict detection and resolution

---

**Version**: 1.0  
**Last Updated**: 2024-06-23
