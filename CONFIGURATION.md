# Multi-Agent System Configuration

## System Configuration

### SLA Thresholds (Supervisor Agent)
```python
thresholds = {
    'min_quality_score': 0.75,           # Minimum data quality
    'max_fraud_risk': 0.70,              # Maximum acceptable fraud risk
    'max_failure_rate': 0.20,            # Maximum stage failure rate
    'min_pipeline_success_rate': 0.80    # Minimum pipeline success
}
```

### Bronze Agent Configuration

**Validation Rules**:
- Required Fields: claim_id, policy_id, policy_holder, claim_date, service_date, provider, claim_amount, service_code
- Claim Amount: Must be positive number
- Dates: Must be YYYY-MM-DD format
- Age: Must be 0-150
- Provider Name: Must be present

**Quality Score Calculation**:
- Base: 0.80 (pass validation)
- +0.10: Has attachments
- +0.05: Has diagnosis codes
- Max: 1.00

### Silver Agent Configuration

**Policy Database**:
```python
valid_policies = {'POL-12345', 'POL-54321', 'POL-99999', 'POL-55555'}
```

**Network Providers**:
```python
network_providers = {'PROV-789', 'PROV-102'}  # In-network
```

**Valid Service Codes**:
```python
valid_service_codes = {'99214', '71046', '27447', '99213', '99215'}
```

**Cost Sharing (In-Network)**:
- Coinsurance: 20%
- Copay: $30
- Deductible: No

**Cost Sharing (Out-of-Network)**:
- Coinsurance: 40%
- Copay: $50
- Deductible: Yes ($1,000)

**Fraud Risk Scoring**:
- High Claim (>$20k): +0.20
- Same-day claim: +0.10
- Missing diagnosis: +0.15
- Service > Claim date: +0.25
- Escalation threshold: >0.70

### Gold Agent Configuration

**Coverage Limits by Service Category**:
```python
coverage_limits = {
    'office_visit': 500.0,
    'emergency': 5000.0,
    'surgery': 50000.0,
    'imaging': 2000.0,
    'lab': 300.0,
    'default': 1000.0
}
```

**Annual Limits per Member**:
- Out-of-Pocket Maximum: $5,000
- Annual Deductible: $1,000

**Approval Rules**:
- Deny: High fraud risk OR Invalid policy OR Invalid service code
- Approve Partial: Amount exceeds coverage limit
- Approve with Review: Multiple issues found OR Critical concerns
- Approve: All validations passed

**Senior Coverage (Age 65+)**:
- +5% additional coverage for in-network claims

### Orchestrator Agent Configuration

**Pipeline Sequence**:
1. Bronze Agent: Validation
2. Silver Agent: Enrichment
3. Gold Agent: Decision Making

**Failure Handling**:
- Stage failure → Entire pipeline fails
- Failed claim → Marked as failed at stage
- Error message → Propagated to supervisor

### Supervisor Agent Configuration

**Escalation Levels**:
- HIGH: Pipeline failure, fraud detected, critical validation issue
- MEDIUM: Multiple issues, manual review recommended
- LOW: Minor concerns, standard processing

**Conflict Detection**:
- Agent Decision Mismatch: Silver positive but Gold denies
- Confidence-Decision Alignment: High confidence but recommends review
- Data Inconsistency: Contradictory enrichments

**Intervention Types**:
1. PROCESS_REVIEW: Review pipeline configuration
2. DATA_QUALITY_REVIEW: Enhance validation rules
3. ESCALATION_REVIEW: Adjust escalation thresholds
4. PERFORMANCE_OPTIMIZATION: Improve throughput

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Pipeline Success Rate | >80% | 75-95% |
| Data Quality Average | >75% | 80-95% |
| Average Processing Time | <50ms | 40-60ms |
| Throughput | 1000+/min | ~1200/min |
| Fraud Detection Rate | >90% | 85-95% |
| False Positive Rate | <5% | 2-8% |

## Monitoring Dashboards

### System Health Dashboard
- Overall success rate
- Stage-wise failure rates
- Average quality scores
- Escalation counts
- Processing times

### Batch Processing Dashboard
- Claims processed
- Approval/denial counts
- Average claim amount
- Financial summary
- SLA compliance status

### Escalation Dashboard
- High-risk claims
- Fraud detections
- Policy violations
- Manual review queue
- Escalation trends

## Alerting Thresholds

| Alert | Threshold | Action |
|-------|-----------|--------|
| Pipeline Success < 80% | Real-time | Page on-call |
| Fraud Risk > 70% | Per claim | Immediate escalation |
| Quality Score < 75% | Per batch | Review data source |
| Processing Time > 1s | Per claim | Log and investigate |
| Escalation Rate > 15% | Per batch | Review threshold settings |

## Integration Points

### Input
- Raw claim JSON from Source System
- Batch files from EDI providers
- API calls from Partner Systems

### Output
- Claim decisions (JSON)
- Payment files (EDIOUT)
- Audit reports (CSV/JSON)
- Health reports (Dashboard API)

## Database Configuration (if using persistence)

```sql
-- Claims processing history
CREATE TABLE claims_processed (
    claim_id VARCHAR(50) PRIMARY KEY,
    raw_data JSON,
    bronze_result JSON,
    silver_result JSON,
    gold_result JSON,
    supervision_report JSON,
    final_decision VARCHAR(50),
    processing_timestamp DATETIME
);

-- Escalations
CREATE TABLE escalations (
    escalation_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50),
    escalation_level VARCHAR(10),
    reasons JSON,
    assigned_to VARCHAR(100),
    created_at DATETIME
);

-- Conflicts
CREATE TABLE conflicts (
    conflict_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50),
    conflict_type VARCHAR(50),
    details JSON,
    requires_attention BOOLEAN,
    created_at DATETIME
);
```

## Deployment Configuration

### Single Machine Deployment
```
Bronze Agent + Silver Agent + Gold Agent
    ↓
Orchestrator Agent
    ↓
Supervisor Agent
```

### Distributed Deployment
```
Bronze Agents (Multiple instances)
    ↓
Silver Agents (Multiple instances)
    ↓
Gold Agents (Multiple instances)
    ↓
Orchestrator (Load Balanced)
    ↓
Supervisor (Centralized)
```

### Containerized Deployment
```dockerfile
FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

**Configuration Version**: 1.0  
**Last Updated**: 2024-06-23
