"""
Core script analysis module using LLM API.
Supports OpenAI (default) and Anthropic Claude via API.
"""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT, get_user_prompt

# Load environment variables from .env file
load_dotenv()


class ScriptAnalyzer:
    """Analyzes scripts using OpenAI API (default) to generate storytelling insights."""

    def __init__(self, api_key: Optional[str] = None, use_openai: bool = True):
        """
        Initialize the analyzer with OpenAI API key (default).

        Args:
            api_key: Optional API key. If not provided, uses OPENAI_API_KEY or ANTHROPIC_API_KEY env vars.
            use_openai: If True (default), uses OpenAI. If False, uses Claude/Anthropic.
        """
        self.use_openai = use_openai

        if self.use_openai:
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError(
                    "OPENAI_API_KEY not provided. "
                    "Set it as an environment variable or pass it as an argument."
                )
            self.client = OpenAI(api_key=key)
        else:
            from anthropic import Anthropic
            key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not provided. "
                    "Set it as an environment variable or pass it as an argument."
                )
            self.client = Anthropic(api_key=key)

    def analyze_script(self, script_text: str) -> dict:
        """
        Analyze a script using OpenAI or Claude API.

        Args:
            script_text: The full text of the script

        Returns:
            A dictionary containing analysis results with keys:
            - summary
            - emotional_tone
            - engagement_potential
            - improvement_suggestions
            - most_suspenseful_moment
            - raw_response (full response for debugging)

        Raises:
            ValueError: If script is empty or too short
            json.JSONDecodeError: If response cannot be parsed as JSON
        """
        if not script_text or not script_text.strip():
            raise ValueError("Script text cannot be empty")

        if len(script_text.strip()) < 50:
            raise ValueError("Script text is too short (minimum 50 characters)")

        # Prepare prompts
        user_message = get_user_prompt(script_text)

        try:
            if self.use_openai:
                # Call OpenAI API
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=2048,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.7,
                )
                response_text = response.choices[0].message.content
            else:
                # Call Claude API
                response = self.client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_message}],
                )
                response_text = response.content[0].text
        except Exception as e:
            return {
                "error": f"API call failed: {str(e)}",
                "raw_response": str(e),
                "parse_error": str(type(e).__name__),
            }

        # Parse JSON response
        try:
            # Try to find JSON in the response (might wrap it in markdown)
            json_str = response_text

            # If wrapped in markdown code blocks, extract the JSON
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()

            analysis = json.loads(json_str)
        except json.JSONDecodeError as e:
            # If parsing fails, return raw response with error info
            return {
                "error": "Failed to parse response as JSON",
                "raw_response": response_text,
                "parse_error": str(e),
            }

        # Add raw response for debugging
        analysis["raw_response"] = response_text

        return analysis

    def validate_analysis(self, analysis: dict) -> bool:
        """
        Validate that the analysis contains all expected keys.

        Args:
            analysis: The analysis dictionary from analyze_script

        Returns:
            True if valid, False otherwise
        """
        expected_keys = {
            "summary",
            "emotional_tone",
            "engagement_potential",
            "improvement_suggestions",
            "most_suspenseful_moment",
        }

        if "error" in analysis:
            return False

        return all(key in analysis for key in expected_keys)


def analyze_script(script_text: str) -> dict:
    """
    Convenience function to analyze a script using the default analyzer.

    Args:
        script_text: The full text of the script

    Returns:
        Analysis dictionary (see ScriptAnalyzer.analyze_script for details)
    """
    analyzer = ScriptAnalyzer()
    return analyzer.analyze_script(script_text)
