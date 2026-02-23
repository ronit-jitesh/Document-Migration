"""
Siemens AI Document Migration — Streamlit Application
======================================================
Upload old, messy SOP documents and get clean, standardized Word docs.
"""

import os
import json
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from schema import SiemensSOP
from migrator import read_file, extract_sop, generate_word_doc

load_dotenv()

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Siemens Document Migration",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for Premium Look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #003366 0%, #006666 50%, #009999 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 51, 102, 0.3);
    }
    .header-banner h1 {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-banner p {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #009999;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }
    .metric-card h3 {
        color: #003366;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card p {
        color: #333;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0;
    }

    /* Confidence gauge */
    .confidence-high { color: #28a745; font-weight: 700; }
    .confidence-mid  { color: #ffc107; font-weight: 700; }
    .confidence-low  { color: #dc3545; font-weight: 700; }

    /* Section headers */
    .section-label {
        color: #003366;
        font-size: 1rem;
        font-weight: 600;
        border-bottom: 2px solid #009999;
        padding-bottom: 0.4rem;
        margin-bottom: 0.75rem;
    }

    /* Safety warning badge */
    .safety-badge {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }

    /* Step card */
    .step-card {
        background: #f8f9fa;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        margin: 0.3rem 0;
        border-left: 3px solid #009999;
    }

    /* Sidebar branding */
    .sidebar-brand {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1rem;
    }
    .sidebar-brand h2 {
        color: #009999;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0;
    }
    .sidebar-brand p {
        color: #888;
        font-size: 0.8rem;
        margin: 0.2rem 0 0 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <h2>🏭 Siemens AI</h2>
            <p>Document Migration System</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload an old SOP document",
        type=["txt", "pdf"],
        help="Supported formats: .txt, .pdf",
    )

    st.markdown("---")
    st.markdown("### 📂 Or Try a Sample")
    sample_dir = Path(__file__).parent / "input_docs"
    sample_files = sorted(sample_dir.glob("*.txt")) if sample_dir.exists() else []

    selected_sample = st.selectbox(
        "Select a sample SOP",
        options=["— Select —"] + [f.name for f in sample_files],
        index=0,
    )

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    model_choice = st.selectbox(
        "LLM Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        help="gpt-4o-mini is fast & cost-effective. gpt-4o is most accurate.",
    )

    api_key_input = st.text_input(
        "OpenAI API Key (optional override)",
        type="password",
        help="Leave blank to use .env file",
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.markdown("---")
    st.markdown(
        "<p style='color:#888; font-size:0.75rem; text-align:center;'>"
        "Siemens Document Migration POC<br>v1.0 • Built with LangChain + Streamlit"
        "</p>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main Content
# ---------------------------------------------------------------------------

# Header banner
st.markdown(
    """
    <div class="header-banner">
        <h1>📄 AI Document Migration</h1>
        <p>Transform unstructured manufacturing SOPs into standardized, version-controlled documents</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Determine input text
# ---------------------------------------------------------------------------
raw_text = None

if uploaded_file is not None:
    # Save uploaded file to a temp location and read it
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    raw_text = read_file(tmp_path)
    os.unlink(tmp_path)

elif selected_sample and selected_sample != "— Select —":
    sample_path = sample_dir / selected_sample
    raw_text = read_file(str(sample_path))


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
if raw_text is None:
    # Landing / empty state
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <h3>📥 Step 1</h3>
                <p>Upload an old SOP document or select a sample from the sidebar</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <h3>🤖 Step 2</h3>
                <p>AI extracts & structures the content into a standardized format</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="metric-card">
                <h3>📄 Step 3</h3>
                <p>Download a clean, professional Word document ready for review</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.info("👈 **Get started** by uploading a document or selecting a sample from the sidebar.")

else:
    # --- Two-column migration view ---
    st.markdown("---")

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown('<div class="section-label">📜 Original Document (Raw Text)</div>', unsafe_allow_html=True)
        st.text_area(
            "Raw content",
            value=raw_text,
            height=500,
            disabled=True,
            label_visibility="collapsed",
        )
        st.caption(f"📏 {len(raw_text):,} characters • {len(raw_text.splitlines()):,} lines")

    # --- Extract button ---
    with right_col:
        st.markdown('<div class="section-label">🤖 Extracted Structured Data</div>', unsafe_allow_html=True)

        if "sop_data" not in st.session_state:
            st.session_state.sop_data = None

        if st.button("🚀 Extract & Migrate", type="primary", use_container_width=True):
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key or api_key == "your-api-key-here":
                st.error("⚠️ Please provide an OpenAI API key in the sidebar or `.env` file.")
            else:
                with st.spinner("🔄 AI is analyzing the document..."):
                    try:
                        sop = extract_sop(raw_text, model=model_choice)
                        st.session_state.sop_data = sop
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {e}")

        sop = st.session_state.sop_data

        if sop is not None:
            # --- Confidence Score ---
            score = sop.confidence_score
            if score >= 8:
                css_class = "confidence-high"
                emoji = "🟢"
            elif score >= 5:
                css_class = "confidence-mid"
                emoji = "🟡"
            else:
                css_class = "confidence-low"
                emoji = "🔴"

            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>Confidence Score</h3>
                    <p>{emoji} <span class="{css_class}">{score}/10</span></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # --- Metadata ---
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.markdown(
                    f'<div class="metric-card"><h3>Document ID</h3><p>{sop.document_id}</p></div>',
                    unsafe_allow_html=True,
                )
            with meta_col2:
                st.markdown(
                    f'<div class="metric-card"><h3>Version</h3><p>{sop.version}</p></div>',
                    unsafe_allow_html=True,
                )

            st.markdown(f"**📌 Title:** {sop.title}")
            st.markdown(f"**🏢 Department:** {sop.department}")

            # --- Safety Warnings ---
            with st.expander(f"⚠️ Safety Warnings ({len(sop.safety_warnings)})", expanded=True):
                for w in sop.safety_warnings:
                    st.markdown(f'<div class="safety-badge">⚠️ {w}</div>', unsafe_allow_html=True)

            # --- Equipment ---
            with st.expander(f"🔧 Equipment ({len(sop.equipment)})"):
                for item in sop.equipment:
                    st.markdown(f"- {item}")

            # --- Steps ---
            with st.expander(f"📋 Procedure Steps ({len(sop.steps)})"):
                for i, step in enumerate(sop.steps, 1):
                    st.markdown(f'<div class="step-card"><b>Step {i}:</b> {step}</div>', unsafe_allow_html=True)

            # --- Full JSON ---
            with st.expander("🔍 Full Extracted JSON"):
                st.json(sop.model_dump())

            # --- Generate Word Document ---
            st.markdown("---")
            if st.button("📝 Generate New SOP Document", type="primary", use_container_width=True):
                with st.spinner("📄 Generating Word document..."):
                    try:
                        output_path = generate_word_doc(sop)
                        st.session_state.output_path = output_path
                        st.success(f"✅ Document generated successfully!")
                    except Exception as e:
                        st.error(f"❌ Generation failed: {e}")

            if "output_path" in st.session_state and st.session_state.output_path:
                output_path = st.session_state.output_path
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Standardized SOP (.docx)",
                        data=f.read(),
                        file_name=Path(output_path).name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
