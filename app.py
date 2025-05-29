import streamlit as st
from google.cloud import firestore
from vertexai.generative_models import GenerativeModel
import vertexai
import os
import base64
import re
import io
from datetime import datetime
import markdown2
from xhtml2pdf import pisa

# Initialize Vertex AI and Firestore
PROJECT_ID = "security-threat-analyzer"
REGION = "us-central1"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
vertexai.init(project=PROJECT_ID, location=REGION)

# Firestore setup
db = firestore.Client()

# Gemini model
model = GenerativeModel("gemini-2.0-flash-001")

def analyze_with_gemini(file_type: str, content: str) -> str:
    prompt = f"""
    You are a security assistant. Analyze the following {file_type} content. Identify any security issues, misconfigurations, or vulnerabilities.
    Provide clear and actionable remediation steps if needed.

    Content:
    {content}
    """
    response = model.generate_content(prompt)
    return response.text

def get_threat_score(analysis: str) -> str:
    if "critical" in analysis.lower():
        return "🔴 Critical"
    elif "high" in analysis.lower():
        return "🟠 High"
    elif "medium" in analysis.lower():
        return "🟡 Medium"
    else:
        return "🟢 Low"

def save_to_firestore(file_name: str, file_type: str, content: str, analysis: str, score: str):
    db.collection("threat_reports").add({
        "file_name": file_name,
        "file_type": file_type,
        "content": content,
        "analysis": analysis,
        "score": score,
        "timestamp": firestore.SERVER_TIMESTAMP,
    })

def detect_file_type(name: str) -> str:
    name = name.lower()
    if "dockerfile" in name:
        return "Dockerfile"
    elif name.endswith(".log"):
        return "Log File"
    elif name.endswith(".json"):
        return "Scan Report"
    else:
        return "Unknown"

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F700-\U0001F77F"
        u"\U0001F780-\U0001F7FF"
        u"\U0001F800-\U0001F8FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def markdown_to_pdf_bytes(md_text: str, file_name: str, file_type: str, score: str) -> bytes:
    """
    Converts markdown text to a PDF bytes object with header and timestamp added.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add header and timestamp to markdown
    header_md = f"""# Security Threat Report

**Report generated on:** {now}  
**File:** {file_name}  
**Type:** {file_type}  
**Threat Score:** {remove_emojis(score)}

---

"""

    full_md = header_md + md_text

    # Convert markdown to HTML
    html = markdown2.markdown(full_md)

    # Convert HTML to PDF bytes using xhtml2pdf
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf_buffer)

    if pisa_status.err:
        raise Exception("Failed to create PDF from markdown")

    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    return pdf_bytes

# Streamlit UI
st.set_page_config(page_title="Security Threat Analyzer", layout="wide")
st.title("🔍 Security Threat Analyzer")
st.write("Upload a Dockerfile, system log, or vulnerability scan report to analyze potential security issues.")

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

uploaded_file = st.file_uploader("Upload file", type=["txt", "log", "json", "Dockerfile"])

if uploaded_file is not None:
    # Detect if a new file is uploaded (filename changed)
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.analysis_result = None
        st.session_state.last_uploaded_file = uploaded_file.name

    file_content = uploaded_file.read().decode("utf-8")
    file_type = detect_file_type(uploaded_file.name)

    if st.session_state.analysis_result is None:
        with st.spinner("Analyzing file with Gemini..."):
            analysis = analyze_with_gemini(file_type, file_content)
            threat_score = get_threat_score(analysis)
            save_to_firestore(uploaded_file.name, file_type, file_content, analysis, threat_score)

            pdf_bytes = markdown_to_pdf_bytes(analysis, uploaded_file.name, file_type, threat_score)

            st.session_state.analysis_result = {
                "analysis": analysis,
                "score": threat_score,
                "pdf_bytes": pdf_bytes
            }

    result = st.session_state.analysis_result

    st.subheader("Threat Report")
    st.markdown(f"**File:** {uploaded_file.name}")
    st.markdown(f"**Type:** {file_type}")
    st.markdown(f"**Threat Score:** {result['score']}")

    st.markdown(result["analysis"], unsafe_allow_html=False)

    st.download_button(
        label="📄 Download PDF Report",
        data=result["pdf_bytes"],
        file_name="threat_report.pdf",
        mime="application/pdf",
        use_container_width=True)

    st.success("✅ Analysis complete and saved to Firestore.")
else:
    st.info("Please upload a file to begin analysis.")