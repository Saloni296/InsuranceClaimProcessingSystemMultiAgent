# System Architecture Visualization (GenAI-enhanced)

## High-Level Flow Diagram

```
╔════════════════════════════════════════════════════════════════════════════╗
║                    INSURANCE CLAIM PROCESSING SYSTEM (GenAI)               ║
║                OCR → LLM → Bronze → Silver → Gold → Supervisor            ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│                         INPUT SOURCES                                     │
├──────────────────────────────────────────────────────────────────────────┤
│  • Web Forms (file uploads)  • Mobile App  • API Requests  • Email Attach  │
│  • Photos / Images (damage)  • PDFs (invoices, forms)  • EDI / CSV         │
└────────────────┬─────────────────────────────────────────────────┬───────┘
                  │                                                 │
                  └─────────────────────┬───────────────────────────┘
                                        │
                                        ▼
                     ╔══════════════════════════════════╗
                     ║   MAIN.PY - Orchestration      ║
                     ║  Ingests claim packages         ║
                     ╚═════────────────┬───────────────╝
                                       │
            ┌─────────────┬──────────────┼──────────────┬──────────────┐
            │             │              │              │              │
            ▼             ▼              ▼              ▼              ▼
     ╔═════════╗   ╔════════════╗  ╔════════════╗  ╔════════════╗  ╔══════════╗
     ║ INGEST  ║──▶║ OCR AGENT  ║▶▶║ LLM AGENT  ║▶▶║ BRONZE     ║▶▶║ SILVER   ║
     ║ (Upload)║   ║ (Extract)  ║  ║ (Summarize)║  ║ (Validate & ║  ║ (Policy & ║
     ║ Files   ║   ╚════════════╝  ╚════════════╝  ║  Attach LLM) ║  ║ Enrich)   ║
     ╚═════════╝                                ╚════════════╗  ╚══════════╝
                                                          │         │
                                                          ▼         ▼
                                                       ╔════════════════╗
                                                       ║  GOLD AGENT     ║
                                                       ║ Completeness &  ║
                                                       ║ Follow-ups &    ║
                                                       ║ Final Decision  ║
                                                       ╚════════╝
                                                            │
                                                            ▼
                                                   ┌───────────────────┐
                                                   │ ORCHESTRATOR      │
                                                   │ Aggregates Stages │
                                                   │ & Produces Output │
                                                   └────────┬──────────┘
                                                            │
                                                            ▼
                                                   ╔══════════════════╗
                                                   ║ SUPERVISOR AGENT ║
                                                   ║ (Oversight & SLA)║
                                                   ╚══════════════════╝
``` 

Notes:
- OCR Agent extracts structured text (amounts, dates, provider names) and attaches ocr_texts to the claim.
- LLM Agent consumes OCR outputs and produces an incident_summary and structured outputs used by Silver and Gold.

---

## Agent Interaction Diagram (detailed)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ SUPERVISOR AGENT: Monitors LLM/OCR confidence, SLA, escalations & trends   │
└──────────────┬─────────────────────────────────────────────────────────────┘
                │
                ▼
     ┌──────────────────────────┐      ┌──────────────────────────┐
     │  ORCHESTRATOR AGENT      │◀────▶│  ERROR HANDLER / QUEUE   │
     │ - triggers OCR & LLM     │      │ - retry failed OCR/LLM   │
     │ - routes Bronze→Silver→  │      │ - queues manual reviews  │
     │   Gold                   │      └──────────────────────────┘
     └──────────┬───────────────┘
                │
     ┌──────────┴──────────┐
     │    Pre-Processing   │
     │  OCR Agent (extract)│
     │  LLM Agent (summarize)
     └──────────┬──────────┘
                │
     ┌──────────┴──────────┐
     │      BRONZE         │
     │  Validate + attach  │
     │  OCR & incident_summary
     └──────────┬──────────┘
                │
     ┌──────────┴──────────┐
     │      SILVER         │
     │  Policy check (LLM) │
     │  Enrichment & fraud │
     └──────────┬──────────┘
                │
     ┌──────────┴──────────┐
     │       GOLD          │
     │  Completeness (LLM) │
     │  Follow-ups & Final │
     │  Decisioning         │
     └──────────┬──────────┘
                │
                ▼
     ┌──────────────────────────┐
     │  Persistence & Outputs   │
     │  (processing_results.json│
     │   audit logs, metrics)   │
     └──────────────────────────┘
```

---

## Data Flow Through Pipeline (GenAI-focused)

```
INPUT: Claim package JSON + uploaded files
   - { claim_id, policy_id, policy_holder, uploaded_files: [photo.jpg, invoice.pdf, form.pdf], metadata }

STEP 0: ORCHESTRATOR accepts package and triggers pre-processing
STEP 1: OCR Agent
   - Extract text per file → ocr_texts: {file: text}
   - Normalize dates, amounts, provider names when possible
   - Attach confidence scores per extracted field

STEP 2: LLM Agent (Summarization)
   - Ingest OCR outputs and create incident_summary
   - Return structured fields (incident_summary, key_entities, confidence)

STEP 3: BRONZE Agent
   - Validate JSON schema & required fields
   - Attach OCR outputs and incident_summary
   - Compute data_quality_score
   - If data_quality_score < threshold → escalate

STEP 4: SILVER Agent
   - Fetch policy text from store for policy_id
   - Call LLM compare(summary, policy_text) → policy_check (coverage_match, missing_clauses)
   - Enrich with fraud detection heuristics
   - Compute eligible_amount and enrichments

STEP 5: GOLD Agent
   - Call LLM completeness check with OCR & policy_check → missing_documents, follow_up_questions
   - If missing_documents → decision may be APPROVE_WITH_REVIEW or request customer follow-up
   - Apply coverage limits, calculate patient responsibility
   - Produce decision & audit_trail (include LLM outputs for transparency)

OUTPUT: Final claim decision + missing_documents + follow_up_questions + audit trail + metrics
```

Operational considerations:
- Attach LLM and OCR confidence scores to every stage; Supervisor uses them to route for manual review.
- Keep raw OCR outputs stored (redact PII in logs) for auditing and retraining prompts.
- Use structured prompts and output schemas when calling LLM to ensure machine-actionable responses.

---

## Decision Tree (GenAI-augmented)

```
CLAIM RECEIVED
   ↓
OCR & LLM Summarization → incident_summary (confidence)
   ↓
BRONZE validation (schema + fields)
   ├─ FAIL → Escalate to manual review
   ↓ SUCCESS
SILVER: policy_check = LLM.compare(incident_summary, policy_text)
   ├─ coverage_match = False → flag policy mismatch (issue)
   ↓
GOLD: completeness = LLM.identify_missing_documents(ocr_texts)
   ├─ missing_documents not empty → Generate follow_up_questions
   ├─ If missing critical doc → DECISION = APPROVE_WITH_REVIEW or HOLD
   ↓
Apply coverage limits, fraud rules, compute financials
   ↓
Decision = APPROVE / DENY / APPROVE_PARTIAL / APPROVE_WITH_REVIEW

Notes:
- At each LLM call, record prompt, model, temperature, and confidence to the audit trail.
- When LLM confidence < threshold, escalate to Supervisor for manual review.
```

---

## System State Machine (GenAI-aware)

```
INITIAL → BATCH_RECEIVED → PREPROCESSING
   (OCR + LLM Summarization)
     ↓
BRONZE_ACTIVE → SILVER_ACTIVE → GOLD_ACTIVE
     ↓             ↓               ↓
   VALID         ENRICHED       DECIDED
     ↓             ↓               ↓
   IF ISSUES or LOW_CONFIDENCE → ESCALATE → Supervisor
     ↓
   FINAL_STATE: Persist results, generate health & supervision reports
```

---

## Observability & Metrics

- Stage-level metrics: counts, success/fail, latency
- LLM/OCR metrics: per-call latency, confidence distributions, error rates
- Business metrics: approval rates, average approved amount, escalation rate
- Auditability: store prompts/LLM outputs (redact PII) and link to decisions

---

## Security & Privacy Notes

- PII must be redacted or stored encrypted when persisting OCR/LLM outputs.
- Access to LLM logs should be restricted and audited.
- Ensure HIPAA/region-specific compliance for all stored data.

---

## Next Steps / Integration Ideas

- Replace placeholder llm_agent.py and ocr_agent.py with provider integrations (OpenAI/Azure/Open-source LLMs, Google/Azure OCR)
- Implement structured output schemas for LLM responses (JSON schema enforcement)
- Add async processing and worker queues for OCR/LLM to improve throughput
- Add CI checks that validate LLM output schemas and example prompts

---

**Version**: 2.0-genai
**Last Updated**: 2026-07-02

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

