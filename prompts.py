"""
Prompt definitions for script analysis using Claude API.
Handles system and user prompts for structured script analysis.
"""

SYSTEM_PROMPT = """You are an expert screenwriting analyst and storytelling consultant. Your role is to analyze short scripts and provide detailed insights about their narrative structure, emotional impact, and engagement potential.

You analyze scripts across these key dimensions:
1. **Story Summary**: A concise 3-4 line summary of the plot
2. **Emotional Tone**: The dominant emotions conveyed and how they evolve throughout the script
3. **Engagement Potential**: A score (0-10) with breakdown of specific factors:
   - Opening Hook: How compelling is the opening? (0-10)
   - Character Conflict: Depth of character dynamics and conflicts? (0-10)
   - Tension/Pacing: How well-paced is the story? (0-10)
   - Cliffhanger/Resolution: Strength of the ending hook? (0-10)
4. **Improvement Suggestions**: Specific, actionable feedback on:
   - Pacing issues
   - Character development
   - Dialogue quality and authenticity
   - Emotional impact and moments
   - Story structure and narrative flow
5. **Most Suspenseful Moment**: Identify and describe the most suspenseful or cliffhanger moment

Provide your analysis in a structured JSON format for clarity and consistency."""


def get_user_prompt(script_text: str) -> str:
    """
    Generate the user prompt for analyzing a script.

    Args:
        script_text: The full text of the script to analyze

    Returns:
        A formatted user prompt ready to send to Claude
    """
    return f"""Analyze the following script and provide detailed insights:

<SCRIPT>
{script_text}
</SCRIPT>

Please provide your analysis in the following JSON format:
{{
    "summary": "3-4 line summary of the plot",
    "emotional_tone": {{
        "dominant_emotions": ["emotion1", "emotion2", ...],
        "emotional_arc": "Description of how emotions evolve",
        "key_emotional_moments": ["moment 1", "moment 2", ...]
    }},
    "engagement_potential": {{
        "overall_score": 0-10,
        "breakdown": {{
            "opening_hook": {{"score": 0-10, "explanation": "..."}},
            "character_conflict": {{"score": 0-10, "explanation": "..."}},
            "tension_pacing": {{"score": 0-10, "explanation": "..."}},
            "cliffhanger_resolution": {{"score": 0-10, "explanation": "..."}}
        }}
    }},
    "improvement_suggestions": {{
        "pacing": "...",
        "character_development": "...",
        "dialogue": "...",
        "emotional_impact": "...",
        "story_structure": "..."
    }},
    "most_suspenseful_moment": {{
        "moment": "Description of the moment",
        "why_suspenseful": "Explanation of what makes it suspenseful/cliffhanger-y",
        "line_or_scene": "Reference to when it occurs in the script"
    }}
}}

Be specific, concrete, and insightful. Reference actual dialogue or scenes from the script in your analysis."""


def get_analysis_prompt(script_text: str) -> str:
    """
    Legacy alias for get_user_prompt for backward compatibility.
    """
    return get_user_prompt(script_text)
