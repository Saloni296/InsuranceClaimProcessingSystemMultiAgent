import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.bronze_agent import BronzeAgent
from agents.silver_agent import SilverAgent
from agents.gold_agent import GoldAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.supervisor_agent import SupervisorAgent


REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
REPORTS_DIR = REPO_ROOT / "reports"
PROCESSING_RESULTS_PATH = DATA_DIR / "processing_results.json"


def load_claims():
    genai = DATA_DIR / "sample_claims_genai.json"
    legacy = DATA_DIR / "sample_claims.json"

    if genai.exists():
        with open(genai, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

    if legacy.exists():
        with open(legacy, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            return data.get('claims', [])

    return []


def save_processing_results(results):
    PROCESSING_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save canonical latest processing result
    with open(PROCESSING_RESULTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    # Save a timestamped report file in reports/
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    report_path = REPORTS_DIR / f"report-{timestamp}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    return report_path


def load_latest_results():
    if REPORTS_DIR.exists():
        report_files = sorted(REPORTS_DIR.glob('report-*.json'))
        if report_files:
            latest_report = report_files[-1]
            with open(latest_report, 'r', encoding='utf-8') as f:
                return json.load(f)

    if PROCESSING_RESULTS_PATH.exists():
        with open(PROCESSING_RESULTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def display_claim_details(claim):
    st.subheader("Claim Metadata")
    st.markdown(
        f"**Claim ID:** {claim.get('claim_id')}  \\"
        f"**Policy ID:** {claim.get('policy_id')}  \\"
        f"**Provider:** {claim.get('provider', {}).get('name')}  \\"
        f"**Claim Amount:** ${claim.get('claim_amount')}  \\"
        f"**Service:** {claim.get('service_description')}  \\"
        f"**Uploaded files:** {claim.get('uploaded_files', [])}"
    )


def display_batch_summary(batch_result):
    summary = batch_result.get('batch_summary', {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Claims", batch_result.get('total_claims', 0))
    col2.metric("Successful", summary.get('successful_pipeline', 0))
    col3.metric("Success Rate", f"{summary.get('pipeline_success_rate', 0):.2%}")

    st.markdown("**Approvals**")
    st.write(summary.get('approvals', {}))
    st.markdown("**Financial Summary**")
    st.write(summary.get('financial_summary', {}))


def display_supervisor_insights(report):
    analysis = report.get('oversight_analysis', {})
    escalations = report.get('escalations', [])
    conflicts = report.get('conflicts', [])
    interventions = report.get('interventions', [])

    st.subheader("Supervisor Insights")
    st.write("**Performance Metrics**")
    st.json(analysis.get('performance_metrics', {}))
    st.write("**SLA Compliance**")
    st.json(analysis.get('sla_compliance', {}))
    st.write("**Quality Assessment**")
    st.json(analysis.get('quality_assessment', {}))

    st.subheader("Escalations")
    if escalations:
        st.json(escalations)
    else:
        st.info("No escalations detected.")

    st.subheader("Conflicts")
    if conflicts:
        st.json(conflicts)
    else:
        st.info("No conflicts detected.")

    st.subheader("Recommended Interventions")
    if interventions:
        st.json(interventions)
    else:
        st.info("No interventions recommended.")


st.set_page_config(page_title="Insurance Claim GenAI Demo", layout="wide")
st.title("Insurance Claim Processing — GenAI Pipeline Demo")

claims = load_claims()
if not claims:
    st.error("No sample claims found in data/. Place sample_claims_genai.json or sample_claims.json in the data folder.")
    st.stop()

agent_setup = st.sidebar.expander("Agent configuration")
with agent_setup:
    st.write("This app uses the local Bronze/Silver/Gold orchestrator pipeline.")

claim_ids = [c.get('claim_id', f"claim_{i}") for i, c in enumerate(claims)]
selected = st.sidebar.selectbox("Select claim to inspect", claim_ids)
run_mode = st.sidebar.radio("Mode", ["Single claim", "Full batch", "Latest saved report"])

if st.sidebar.button("Execute"):
    bronze = BronzeAgent()
    silver = SilverAgent()
    gold = GoldAgent()
    orchestrator = OrchestratorAgent(bronze, silver, gold)
    supervisor = SupervisorAgent(orchestrator)

    if run_mode == "Single claim":
        idx = claim_ids.index(selected)
        claim = claims[idx]
        result = orchestrator.orchestrate_claim(claim)
        st.success("Single claim pipeline completed")
        st.subheader("Claim Processing Result")
        st.json(result)
        report_path = save_processing_results({
            'execution_timestamp': datetime.now().isoformat(),
            'mode': 'single_claim',
            'batch_results': {
                'batch_id': f"APP-BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'total_claims': 1,
                'claim_results': [result],
                'batch_summary': {}
            }
        })
        st.success(f"Saved report to {report_path}")

    elif run_mode == "Full batch":
        report = supervisor.supervise_batch(claims)
        st.success("Batch processing completed")
        st.subheader("Batch Report")
        display_batch_summary(report.get('batch_results', {}))
        display_supervisor_insights(report)
        report_path = save_processing_results(report)
        st.success(f"Saved report to {report_path}")

    elif run_mode == "Latest saved report":
        report = load_latest_results()
        if report:
            st.success("Loaded latest saved report")
            st.json(report)
        else:
            st.warning("No saved report found yet.")

st.sidebar.markdown("---")
st.sidebar.write("Claims in dataset:")
for c in claims:
    st.sidebar.write(f"- {c.get('claim_id')}")

idx = claim_ids.index(selected)
selected_claim = claims[idx]

col1, col2 = st.columns([2, 3])
with col1:
    display_claim_details(selected_claim)

with col2:
    st.subheader("Claim Details")
    ocr = selected_claim.get('ocr_texts', {})
    if ocr:
        st.json(ocr)
    else:
        st.info("OCR not yet run for this claim. Execute the pipeline to generate OCR and processing output.")

st.markdown("---")
st.subheader("Latest saved processing result")
latest = load_latest_results()
if latest:
    st.json(latest)
else:
    st.info("No saved processing result available. Run a single claim or full batch to generate the report.")
