# LLM Agent placeholders: summarization, policy check, completeness & follow-up generation
from typing import Dict, Any, List


def summarize_incident(ocr_texts: Dict[str, str]) -> str:
    """Create an incident summary from OCR-extracted texts.
    Replace this placeholder with a call to your preferred LLM (OpenAI, etc.).
    """
    # Combine OCR texts into a single prompt
    combined = "\n".join([f"FILE: {k}\n{v}" for k, v in ocr_texts.items()])
    # Placeholder summary
    summary = f"[LLM SUMMARY based on OCR content: {', '.join(list(ocr_texts.keys()))}]"
    return summary


def check_policy_coverage(claim_summary: str, policy_text: str) -> Dict[str, Any]:
    """Compare claim summary with policy text and return coverage assessment.
    Replace with LLM call to reason over documents.
    """
    # Simple placeholder logic
    coverage_match = True
    details = "[LLM policy coverage check placeholder]"
    missing_clauses: List[str] = []
    if 'excluded' in policy_text.lower():
        coverage_match = False
        missing_clauses.append('Exclusion found')

    return {
        'coverage_match': coverage_match,
        'details': details,
        'missing_clauses': missing_clauses
    }


def check_completeness_and_generate_questions(claim_data: Dict[str, Any], ocr_texts: Dict[str, str]) -> Dict[str, Any]:
    """Identify missing documents and generate follow-up questions using LLM.
    Replace with a real LLM call that inspects claim and OCR outputs.
    """
    # Placeholder heuristics
    required_docs = {'claim_form', 'invoice', 'photo'}
    present = set()
    for k in ocr_texts.keys():
        k_lower = k.lower()
        if 'form' in k_lower:
            present.add('claim_form')
        if 'invoice' in k_lower:
            present.add('invoice')
        if 'photo' in k_lower or 'image' in k_lower:
            present.add('photo')

    missing = list(required_docs - present)
    follow_ups = []
    for m in missing:
        if m == 'invoice':
            follow_ups.append('Please upload the invoice showing the billed amount and provider details.')
        elif m == 'claim_form':
            follow_ups.append('Please upload the signed claim form.')
        elif m == 'photo':
            follow_ups.append('Please upload photos of the incident or damages.')

    return {
        'missing_documents': missing,
        'follow_up_questions': follow_ups
    }
