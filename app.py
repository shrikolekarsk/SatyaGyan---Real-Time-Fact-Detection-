import os
import sys
import tempfile
import streamlit as st
from dotenv import load_dotenv
import re
from pathlib import Path

# Try to import optional libraries
try:
    from docx import Document
except ImportError:
    Document = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# Load environment variables
load_dotenv()

# Add src to sys.path for importing crew
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

try:
    from fact_checker.crew import FactChecker
except ImportError as e:
    st.error(f"Could not import FactChecker: {e}")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="SatyaGyan - Professional Fact Check",
    layout="wide",
    page_icon="🔍",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Standard UI/UX ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800;900&display=swap');

    :root {
        --main-bg-color: rgba(0, 0, 0, 0.75);
        --primary-text-color: #E0E0E0;
        --secondary-text-color: #B0B0B0;
        --main-title-color: #00FFC2; /* Vibrant, high-contrast green */
        --section-header-color: #00B8D4; /* Professional turquoise */
        --feature-title-color: #FFD700; /* Gold for card titles */
        --button-primary-color: #00B8D4;
        --button-primary-hover-color: #00E5FF;
        --border-color: #383838;
        --highlight-color: #FFD700;
        --container-bg-color: rgba(0, 0, 0, 0.65);
    }

    html, body, [data-testid="stAppViewContainer"], .main {
        font-family: 'Nunito', sans-serif;
        color: var(--primary-text-color);
        background-color: transparent !important;
        background-image: url("https://thumbs.dreamstime.com/b/cartoon-robot-pointing-hand-humanoid-innovative-technology-340147653.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Hide the Streamlit header and footer */
    .stApp > header, .stApp > footer {
        display: none;
    }

    /* Main Header */
    .main-header {
        background: var(--main-bg-color);
        border-bottom: 2px solid var(--section-header-color);
        padding: 4rem 3rem;
        margin-bottom: 2.5rem;
        text-align: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.8);
        border-radius: 12px;
    }

    .main-title {
        color: var(--main-title-color) !important;
        font-size: 5rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        letter-spacing: 4px;
        text-shadow: 0 0 15px rgba(0,255,194,0.6);
    }

    .main-subtitle {
        color: var(--secondary-text-color) !important;
        font-size: 1.6rem;
        font-weight: 400;
        margin: 0;
    }

    /* Section Header */
    .section-header {
        font-size: 3rem;
        font-weight: 800;
        color: var(--section-header-color) !important;
        text-align: center;
        margin: 3.5rem 0 2rem 0;
        position: relative;
        text-shadow: 0 0 10px rgba(0,184,212,0.4);
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 6px;
        background: var(--section-header-color);
        border-radius: 3px;
        box-shadow: 0 0 10px rgba(0,184,212,0.6);
    }

    /* Card Styling */
    .feature-card {
        background: var(--main-bg-color);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.6);
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        border: 1px solid var(--border-color);
    }

    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(255, 215, 0, 0.5);
        border-color: var(--highlight-color);
        background: rgba(0, 0, 0, 0.85);
    }

    .feature-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--feature-title-color) !important;
        margin-bottom: 0.6rem;
        text-shadow: 0 0 5px rgba(255,215,0,0.5);
    }
    .feature-title i {
        color: var(--section-header-color);
        font-size: 2rem;
    }

    .feature-description {
        color: var(--secondary-text-color) !important;
        font-size: 1.1rem;
        line-height: 1.6;
    }

    /* Input section */
    # .input-section {
    #     background: var(--main-bg-color);
    #     padding: 3rem;
    #     border-radius: 15px;
    #     box-shadow: 0 6px 20px rgba(0,0,0,0.6);
    #     margin-bottom: 2.5rem;
    # }

    /* Radio button styling */
    .stRadio > div {
        flex-direction: row;
        gap: 1.5rem;
        justify-content: center;
    }

    .stRadio > div > label {
        background: var(--container-bg-color);
        padding: 1rem 1.8rem;
        border-radius: 10px;
        border: 2px solid var(--border-color);
        transition: all 0.3s ease-in-out;
        cursor: pointer;
        font-weight: 700;
        color: var(--primary-text-color);
        min-width: 180px;
        text-align: center;
    }

    .stRadio > div > label:hover {
        border-color: var(--button-primary-hover-color);
        background: rgba(0, 184, 212, 0.2);
    }

    .stRadio > div > label[data-baseweb="radio"] {
        background: var(--button-primary-color);
        color: #121212;
        border-color: var(--button-primary-color);
        transform: scale(1.05);
        box-shadow: 0 4px 20px rgba(0, 184, 212, 0.5);
    }

    .stRadio > div > label[data-baseweb="radio"] p {
        color: #121212 !important;
    }

    .stRadio label p {
        font-weight: 700 !important;
    }

    /* Button styling */
    .stButton > button {
        background: var(--button-primary-color) !important;
        color: #121212 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem 3.5rem !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 4px 20px rgba(0, 184, 212, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-7px) !important;
        box-shadow: 0 12px 30px rgba(0, 184, 212, 0.6) !important;
        background: var(--button-primary-hover-color) !important;
    }

    .stDownloadButton > button {
        background: #28a745 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stDownloadButton > button:hover {
        background: #218838 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 10px rgba(40, 167, 69, 0.3) !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stFileUploader > div > div {
        background-color: var(--container-bg-color) !important;
        color: var(--primary-text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-size: 1.1rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--secondary-text-color) !important;
    }

    .stFileUploader > div > div {
        border-style: dashed !important;
        padding: 2.5rem !important;
        background-color: var(--container-bg-color) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--button-primary-hover-color) !important;
        box-shadow: 0 0 0 4px rgba(0, 229, 255, 0.3) !important;
        outline: none !important;
    }

    /* Results section */
    .results-section {
        background: var(--main-bg-color);
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        margin-top: 2.5rem;
    }

    .results-section h3 {
        color: var(--feature-title-color) !important;
    }

    .verdict-container {
        text-align: center;
        padding: 1.8rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .verdict-true {
        background-color: #D4EDDA;
        color: #155724;
    }
    .verdict-false {
        background-color: #F8D7DA;
        color: #721c24;
    }
    .verdict-partial {
        background-color: #FFF3CD;
        color: #856404;
    }
    .verdict-inconclusive {
        background-color: #D1ECF1;
        color: #0C5460;
    }
    .verdict-container p {
        color: initial !important;
    }

    .stExpander > div > p {
        color: var(--primary-text-color) !important;
    }

    .stExpander div[role="button"] {
        background: var(--main-bg-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 10px;
        color: var(--feature-title-color) !important;
    }

    .stExpander div[role="button"] p {
        color: var(--feature-title-color) !important;
        font-size: 1.2rem;
        font-weight: 600;
    }

    .stMarkdown p {
        color: var(--primary-text-color) !important;
        font-size: 1.1rem;
    }
    .stMarkdown h3 {
        color: var(--feature-title-color) !important;
        text-shadow: 0 0 5px rgba(255,215,0,0.5);
    }
</style>
""", unsafe_allow_html=True)


def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)


# Main header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">SatyaGyan</h1>
    <p class="main-subtitle">Professional AI-Powered Fact Verification System</p>
</div>
""", unsafe_allow_html=True)

# Environment check
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ **Configuration Error:** Please set your OPENAI_API_KEY in the .env file")
    st.stop()

# Features overview
st.markdown('<h2 class="section-header">Platform Capabilities</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🗣️ Text Claims</div>
        <div class="feature-description">Advanced AI verification of factual statements with comprehensive source validation.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🌐 Web Content</div>
        <div class="feature-description">Real-time analysis of articles, news content, and online publications.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📺 Video Content</div>
        <div class="feature-description">Intelligent fact-checking of YouTube videos, transcripts, and multimedia content.</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📄 Documents</div>
        <div class="feature-description">Comprehensive processing and verification of PDF documents, Word files, and text files.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Input Section
with st.container():
    st.markdown('<h3 class="section-header">Select Verification Method</h3>', unsafe_allow_html=True)

    # Input mode selection
    mode = st.radio(
        "",
        ["📝 Text Claim", "🌐 Website URL", "📺 YouTube Video", "📄 Document Upload"],
        horizontal=True,
        key="input_mode"
    )

    user_input = ""
    claim, url, youtube_url, uploaded_file = "", "", "", None

    # Input forms based on selected mode
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    if mode == "📝 Text Claim":
        st.markdown("**Enter the factual claim you want to verify:**")
        claim = st.text_area(
            "",
            height=120,
            placeholder="Enter the statement or claim you want to fact-check...",
            key="claim_input"
        )
        user_input = claim

    elif mode == "🌐 Website URL":
        st.markdown("**Enter the website URL to analyze:**")
        url = st.text_input(
            "",
            placeholder="https://example.com/article",
            key="url_input"
        )
        user_input = url

    elif mode == "📺 YouTube Video":
        st.markdown("**Enter the YouTube video URL:**")
        youtube_url = st.text_input(
            "",
            placeholder="https://www.youtube.com/watch?v=...",
            key="youtube_input"
        )
        if youtube_url:
            if re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)', youtube_url):
                st.success("✅ Valid YouTube URL detected")
            else:
                st.warning("⚠️ Please enter a valid YouTube URL")
        user_input = youtube_url

    elif mode == "📄 Document Upload":
        st.markdown("**Upload a document for analysis:**")
        uploaded_file = st.file_uploader(
            "",
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, Word Document (.docx), Text File (.txt)"
        )
        if uploaded_file:
            st.success(f"✅ File uploaded: **{uploaded_file.name}** ({round(uploaded_file.size / 1024, 1)} KB)")

    st.markdown("</div>", unsafe_allow_html=True)

# Analysis button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button(
        "Launch Professional Analysis",
        use_container_width=True,
        key="analyze_btn"
    )

# Analysis execution
if analyze_button:
    # Input validation
    has_input = bool(claim or url or youtube_url or uploaded_file)
    if not has_input:
        st.error("⚠️ **Input Required:** Please provide content to analyze.")
        st.stop()

    # Processing indicator
    with st.spinner(
            "🔍 **SatyaGyan Analysis in Progress** - Our AI agents are researching, analyzing, and verifying your content..."):
        input_content = ""

        # File processing
        if uploaded_file:
            suffix = Path(uploaded_file.name).suffix.lower()
            try:
                if suffix == ".pdf" and PyPDF2:
                    reader = PyPDF2.PdfReader(uploaded_file)
                    input_content = "".join([page.extract_text() for page in reader.pages])
                elif suffix == ".docx" and Document:
                    doc = Document(uploaded_file)
                    input_content = "\n".join([p.text for p in doc.paragraphs])
                elif suffix == ".txt":
                    raw = uploaded_file.read()
                    for enc in ["utf-8", "utf-16", "latin-1", "cp1252"]:
                        try:
                            input_content = raw.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        st.error(
                            "❌ **File Processing Error:** Unable to decode text file. Please ensure UTF-8 encoding.")
                        st.stop()
                else:
                    st.error("❌ **Unsupported Format:** Please upload a PDF, Word document, or text file.")
                    st.stop()
            except Exception as e:
                st.error(f"❌ **File Processing Error:** {e}")
                st.stop()
        else:
            input_content = claim or url or youtube_url

        # Run analysis
        try:
            progress = st.progress(0, text="Initializing SatyaGyan system...")
            progress.progress(20, text="Loading AI agents...")
            checker = FactChecker()
            progress.progress(60, text="Executing multi-agent analysis...")
            result = checker.crew().kickoff(inputs={"input_content": input_content})
            progress.progress(100, text="Analysis complete!")
        except Exception as e:
            st.error(f"❌ **Analysis Error:** {e}")
            st.stop()

    # Success notification
    st.success("🎉 **Analysis Complete** - Professional verification report generated successfully")
    st.balloons()

    # Results section
    st.markdown("""
    <div class="results-section">
    """, unsafe_allow_html=True)

    result_text = str(result)
    result_lower = result_text.lower()

    st.markdown("### 📊 Verification Result")

    # Determine verdict
    if "true" in result_lower and "false" not in result_lower and "misleading" not in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-true">
            ✅ VERDICT: THE PROVIDED INFORMATION IS TRUE
        </div>
        """, unsafe_allow_html=True)
    elif "false" in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-false">
            ❌ VERDICT: THE PROVIDED INFORMATION IS FALSE
        </div>
        """, unsafe_allow_html=True)
    elif "misleading" in result_lower or "partially" in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-partial">
            ⚠️ VERDICT: THE PROVIDED INFORMATION IS PARTIALLY ACCURATE
        </div>
        """, unsafe_allow_html=True)
    elif "inconclusive" in result_lower:
        st.markdown("""
        <div class="verdict-container verdict-inconclusive">
            🔍 VERDICT: REQUIRES FURTHER INVESTIGATION
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="verdict-container verdict-inconclusive">
            📋 DETAILED ANALYSIS AVAILABLE
        </div>
        """, unsafe_allow_html=True)

    # Detailed report
    st.markdown("### 📄 Comprehensive Analysis Report")
    with st.expander("**Click to view detailed verification report**", expanded=True):
        st.markdown(result_text)

    st.markdown("</div>", unsafe_allow_html=True)

    # Download options
    st.markdown("### 📥 Export Options")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📄 Download as Text Report",
            data=result_text,
            file_name="satyagyan_professional_report.txt",
            mime="text/plain",
            use_container_width=True
        )

# Professional Footer
st.markdown("""
<div class="footer">
    © 2025 Shri Kolekar SK - All Rights Reserved
</div>
""", unsafe_allow_html=True)