# Insurance Claim Processing Multi-Agent Architecture

## Use Case: Health Insurance Claim Processing Pipeline

### Business Objective
Process health insurance claims through quality tiers (Bronze → Silver → Gold) with increasing levels of validation, enrichment, and business logic application. Each tier performs specific transformations and validations.

### Data Flow (GenAI-enhanced)
```
Customer submits claim package (JSON) + uploads (photos, invoices, claim form)
    ↓
[Orchestrator Agent] - Ingests package and triggers pre-processing
    ↓
[OCR Agent] - Extracts text from uploaded images & PDFs; attaches ocr_texts to claim
    ↓
[Bronze Agent] - Validation & LLM Summarization
    ├─ Schema validation
    ├─ Required fields check
    ├─ Attach OCR outputs
    ├─ Call LLM to summarize incident from OCR texts
    └─ Produce incident_summary and data quality score
    ↓
[Silver Agent] - LLM Policy Check & Enrichment
    ├─ Fetch policy text for policy_id
    ├─ Call LLM to compare incident_summary vs policy text (coverage assessment)
    ├─ Provider network checks and fraud detection
    └─ Calculate eligible reimbursement amounts
    ↓
[Gold Agent] - LLM Completeness & Decisioning
    ├─ Use LLM to identify missing documents and generate follow-up questions
    ├─ Apply coverage limits and compute patient responsibility
    ├─ Generate final recommendation (APPROVE/DENY/PARTIAL/REVIEW)
    └─ Produce auditable rationale including LLM outputs
    ↓
[Supervisor Agent] - Oversight
    ├─ Monitor LLM/OCR confidence and pipeline health
    ├─ Identify escalations and recommend manual review
    └─ Generate supervision and health reports
```

### Key Features
- **Tiered Processing**: Each tier has specific responsibilities
- **Error Handling**: Failed claims are escalated with context
- **Audit Trail**: All transformations are logged
- **Quality Gates**: Each tier validates output before passing to next
- **Supervisor Oversight**: Central coordination and conflict resolution

### Metrics
- Throughput: Claims processed per minute
- Quality Score: % of claims passing all validations
- Processing Time: Total time from ingestion to gold
- Escalation Rate: % of claims requiring manual review
