"""
Streamlit web application for script analysis.
Provides an interactive interface for users to submit scripts and view analysis results.
"""

import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from script_analyzer import ScriptAnalyzer

# Load environment variables from .env file
load_dotenv()


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "script_text" not in st.session_state:
        st.session_state.script_text = ""
    if "error_message" not in st.session_state:
        st.session_state.error_message = None


def display_summary(analysis: dict):
    """Display the story summary section."""
    st.subheader("📖 Story Summary")
    st.write(analysis.get("summary", "N/A"))


def display_emotional_tone(analysis: dict):
    """Display the emotional tone analysis section."""
    st.subheader("💭 Emotional Tone")

    emotional_tone = analysis.get("emotional_tone", {})

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Dominant Emotions:**")
        emotions = emotional_tone.get("dominant_emotions", [])
        if emotions:
            for emotion in emotions:
                st.write(f"• {emotion}")
        else:
            st.write("N/A")

    with col2:
        st.write("**Key Emotional Moments:**")
        moments = emotional_tone.get("key_emotional_moments", [])
        if moments:
            for moment in moments:
                st.write(f"• {moment}")
        else:
            st.write("N/A")

    st.write("**Emotional Arc:**")
    st.write(emotional_tone.get("emotional_arc", "N/A"))


def display_engagement(analysis: dict):
    """Display the engagement potential section with visual score."""
    st.subheader("⭐ Engagement Potential")

    engagement = analysis.get("engagement_potential", {})
    overall_score = engagement.get("overall_score", 0)

    # Display overall score prominently
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Overall Score", f"{overall_score}/10")
    with col2:
        st.progress(value=overall_score / 10)

    # Display breakdown scores
    st.write("**Component Breakdown:**")
    breakdown = engagement.get("breakdown", {})

    for component, details in breakdown.items():
        component_display = component.replace("_", " ").title()
        if isinstance(details, dict):
            score = details.get("score", 0)
            explanation = details.get("explanation", "N/A")
            col1, col2 = st.columns([1, 4])
            with col1:
                st.metric(component_display, f"{score}/10")
            with col2:
                st.write(explanation)
        else:
            st.write(f"**{component_display}:** {details}")


def display_improvements(analysis: dict):
    """Display the improvement suggestions section."""
    st.subheader("💡 Improvement Suggestions")

    suggestions = analysis.get("improvement_suggestions", {})

    for area, suggestion in suggestions.items():
        area_display = area.replace("_", " ").title()
        with st.expander(f"📌 {area_display}"):
            st.write(suggestion)


def display_suspenseful_moment(analysis: dict):
    """Display the most suspenseful moment section."""
    st.subheader("🎬 Most Suspenseful Moment")

    moment = analysis.get("most_suspenseful_moment", {})

    if moment:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**The Moment:**")
            st.write(moment.get("moment", "N/A"))

        with col2:
            st.write("**Why It's Suspenseful:**")
            st.write(moment.get("why_suspenseful", "N/A"))

        st.write("**Location in Script:**")
        st.write(moment.get("line_or_scene", "N/A"))
    else:
        st.write("No suspenseful moment identified.")


def display_results(analysis: dict):
    """Display all analysis results in organized sections."""
    if "error" in analysis:
        st.error(f"Analysis Error: {analysis.get('error')}")
        if "parse_error" in analysis:
            st.info(f"Parse Details: {analysis.get('parse_error')}")
        st.write("**Raw Response:**")
        st.code(analysis.get("raw_response", ""), language="text")
        return

    # Display all sections
    display_summary(analysis)
    st.divider()

    display_emotional_tone(analysis)
    st.divider()

    display_engagement(analysis)
    st.divider()

    display_improvements(analysis)
    st.divider()

    display_suspenseful_moment(analysis)

    # Optional: Show raw JSON for debugging
    with st.expander("🔍 View Raw Analysis (JSON)"):
        raw_response = analysis.get("raw_response", "")
        st.code(raw_response, language="json")


def load_sample_script():
    """Load a sample script for testing."""
    sample_dir = Path("sample_scripts")
    if sample_dir.exists():
        sample_files = list(sample_dir.glob("*.txt"))
        if sample_files:
            with open(sample_files[0], "r") as f:
                return f.read()
    return ""


def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Script Analyzer",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    initialize_session_state()

    # Header
    st.title("🎬 AI Script Analyzer")
    st.markdown(
        "Analyze your scripts with AI-powered insights. Get summaries, emotional analysis, "
        "engagement potential scores, and improvement suggestions."
    )

    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.warning(
                "⚠️ OPENAI_API_KEY not found. "
                "Please set it in your .env file or environment variables."
            )
            st.stop()

        st.success("✅ OpenAI API Key configured")

        st.markdown("---")
        st.header("📝 About")
        st.markdown(
            """
This application uses OpenAI (GPT-4o) to analyze scripts and provide insights on:
- Story structure and plot
- Emotional tone and arc
- Engagement potential (0-10 score)
- Actionable improvement suggestions
- Most suspenseful moments
            """
        )

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Submit Your Script")

        # Script input options
        input_method = st.radio(
            "How would you like to input your script?",
            ["Paste Text", "Upload File", "Use Sample"],
            horizontal=True,
        )

        script_text = ""

        if input_method == "Paste Text":
            script_text = st.text_area(
                "Paste your script here:",
                value=st.session_state.script_text,
                height=300,
                placeholder="Enter a short script (1-3 pages)...",
            )
        elif input_method == "Upload File":
            uploaded_file = st.file_uploader("Upload a script file", type=["txt"])
            if uploaded_file:
                script_text = uploaded_file.read().decode("utf-8")
        else:  # Use Sample
            script_text = load_sample_script()
            if script_text:
                st.info("📌 Using sample script. Feel free to replace it!")
            else:
                st.warning("No sample scripts found in sample_scripts/ directory.")

        # Update session state
        st.session_state.script_text = script_text

    with col2:
        st.header("Actions")
        analyze_button = st.button(
            "🔍 Analyze Script",
            use_container_width=True,
            type="primary",
        )

    st.divider()

    # Analysis
    if analyze_button:
        if not script_text or not script_text.strip():
            st.error("❌ Please enter or upload a script to analyze.")
        else:
            with st.spinner("🤔 Analyzing script... This may take a moment."):
                try:
                    analyzer = ScriptAnalyzer()
                    result = analyzer.analyze_script(script_text)
                    st.session_state.analysis_result = result
                    st.session_state.error_message = None
                except ValueError as e:
                    st.error(f"❌ Input Error: {str(e)}")
                    st.session_state.error_message = str(e)
                except Exception as e:
                    st.error(f"❌ Analysis Error: {str(e)}")
                    st.session_state.error_message = str(e)

    # Display results
    if st.session_state.analysis_result:
        st.header("📊 Analysis Results")
        display_results(st.session_state.analysis_result)


if __name__ == "__main__":
    main()
