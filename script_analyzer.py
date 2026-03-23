"""
Core script analysis module using LLM API.
Supports OpenAI (default), Google Gemini, Anthropic Claude, and OpenRouter Free via API.
"""

import json
import os
import re
from typing import Optional

import requests
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover
    OpenAI = None

from prompts import SYSTEM_PROMPT, get_user_prompt

# Load environment variables from .env file
load_dotenv()


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL_NAME = "openrouter/free"
OPENROUTER_TIMEOUT_SECONDS = 60


class ScriptAnalyzer:
    """Analyzes scripts using multiple LLM APIs (OpenAI, Gemini, Claude, OpenRouter Free) to generate storytelling insights."""

    def __init__(self, api_key: Optional[str] = None, model: str = "openai"):
        """
        Initialize the analyzer with the specified LLM API.

        Args:
            api_key: Optional API key. If not provided, uses environment variables.
            model: Which model to use: "openai" (default), "gemini", "claude", or "openrouter_free"
        """
        self.model = model.lower()

        if self.model == "openai":
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError(
                    "OPENAI_API_KEY not provided. "
                    "Set it as an environment variable or pass it as an argument."
                )
            if OpenAI is None:
                raise ValueError(
                    "OpenAI SDK not installed. Run `pip install openai` before using this model."
                )
            self.client = OpenAI(api_key=key)

        elif self.model == "gemini":
            key = api_key or os.getenv("GEMINI_API_KEY")
            if not key:
                raise ValueError(
                    "GEMINI_API_KEY not provided. "
                    "Set it as an environment variable or pass it as an argument."
                )
            import google.generativeai as genai
            genai.configure(api_key=key)
            self.client = genai

        elif self.model == "claude":
            from anthropic import Anthropic
            key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not provided. "
                    "Set it as an environment variable or pass it as an argument."
                )
            self.client = Anthropic(api_key=key)
        elif self.model == "openrouter_free":
            key = api_key or os.getenv("OPENROUTER_API_KEY")
            if not key:
                raise ValueError(
                    "OPENROUTER_API_KEY not provided. "
                    "Set it as an environment variable or pass it as an argument."
                )
            self.openrouter_api_key = key
            self.client = None
        else:
            raise ValueError(
                f"Unsupported model: {model}. Use 'openai', 'gemini', 'claude', or 'openrouter_free'"
            )

    def analyze_script(self, script_text: str) -> dict:
        """
        Analyze a script using the configured LLM API.

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
            if self.model == "openai":
                response = self._call_openai(user_message)
            elif self.model == "gemini":
                response = self._call_gemini(user_message)
            elif self.model == "claude":
                response = self._call_claude(user_message)
            elif self.model == "openrouter_free":
                response = self._call_openrouter_free(user_message)
            else:
                raise ValueError(f"Unsupported model: {self.model}")

            response_text = response
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

            json_str = self._sanitize_json(json_str)
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

    @staticmethod
    def _sanitize_json(raw_json: str) -> str:
        """Attempt to repair minor formatting issues (e.g., trailing commas)."""
        # Remove trailing commas before closing object/array tokens
        sanitized = re.sub(r",\s*(?=[}\]])", "", raw_json)
        return sanitized

    def _call_openai(self, user_message: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    def _call_gemini(self, user_message: str) -> str:
        """Call Google Gemini API."""
        model = self.client.GenerativeModel("gemini-2.0-flash")
        combined_prompt = f"{SYSTEM_PROMPT}\n\n{user_message}"
        response = model.generate_content(
            combined_prompt,
            generation_config=self.client.types.GenerationConfig(
                max_output_tokens=2048,
                temperature=0.7,
            ),
        )
        return response.text

    def _call_claude(self, user_message: str) -> str:
        """Call Claude API."""
        response = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def _call_openrouter_free(self, user_message: str) -> str:
        """Call the OpenRouter free models router."""
        payload = {
            "model": OPENROUTER_MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "reasoning": {"enabled": True},
        }
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            OPENROUTER_CHAT_URL,
            json=payload,
            headers=headers,
            timeout=OPENROUTER_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("OpenRouter returned no choices in the response.")

        message_content = choices[0].get("message", {}).get("content")
        if message_content is None:
            raise ValueError("OpenRouter response missing message content.")

        return message_content

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
