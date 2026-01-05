import streamlit as st
import pdfplumber
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_text_from_pdf(pdf_file):
    """Extract all text from a PDF file."""
    text = ""
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text.strip()
    
    except Exception as e:
        return f"Error extracting text: {str(e)}"


def compare_resume_jd(resume_text, jd_text):
    """Send resume and JD to OpenAI for comparison."""
    
    prompt = f"""You are a technical recruiter performing a skill-match analysis.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

TASK:
Compare the resume against the job description with these rules:
1. Focus ONLY on technical skills and tools
2. Output exactly 5-6 lines
3. Explicitly list missing required skills
4. Use technical, precise language
5. Do not add pleasantries or summaries

OUTPUT FORMAT:
- Line 1: Matched skills (list them)
- Lines 2-4: Missing skills and gaps (be explicit)
- Line 5-6: Brief technical assessment

Begin your analysis:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical recruiter focused on skill analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        analysis = response.choices[0].message.content
        return analysis
    
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"


# Streamlit UI
st.set_page_config(
    page_title="Resume-JD Matcher",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Resume vs Job Description Matcher")
st.markdown("Upload a resume and paste a job description to analyze skill matching.")

# Create two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Upload Resume")
    resume_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload the candidate's resume in PDF format"
    )

with col2:
    st.subheader("2️⃣ Job Description")
    jd_text = st.text_area(
        "Paste the job description here",
        height=300,
        placeholder="Paste the full job description text..."
    )

st.markdown("---")
analyze_button = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

# Process when button clicked
if analyze_button:
    if not resume_file:
        st.error("⚠️ Please upload a resume PDF")
    elif not jd_text.strip():
        st.error("⚠️ Please enter a job description")
    else:
        with st.spinner("🔄 Analyzing resume vs job description..."):
            
            # Extract resume text
            resume_text = extract_text_from_pdf(resume_file)
            
            if resume_text.startswith("Error"):
                st.error(resume_text)
            else:
                # Get analysis
                analysis = compare_resume_jd(resume_text, jd_text)
                
                # Display results
                st.success("✅ Analysis Complete")
                st.subheader("📊 Skill Match Analysis")
                st.info(analysis)
                
                # Debug: show extracted text
                with st.expander("🔍 View Extracted Resume Text"):
                    st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)