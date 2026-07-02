# Insurance Multi-Agent System - Quick Start Guide

## 🎯 What You Have

A complete **production-ready multi-agent system** for processing health insurance claims with:

- **5 Intelligent Agents** working in tandem
- **4-Stage Processing Pipeline** (Bronze→Silver→Gold + Supervision)
- **Fraud Detection & Risk Assessment**
- **Compliance & Audit Trails**
- **Performance Monitoring & Health Reports**

---

## 📋 File Directory

```
Insurance_UseCase/
│
├─ MAIN AGENTS (Core Logic)
│  ├── bronze_agent.py          [Validation, attach OCR & LLM summary]
│  ├── silver_agent.py          [Policy check (LLM) & Enrichment]
│  ├── gold_agent.py            [Completeness (LLM), Decisions & Payment]
│  ├── orchestrator_agent.py    [Pipeline Coordinator & OCR pre-stage]
│  ├── ocr_agent.py             [OCR extraction from uploads]
│  ├── llm_agent.py             [LLM wrappers: summarization, policy check, follow-ups]
│  └── supervisor_agent.py      [System Oversight]
│
├─ EXECUTION
│  ├── main.py                  [Run the complete system]
│  └── sample_claims.json       [Test data: 4 insurance claims]
│  └── sample_claims_genai.json [GenAI demo claim with uploads]
│
├─ DOCUMENTATION
│  ├── README.md                [Complete system documentation]
│  ├── CONFIGURATION.md         [Tuning & deployment settings]
│  ├── USE_CASE.md             [Business use case description]
│  └── QUICK_START.md          [This file]
│
└─ OUTPUTS
   └── processing_results.json  [Execution results with audit trails]
```

---

## 🚀 Running the System

### Option 1: Run Complete System Demo
```bash
python main.py
```
This will:
1. Process 4 sample claims through the pipeline
2. Generate supervision reports
3. Create system health report
4. Save all results to `processing_results.json`

### Option 2: Process Single Claim
```python
import json
from orchestrator_agent import OrchestratorAgent
from bronze_agent import BronzeAgent
from silver_agent import SilverAgent
from gold_agent import GoldAgent

# Load sample claim
with open('sample_claims.json') as f:
    claims = json.load(f)['claims']

# Initialize agents
bronze = BronzeAgent()
silver = SilverAgent()
gold = GoldAgent()
orchestrator = OrchestratorAgent(bronze, silver, gold)

# Process single claim
result = orchestrator.orchestrate_claim(claims[0])
print(json.dumps(result, indent=2, default=str))
```

### Option 3: Batch Processing with Supervision
```python
from supervisor_agent import SupervisorAgent
import json

with open('sample_claims.json') as f:
    claims = json.load(f)['claims']

# Process with supervision
supervisor = SupervisorAgent(orchestrator)
report = supervisor.supervise_batch(claims)

print(f"Pipeline Success Rate: {report['batch_results']['batch_summary']['pipeline_success_rate']:.2%}")
print(f"Escalations: {len(report['escalations'])}")
print(f"Interventions: {len(report['interventions'])}")
```

---

## 🔍 Understanding the Pipeline

### Data Flow

```
Customer uploads claim + files (photos, invoices, forms)
    ↓
┌─────────────────────────────────────────────────────┐
│ ORCHESTRATOR - Pre-stage (OCR)                      │
│ ✓ Extract text from uploaded images & PDFs          │
│ ✓ Normalize amounts & dates when possible           │
└────────────┬────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────┐
│ BRONZE AGENT - Validation & LLM Summary             │
│ ✓ Schema validation                                 │
│ ✓ Attach OCR outputs                                │
│ ✓ Call LLM to summarize incident                    │
│ ✓ Data quality scoring                              │
└────────────┬────────────────────────────────────────┘
             ↓
       [SUCCESS?]
        ╱       ╲
      YES       NO → [ESCALATE & FAIL]
      ↓
┌─────────────────────────────────────────────────────┐
│ SILVER AGENT - Policy Check (LLM) & Enrichment      │
│ ✓ Fetch policy text                                 │
│ ✓ Use LLM to compare summary vs policy              │
│ ✓ Fraud detection & eligible amount calculation     │
└────────────┬────────────────────────────────────────┘
             ↓
       [SUCCESS?]
        ╱       ╲
      YES       NO → [ESCALATE & FAIL]
      ↓
┌─────────────────────────────────────────────────────┐
│ GOLD AGENT - Completeness (LLM) & Decisions         │
│ ✓ Use LLM to detect missing documents & generate Qs │
│ ✓ Apply coverage limits & compute patient pay       │
│ ✓ Make final decision & generate audit trail        │
└────────────┬────────────────────────────────────────┘
             ↓
     FINAL DECISION
   ┌──────────────────────┐
   │ APPROVE              │
   │ DENY                 │
   │ APPROVE_PARTIAL      │
   │ APPROVE_WITH_REVIEW  │
   └──────────────────────┘
```

---

## 📊 Agent Responsibilities

### 🟦 Bronze Agent
**Input**: Raw claim JSON  
**Output**: Validated, clean claim data
- Validates 8 required fields
- Checks data types and ranges
- Calculates initial quality score
- Flags data inconsistencies

**Example**:
```
Input:  {"claim_id": "CLM-001", "claim_amount": "INVALID", ...}
Output: FAILED - Invalid claim amount: INVALID
```

### 🟩 Silver Agent
**Input**: Bronze-validated claim  
**Output**: Enriched data with risk assessment
- Verifies policy exists
- Checks provider network status
- Detects 5 different fraud patterns
- Applies business rules
- Calculates eligible amounts

**Example**:
```
Fraud Risk Patterns:
  - High amount (>$20k):     +0.20 risk
  - Same-day claim:          +0.10 risk
  - Missing diagnosis:       +0.15 risk
  - Service > Claim date:    +0.25 risk
```

### 🟨 Gold Agent
**Input**: Silver-enriched data  
**Output**: Final decision with payment details
- Applies coverage limits by category
- Calculates patient out-of-pocket
- Makes approval/denial decision
- Creates 4-step audit trail
- Generates payment reference

**Decision Logic**:
```
IF fraud_risk > 0.70:        DENY
IF policy_not_verified:      DENY
IF service_code_invalid:     DENY
IF excess_coverage_limit:    APPROVE_PARTIAL
IF issues_found > 2:         APPROVE_WITH_REVIEW
ELSE:                        APPROVE
```

### 🔵 Orchestrator Agent
**Input**: Raw claims (single or batch)  
**Output**: Processed claims with complete history
- Routes claims through pipeline
- Handles stage failures
- Coordinates batch processing
- Collects metrics
- Propagates errors with context

### 🔴 Supervisor Agent
**Input**: Batch processing results  
**Output**: Supervision report with recommendations
- Monitors SLA compliance (80% success)
- Identifies escalations (fraud, failures)
- Detects conflicts (agent disagreements)
- Generates health reports
- Recommends interventions

---

## 💰 Coverage Limits

| Service Category | Limit | Notes |
|------------------|-------|-------|
| Office Visit | $500 | Preventive care |
| Emergency | $5,000 | Emergency room visits |
| Surgery | $50,000 | Major procedures |
| Imaging | $2,000 | X-rays, MRI, CT |
| Lab | $300 | Lab tests |
| Default | $1,000 | Other services |

---

## 🚨 Fraud Risk Detection

The system detects 5 fraud patterns:

1. **High Claim Amount** (>$20k) → +20% risk
2. **Same-Day Claim** (claim_date == service_date) → +10% risk
3. **Missing Diagnosis** (empty diagnosis_codes) → +15% risk
4. **Date Anomaly** (service > claim date) → +25% risk
5. **Escalation Threshold** → Triggers at >70% risk

**Real Example from Test**:
- CLM-2024-004 (Knee Surgery)
  - Amount: $25,000 → 20% risk
  - Status: APPROVED but flagged for review

---

## 📈 Key Metrics

### Batch Results
```
Total Claims:    4
Successful:      3 (75%)
Failed:          1 (25%)

Approvals:
  - Fully Approved:     2 (50%)
  - Partial:            1 (25%)
  - Denied:             1 (25%)

Financial:
  - Total Approved:     $26,750.50
  - Average Approval:   $13,375.25
```

### System Health
```
Status:              DEGRADED
Success Rate:        80%
Escalations:         1
Conflicts:           0
Interventions:       2

SLA Thresholds:
  - Min Success Rate:     80%  ❌ Currently 75%
  - Min Data Quality:     75%  ✓ Currently 95%
  - Max Fraud Risk:       70%  ✓ Within limits
```

---

## 🎮 Test Scenarios

### Scenario 1: Valid In-Network Claim ✓
```json
{
  "claim_id": "CLM-2024-001",
  "claim_amount": 5000.00,
  "provider": {"network": "In-Network"},
  "service_code": "99214"
}
```
**Result**: APPROVE_PARTIAL ($500 limit reached)

### Scenario 2: Out-of-Network Claim ✓
```json
{
  "claim_id": "CLM-2024-002",
  "claim_amount": 1250.50,
  "provider": {"network": "Out-of-Network"}
}
```
**Result**: APPROVE (80% reimbursement for OON)

### Scenario 3: Invalid Data ✗
```json
{
  "claim_id": "CLM-2024-003",
  "claim_amount": "INVALID",
  "service_code": null
}
```
**Result**: DENIED at Bronze stage

### Scenario 4: High-Value Surgery ⚠️
```json
{
  "claim_id": "CLM-2024-004",
  "claim_amount": 25000.00,
  "service_description": "Total knee replacement"
}
```
**Result**: APPROVED (fraud flagged: 20% risk)

---

## 🔧 Customization Examples

### Change Coverage Limit
```python
# In gold_agent.py
self.coverage_limits['office_visit'] = 750  # was 500
```

### Add New Fraud Pattern
```python
# In silver_agent.py
def _detect_fraud_patterns(self, data):
    risk_score = 0.0
    # Add new pattern:
    if data['claim_amount'] > 50000:
        risk_score += 0.30  # Very high risk
    return risk_score
```

### Change SLA Threshold
```python
# In supervisor_agent.py
self.thresholds['min_pipeline_success_rate'] = 0.75  # was 0.80
```

---

## 📚 Further Reading

- **README.md** - Full system architecture and design
- **CONFIGURATION.md** - All configurable parameters
- **USE_CASE.md** - Business context and requirements
- **Code Comments** - Detailed explanations in each agent

---

## ✅ Checklist

Before deploying to production:

- [ ] Review fraud detection thresholds
- [ ] Update coverage limits per plan
- [ ] Configure cost-sharing percentages
- [ ] Set SLA targets
- [ ] Test with real claims data
- [ ] Integrate with payment system
- [ ] Set up monitoring dashboard
- [ ] Configure escalation queue
- [ ] Train support team
- [ ] Document business rules

---

## 🆘 Troubleshooting

### System shows "DEGRADED" status
→ Pipeline success rate is 75%, below 80% SLA
→ Solution: Review Bronze validation rules or increase SLA threshold

### Fraud risk score too high
→ Current formula may be too sensitive
→ Solution: Adjust weights in `_detect_fraud_patterns()`

### Claims not passing Silver stage
→ Policy/provider data might not match
→ Solution: Update mock databases or verify data source

### System not generating audit trails
→ Check Gold agent is running to completion
→ Solution: Review stage failure logs

---

## 🎓 Learning Resources

This system demonstrates:
- ✓ Multi-agent architecture patterns
- ✓ Pipeline processing design
- ✓ Error handling and escalation
- ✓ Performance monitoring
- ✓ Compliance and audit trails
- ✓ Risk detection and scoring
- ✓ Business rule engines
- ✓ System health dashboards

---

**Ready to process claims!** 🚀

Start with: `python main.py`

