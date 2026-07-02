import streamlit as st
import json
from pathlib import Path
from datetime import datetime

from agents.bronze_agent import BronzeAgent
from agents.silver_agent import SilverAgent
from agents.gold_agent import GoldAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.supervisor_agent import SupervisorAgent


def load_claims():
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data"
    genai = data_dir / "sample_claims_genai.json"
    legacy = data_dir / "sample_claims.json"
    if genai.exists():
        with open(genai, 'r', encoding='utf-8-sig') as f:
            claims = json.load(f)
    elif legacy.exists():
        with open(legacy, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            claims = data.get('claims', [])
    else:
        claims = []
    return claims


def save_processing_results(results):
    out = Path(__file__).parent.parent / "data" / "processing_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)


st.set_page_config(page_title="Insurance Claim GenAI Demo", layout="wide")
st.title("Insurance Claim Processing — GenAI Pipeline Demo")

claims = load_claims()
if not claims:
    st.error("No sample claims found (place sample_claims_genai.json or sample_claims.json in repo root).")
    st.stop()

# Sidebar controls
st.sidebar.header("Controls")
claim_ids = [c.get('claim_id', f"claim_{i}") for i, c in enumerate(claims)]
selected = st.sidebar.selectbox("Select claim to inspect", claim_ids)

st.sidebar.markdown("---")
if st.sidebar.button("Run pipeline for selected claim"):
    idx = claim_ids.index(selected)
    bronze = BronzeAgent()
    silver = SilverAgent()
    gold = GoldAgent()
    orchestrator = OrchestratorAgent(bronze, silver, gold)
    claim = claims[idx]
    result = orchestrator.orchestrate_claim(claim)
    st.success("Pipeline completed — result shown below")
    st.json(result)
    # Save as processing_results.json with single claim batch
    results = {
        'execution_timestamp': datetime.now().isoformat(),
        'batch_results': {
            'batch_id': f"APP-BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'total_claims': 1,
            'claim_results': [result],
            'batch_summary': {}
        }
    }
    save_processing_results(results)

if st.sidebar.button("Run full batch"):
    bronze = BronzeAgent()
    silver = SilverAgent()
    gold = GoldAgent()
    orchestrator = OrchestratorAgent(bronze, silver, gold)
    supervisor = SupervisorAgent(orchestrator)
    report = supervisor.supervise_batch(claims)
    st.success("Batch processing complete — report below")
    st.json(report)
    save_processing_results(report)

st.sidebar.markdown("---")
st.sidebar.write("Claims in dataset:")
for c in claims:
    st.sidebar.write(f"- {c.get('claim_id')}")

# Main panel — show selected claim details
idx = claim_ids.index(selected)
claim = claims[idx]

col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("Claim Metadata")
    st.write(f"Claim ID: **{claim.get('claim_id')}**")
    st.write(f"Policy ID: {claim.get('policy_id')}")
    st.write(f"Provider: {claim.get('provider', {}).get('name')}")
    st.write(f"Claim Amount: ${claim.get('claim_amount')}")
    st.write(f"Service: {claim.get('service_description')}")
    st.write(f"Uploaded files: {claim.get('uploaded_files', [])}")

with col2:
    st.subheader("OCR Texts (if present)")
    # Orchestrator may add ocr_texts; we don't run pipeline by default
    ocr = claim.get('ocr_texts', {})
    if ocr:
        st.json(ocr)
    else:
        st.info("OCR not yet run for this claim (use Run pipeline buttons)")

st.markdown("---")

st.subheader("Notes")
st.write("This demo uses placeholder OCR and LLM agents by default. To integrate real providers, update ocr_agent.py and llm_agent.py and provide API keys as environment variables or GitHub Secrets.")

st.markdown("---")
st.write("Processing results (latest):")
try:
    with open(Path(__file__).parent / 'processing_results.json', 'r', encoding='utf-8') as f:
        pr = json.load(f)
        st.json(pr)
except Exception:
    st.info("No processing_results.json produced yet.")
