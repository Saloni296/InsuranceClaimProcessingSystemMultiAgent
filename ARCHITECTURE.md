# System Architecture Visualization

## High-Level Flow Diagram

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    INSURANCE CLAIM PROCESSING SYSTEM                       ║
║                          Multi-Agent Architecture                          ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                         INPUT SOURCES                                     │
├──────────────────────────────────────────────────────────────────────────┤
│  • EDI Files              • API Requests           • Web Forms            │
│  • CSV Uploads            • Database Queries       • Email Attachments   │
└────────────────┬─────────────────────────────────────────────────┬───────┘
                 │                                                 │
                 └─────────────────────┬───────────────────────────┘
                                       │
                                       ▼
                    ╔══════════════════════════════════╗
                    ║   MAIN.PY - Orchestration      ║
                    ║  Loads & Routes Claims          ║
                    ╚═════────────────┬───────────────╝
                                      │
                 ┌────────────────────┼────────────────────┐
                 │                    │                    │
                 ▼                    ▼                    ▼
        ╔════════════════╗  ╔════════════════╗  ╔════════════════╗
        ║ BRONZE AGENT   ║  ║ BRONZE AGENT   ║  ║ BRONZE AGENT   ║
        ║                ║  ║                ║  ║                ║
        ║ Validation     ║  ║ Validation     ║  ║ Validation     ║
        ║ Score: 95%     ║  ║ Score: 95%     ║  ║ FAILED         ║
        ╚────────┬───────╝  ╚────────┬───────╝  ╚────────┬───────╝
                 │                    │                    │
           [SUCCESS]            [SUCCESS]            [FAILED]
                 │                    │                    │
                 ▼                    ▼                    ▼
        ╔════════════════╗  ╔════════════════╗  ╔════════════════╗
        ║ SILVER AGENT   ║  ║ SILVER AGENT   ║  │ Escalate       │
        ║                ║  ║                ║  │ to Supervisor  │
        ║ Enrichment     ║  ║ Enrichment     ║  │                │
        ║ Fraud: 0%      ║  ║ Fraud: 20%     ║  └────────────────┘
        ║ Network: IN    ║  ║ Network: OON   ║
        ╚────────┬───────╝  ╚────────┬───────╝
                 │                    │
           [SUCCESS]            [SUCCESS]
                 │                    │
                 ▼                    ▼
        ╔════════════════╗  ╔════════════════╗
        ║ GOLD AGENT     ║  ║ GOLD AGENT     ║
        ║                ║  ║                ║
        ║ Decision:      ║  ║ Decision:      ║
        ║ PARTIAL        ║  ║ APPROVE        ║
        ║ $500 limit     ║  ║ $25,000        ║
        ╚────────┬───────╝  ╚────────┬───────╝
                 │                    │
                 └────────────────────┼────────────────┐
                                      │                │
                                      ▼                ▼
                            ┌──────────────────────────────────┐
                            │      ORCHESTRATOR COLLECTS       │
                            │      • All stage results         │
                            │      • Metrics & statistics      │
                            │      • Error tracking            │
                            └────────────┬─────────────────────┘
                                         │
                                         ▼
                            ╔════════════════════════════════╗
                            ║ SUPERVISOR AGENT               ║
                            ║                                ║
                            ║ Analyzes Batch:                ║
                            ║ • Success Rate: 75%            ║
                            ║ • Escalations: 1               ║
                            ║ • Fraud Flags: 1               ║
                            ║ • Status: DEGRADED             ║
                            ║ • Recommendations: 2           ║
                            ╚════────────┬────────────────────╝
                                         │
                ┌────────────────────────┼────────────────────┐
                │                        │                    │
                ▼                        ▼                    ▼
        ╔════════════════╗     ╔════════════════╗  ╔════════════════╗
        ║ ESCALATIONS    ║     ║ AUDIT TRAILS   ║  ║ HEALTH REPORT  ║
        ║                ║     ║                ║  ║                ║
        ║ • CLM-003      ║     ║ • Timestamps   ║  ║ • SLA Status   ║
        ║ • High Risk    ║     ║ • Decisions    ║  ║ • Metrics      ║
        ║ • Manual       ║     ║ • Reasons      ║  ║ • Thresholds   ║
        ║   Review       ║     ║ • Stage Info   ║  ║ • Trends       ║
        ╚════════════════╝     ╚════════════════╝  ╚════════════════╝
                │                        │                    │
                └────────────────────────┼────────────────────┘
                                         │
                                         ▼
                        ╔════════════════════════════════╗
                        ║ OUTPUT & PERSISTENCE           ║
                        ║                                ║
                        ║ processing_results.json:       ║
                        ║ • Batch metadata               ║
                        ║ • All claim decisions          ║
                        ║ • Financial summary            ║
                        ║ • Supervisor recommendations   ║
                        ║ • System health metrics        ║
                        ╚════════════════════════════════╝
```

---

## Agent Interaction Diagram

```
                    ┌─────────────────────────────────┐
                    │    SUPERVISOR AGENT             │
                    │  (Oversight & Monitoring)       │
                    │                                 │
                    │ Methods:                        │
                    │ • supervise_batch()             │
                    │ • analyze_batch_performance()   │
                    │ • identify_escalations()        │
                    │ • detect_conflicts()            │
                    │ • generate_health_report()      │
                    └──────────┬──────────────────────┘
                               │ Monitors & Coordinates
                               │
        ┌──────────────────────┴──────────────────────┐
        │                                             │
        ▼                                             ▼
    ╔═══════════════════╗              ╔═════════════════════════╗
    │ ORCHESTRATOR      │              │ ERROR HANDLER           │
    │ AGENT             │              │ • Failed claims         │
    │                   │              │ • Escalations           │
    │ Methods:          │              │ • Conflicts             │
    │ • orchestrate_    │              ╚═════════════════════════╝
    │   claim()         │
    │ • orchestrate_    │
    │   batch()         │
    │ • get_pipeline_   │
    │   metrics()       │
    └───┬───┬───┬───────┘
        │   │   │
        │   │   └─────────────────────┐
        │   │                         │
        ▼   ▼   ▼                     ▼
    ╔═══╗ ╔═══╗ ╔═══╗          ╔═══════════════╗
    ║ B ║ ║ S ║ ║ G ║          ║ METRICS       ║
    ║ R ║─║ I ║─║ O ║          ║ • Processed   ║
    ║ O ║ ║ L ║ ║ L ║          ║ • Success Rate║
    ║ N ║ ║ V ║ ║ D ║          ║ • Throughput  ║
    ║ Z ║ ║ E ║ ║ A ║          ║ • Stage Fails ║
    ║ E ║ ║ R ║ ║ G ║          ╚═══════════════╝
    ╚═══╝ ╚═══╝ ╚═══╝
     ▲     ▲     ▲
     │     │     │
   DATA  DATA  DATA
   FLOW  FLOW  FLOW
     ↓     ↓     ↓
  
  Input → Validation → Enrichment → Decision → Output
```

---

## Data Flow Through Pipeline

```
CLAIM STAGES & TRANSFORMATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STAGE 1: BRONZE AGENT (Validation)
─────────────────────────────────────────────────────────
  Input:
    {
      "claim_id": "CLM-2024-001",
      "policy_id": "POL-12345",
      "claim_amount": "5000.00",        ← Can be string
      "service_code": "99214",
      "provider": {"name": "City General", "id": "PROV-789"},
      "policy_holder": {
        "name": "John Doe",
        "age": 35
      }
    }

  Checks:
    ✓ claim_id exists
    ✓ policy_id exists
    ✓ claim_amount numeric & positive
    ✓ service_code present
    ✓ Dates in YYYY-MM-DD format
    ✓ Age 0-150 range
    
  Output:
    {
      "success": true,
      "data": {
        "claim_id": "CLM-2024-001",
        "claim_amount": 5000.00,        ← Converted to float
        "data_quality_score": 0.95,     ← 95%
        "status": "bronze_validated"
      },
      "validation_errors": [],
      "warnings": []
    }


STAGE 2: SILVER AGENT (Enrichment)
─────────────────────────────────────────────────────────
  Input: Bronze output (validated data)

  Enrichments:
    • policy_verified: true
    • network_status: "IN-NETWORK"
    • cost_sharing: {
        "coinsurance": 0.20,
        "copay": 30.00,
        "deductible_applies": false
      }
    • fraud_risk_score: 0.00          ← 0% risk
    • eligible_amount: 5000.00
    • business_rules_applied: [...]

  Output:
    {
      "success": true,
      "data": {
        "claim_id": "CLM-2024-001",
        "enrichments": {
          "policy_verified": true,
          "network_status": "IN-NETWORK",
          "fraud_risk_score": 0.00,
          "eligible_amount": 5000.00
        },
        "issues": [],
        "status": "silver_enriched"
      }
    }


STAGE 3: GOLD AGENT (Decision)
─────────────────────────────────────────────────────────
  Input: Silver output (enriched data)

  Calculations:
    • Service category: "office_visit"
    • Coverage limit: $500.00
    • Claimed amount: $5000.00
    • Eligible amount: min(5000, 500) = $500.00

  Decision:
    IF eligible < claimed:
      decision = "APPROVE_PARTIAL"
    ELSE IF no_issues:
      decision = "APPROVE"

  Patient Responsibility:
    • Deductible: $0.00 (in-network)
    • Coinsurance: ($500 - $0) × 20% = $100.00
    • Patient total: $100.00

  Output:
    {
      "success": true,
      "data": {
        "claim_id": "CLM-2024-001",
        "decision": {
          "recommendation": "APPROVE_PARTIAL",
          "reason": "Amount exceeds coverage limit ($500)",
          "confidence_score": 0.80
        },
        "payment_details": {
          "approved_amount": 500.00,
          "insurance_pays": 400.00,
          "patient_pays": 100.00,
          "claim_reference": "REF-CLM-2024-001-20260623",
          "expected_payment_date": "2024-02-15"
        },
        "audit_trail": [
          {"action": "CLAIM_RECEIVED", "timestamp": "..."},
          {"action": "VALIDATIONS_COMPLETED", "timestamp": "..."},
          {"action": "ENRICHMENT_COMPLETED", "timestamp": "..."},
          {"action": "DECISION_MADE", "timestamp": "..."},
          {"action": "PAYMENT_APPROVED", "timestamp": "..."}
        ],
        "status": "gold_processed"
      }
    }


STAGE 4: SUPERVISION
─────────────────────────────────────────────────────────
  Batch Analysis:
    • Total claims: 4
    • Successful: 3
    • Failed: 1
    • Success rate: 75%

  Escalations Identified:
    • CLM-2024-003: FAIL (Bronze validation)
    • Reason: Missing service code
    • Level: HIGH

  Recommendations:
    • Review and improve data source quality
    • Consider increasing SLA threshold
    • Investigate validation rule sensitivity

  Health Status:
    • Overall: DEGRADED
    • Reason: Success rate 75% < 80% SLA
    • Action: Manual review recommended
```

---

## Agent Responsibilities Map

```
┌─────────────────────────────────────────────────────────┐
│           COMPLETE RESPONSIBILITY MATRIX                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ BRONZE: DATA QUALITY                                    │
│ ├─ Validate structure (JSON schema)                     │
│ ├─ Check required fields (8 total)                      │
│ ├─ Type conversion (string → number)                    │
│ ├─ Format validation (dates, phone, etc)                │
│ ├─ Range checking (age 0-150)                           │
│ ├─ Duplicate detection                                  │
│ ├─ Clean formatting                                     │
│ └─ Quality scoring (80-100%)                            │
│                                                         │
│ SILVER: BUSINESS LOGIC                                  │
│ ├─ Verify policy exists                                 │
│ ├─ Check provider network status                        │
│ ├─ Validate service codes                               │
│ ├─ Verify age eligibility                               │
│ ├─ Detect fraud patterns (5 types)                      │
│ ├─ Calculate fraud risk (0-100%)                        │
│ ├─ Apply business rules                                 │
│ ├─ Calculate eligible amounts                           │
│ └─ Determine cost-sharing                               │
│                                                         │
│ GOLD: FINAL DECISIONS                                   │
│ ├─ Categorize service type                              │
│ ├─ Apply coverage limits                                │
│ ├─ Calculate patient responsibility                     │
│ ├─ Make decision (APPROVE/DENY/PARTIAL/REVIEW)         │
│ ├─ Generate payment instructions                        │
│ ├─ Create payment reference                             │
│ ├─ Build audit trail                                    │
│ └─ Format for downstream systems                        │
│                                                         │
│ ORCHESTRATOR: COORDINATION                              │
│ ├─ Route claims through pipeline                        │
│ ├─ Handle stage failures                                │
│ ├─ Process batches                                      │
│ ├─ Collect metrics                                      │
│ ├─ Track performance                                    │
│ └─ Propagate errors                                     │
│                                                         │
│ SUPERVISOR: OVERSIGHT                                   │
│ ├─ Monitor SLA compliance                               │
│ ├─ Identify escalations                                 │
│ ├─ Detect conflicts                                     │
│ ├─ Analyze performance                                  │
│ ├─ Generate health reports                              │
│ ├─ Recommend interventions                              │
│ └─ Track trends over time                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Decision Tree (Gold Agent)

```
                          ┌─────────────────┐
                          │ CLAIM RECEIVED  │
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌──────────────────────┐      ┌──────────────────────┐
        │ FRAUD RISK > 70% ?   │      │ POLICY VERIFIED ?    │
        └──────────┬───────────┘      └──────────┬───────────┘
                   │                             │
            ╱──────┴──────╲                ╱─────┴─────╲
          YES              NO            YES            NO
           │                │             │               │
           ▼                │             ▼               │
        ┌──────────┐        │          ┌──────────┐       │
        │  DENY    │        │          │    ✓     │       │
        └──────────┘        │          └────┬─────┘       │
                            │                │             │
                            ▼                │             ▼
                 ┌──────────────────────┐    │          ┌──────────┐
                 │ SERVICE CODE VALID?  │    │          │  DENY    │
                 └──────────┬───────────┘    │          └──────────┘
                            │                │
                     ╱──────┴──────╲         │
                   YES              NO       │
                    │                │       │
                    ▼                ▼       │
                  ✓                ┌──────────────┐
                                   │  DENY        │
                                   └──────────────┘
                                         │
                                         │
        ┌────────────────────────────────┘
        │
        ▼
    ┌──────────────────────┐
    │ CLAIMED > LIMIT ?    │
    └──────────┬───────────┘
               │
        ╱──────┴──────╲
      YES              NO
       │                │
       ▼                │
    ┌──────────────┐    │
    │APPROVE       │    │
    │PARTIAL       │    │
    │($limit)      │    │
    └──────────────┘    │
                        │
                        ▼
                   ┌─────────────────────┐
                   │ ISSUES > 2 ?        │
                   └────────┬────────────┘
                            │
                     ╱──────┴──────╲
                   YES              NO
                    │                │
                    ▼                ▼
                ┌──────────┐      ┌──────────┐
                │APPROVE   │      │APPROVE   │
                │WITH      │      │(FULL)    │
                │REVIEW    │      └──────────┘
                └──────────┘

LEGEND:
═══════
✓ = Continue to next check
APPROVE = Full approval
APPROVE_PARTIAL = Partial due to limit
APPROVE_WITH_REVIEW = Approved but flag for review
DENY = Reject claim
```

---

## System State Machine

```
                    ┌─────────────────────┐
                    │   INITIAL STATE     │
                    │  Ready to Process   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼───────────┐
                    │  BATCH RECEIVED      │
                    │  4 Claims Loaded     │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ╔════════════════╗  ╔════════════════╗  ╔════════════════╗
    ║ BRONZE ACTIVE  ║  ║ BRONZE ACTIVE  ║  ║ BRONZE ACTIVE  ║
    ╚────────┬───────╝  ╚────────┬───────╝  ╚────────┬───────╝
             │                    │                    │
       [VALID]            [VALID]            [INVALID]
             │                    │                    │
    ┌────────▼────┐     ┌────────▼────┐     ┌────────▼────┐
    │SILVER ACTIVE│     │SILVER ACTIVE│     │ESCALATED    │
    └────────┬────┘     └────────┬────┘     │TO SUPERVISOR│
             │                    │         └─────────────┘
       [OK]      │         [OK]        │
             │        │             │
    ┌────────▼────┐     ┌────────▼────┐
    │GOLD ACTIVE  │     │GOLD ACTIVE  │
    └────────┬────┘     └────────┬────┘
             │                    │
    ┌────────▼────────┐  ┌───────▼─────────┐
    │APPROVED_PARTIAL │  │APPROVED         │
    │($500 limit)     │  │($25,000)        │
    └────────┬────────┘  └───────┬─────────┘
             │                    │
             └────────┬───────────┘
                      │
        ┌─────────────▼──────────────┐
        │  ORCHESTRATOR AGGREGATING  │
        │  3 Success / 1 Failure     │
        │  75% Success Rate          │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │   SUPERVISOR ANALYZING     │
        │   Status: DEGRADED         │
        │   Action: Review Needed    │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  FINAL STATE               │
        │  Results Persisted         │
        │  Health Report Generated   │
        │  Recommendations Ready     │
        └────────────────────────────┘
```

---

This architecture enables:
- ✓ Scalable parallel processing
- ✓ Fault isolation and recovery
- ✓ Clear separation of concerns
- ✓ Comprehensive monitoring
- ✓ Easy customization
- ✓ Production deployment

