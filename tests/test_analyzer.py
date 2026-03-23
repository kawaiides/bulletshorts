"""
Unit tests for the script analyzer module using OpenAI, Gemini, and Claude.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from script_analyzer import OPENROUTER_CHAT_URL, ScriptAnalyzer, analyze_script


class TestScriptAnalyzer:
    """Tests for the ScriptAnalyzer class."""

    @patch("script_analyzer.OpenAI")
    def test_analyzer_initialization(self, mock_openai):
        """Test that analyzer initializes with OpenAI API key."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            assert analyzer.client is not None
            mock_openai.assert_called_once_with(api_key="test_key")

    def test_analyzer_missing_openai_key(self):
        """Test that analyzer raises error without OpenAI API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                ScriptAnalyzer(model="openai")

    def test_analyzer_missing_gemini_key(self):
        """Test that analyzer raises error without Gemini API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                ScriptAnalyzer(model="gemini")

    def test_analyzer_missing_claude_key(self):
        """Test that analyzer raises error without Claude API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                ScriptAnalyzer(model="claude")

    def test_analyzer_missing_openrouter_key(self):
        """Test that analyzer raises error without OpenRouter API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
                ScriptAnalyzer(model="openrouter_free")

    def test_analyzer_invalid_model(self):
        """Test that analyzer raises error for invalid model."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with pytest.raises(ValueError, match="Unsupported model"):
                ScriptAnalyzer(model="invalid_model")

    @patch("script_analyzer.OpenAI")
    def test_empty_script_validation(self, mock_openai):
        """Test that empty scripts are rejected."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            with pytest.raises(ValueError, match="empty"):
                analyzer.analyze_script("")

    @patch("script_analyzer.OpenAI")
    def test_script_too_short(self, mock_openai):
        """Test that very short scripts are rejected."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            with pytest.raises(ValueError, match="too short"):
                analyzer.analyze_script("Hi!")

    @patch("script_analyzer.OpenAI")
    def test_analyze_script_success(self, mock_openai_class):
        """Test successful script analysis with mocked OpenAI response."""
        test_response = {
            "summary": "A story about two people meeting.",
            "emotional_tone": {
                "dominant_emotions": ["melancholy", "hope"],
                "emotional_arc": "Starts sad, ends hopeful",
                "key_emotional_moments": ["the reunion", "the revelation"],
            },
            "engagement_potential": {
                "overall_score": 8,
                "breakdown": {
                    "opening_hook": {"score": 8, "explanation": "Strong opener"},
                    "character_conflict": {
                        "score": 9,
                        "explanation": "Deep emotional conflict",
                    },
                    "tension_pacing": {"score": 7, "explanation": "Good pacing"},
                    "cliffhanger_resolution": {
                        "score": 8,
                        "explanation": "Satisfying ending",
                    },
                },
            },
            "improvement_suggestions": {
                "pacing": "Could be faster",
                "character_development": "Excellent",
                "dialogue": "Natural and authentic",
                "emotional_impact": "Powerful",
                "story_structure": "Well-structured",
            },
            "most_suspenseful_moment": {
                "moment": "The reunion scene",
                "why_suspenseful": "High stakes and uncertainty",
                "line_or_scene": "When Marcus enters",
            },
        }

        # Setup mock
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(test_response)
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            result = analyzer.analyze_script(
                "This is a test script about two characters meeting."
            )

        assert "summary" in result
        assert "emotional_tone" in result
        assert "engagement_potential" in result
        assert result["engagement_potential"]["overall_score"] == 8

    @patch("script_analyzer.OpenAI")
    def test_analyze_script_with_markdown_json(self, mock_openai_class):
        """Test analysis when OpenAI returns JSON wrapped in markdown."""
        test_response = {
            "summary": "Test summary",
            "emotional_tone": {},
            "engagement_potential": {},
            "improvement_suggestions": {},
            "most_suspenseful_moment": {},
        }

        mock_choice = MagicMock()
        mock_choice.message.content = (
            "```json\n" + json.dumps(test_response) + "\n```"
        )
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            result = analyzer.analyze_script(
                "This is a test script with enough content to pass validation requirements."
            )

        assert "summary" in result
        assert result["summary"] == "Test summary"

    @patch("script_analyzer.OpenAI")
    def test_analyze_script_invalid_json(self, mock_openai_class):
        """Test handling of invalid JSON response from OpenAI."""
        mock_choice = MagicMock()
        mock_choice.message.content = "This is not valid JSON response at all"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            result = analyzer.analyze_script(
                "This is a test script with enough content to pass validation."
            )

        assert "error" in result
        assert "Failed to parse" in result["error"]

    @patch("script_analyzer.OpenAI")
    def test_analyze_script_trailing_commas(self, mock_openai_class):
        """Ensure trailing commas in JSON do not break parsing after sanitization."""
        test_response = {
            "summary": "Comma safe",
            "emotional_tone": {},
            "engagement_potential": {},
            "improvement_suggestions": {},
            "most_suspenseful_moment": {},
        }

        json_base = json.dumps(test_response)
        json_with_trailing = "```json\n" + json_base[:-1] + ",\n}\n```"
        mock_choice = MagicMock()
        mock_choice.message.content = json_with_trailing
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            result = analyzer.analyze_script(
                "This script has enough length to pass validation and contains more than fifty characters."
            )

        assert result["summary"] == "Comma safe"

    @patch("script_analyzer.OpenAI")
    def test_sanitize_unterminated_string(self, mock_openai_class):
        """Ensure unterminated strings are closed so JSON can be parsed."""
        test_response = {
            "summary": "Partial",
            "emotional_tone": {},
            "engagement_potential": {},
            "improvement_suggestions": {},
            "most_suspenseful_moment": {},
        }

        payload = json.dumps(test_response)
        # remove final quote for "summary" to simulate unterminated string
        broken = payload.replace('"Partial"', '"Partial', 1)
        json_broken = f"```json\n{broken}\n```"

        mock_choice = MagicMock()
        mock_choice.message.content = json_broken
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            result = analyzer.analyze_script(
                "This script has enough length to pass validation and contains more than fifty characters."
            )

        assert result["summary"] == "Partial"

    @patch("script_analyzer.requests.post")
    def test_openrouter_free_analysis(self, mock_post):
        """Test analysis flow when using OpenRouter free models."""
        test_response_payload = {
            "summary": "Free router test summary",
            "emotional_tone": {},
            "engagement_potential": {},
            "improvement_suggestions": {},
            "most_suspenseful_moment": {},
        }

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": json.dumps(test_response_payload)}}
            ]
        }
        mock_post.return_value = mock_response

        script_text = "This script has enough length to pass the minimum validation requirement."
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test_or_key"}):
            analyzer = ScriptAnalyzer(model="openrouter_free")
            result = analyzer.analyze_script(script_text)

        assert result["summary"] == "Free router test summary"
        assert result["raw_response"] == json.dumps(test_response_payload)

        mock_post.assert_called_once()
        called_args, called_kwargs = mock_post.call_args
        assert called_args[0] == OPENROUTER_CHAT_URL
        assert called_kwargs["headers"]["Authorization"] == "Bearer test_or_key"
        assert called_kwargs["json"]["model"] == "openrouter/free"
        assert called_kwargs["json"]["reasoning"] == {"enabled": True}
        assert called_kwargs["timeout"] == 60

    @patch("script_analyzer.OpenAI")
    def test_validate_analysis_success(self, mock_openai):
        """Test validation of complete analysis."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            valid_analysis = {
                "summary": "Test",
                "emotional_tone": {},
                "engagement_potential": {},
                "improvement_suggestions": {},
                "most_suspenseful_moment": {},
            }
            assert analyzer.validate_analysis(valid_analysis) is True

    @patch("script_analyzer.OpenAI")
    def test_validate_analysis_missing_key(self, mock_openai):
        """Test validation fails with missing keys."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            invalid_analysis = {"summary": "Test"}
            assert analyzer.validate_analysis(invalid_analysis) is False

    @patch("script_analyzer.OpenAI")
    def test_validate_analysis_with_error(self, mock_openai):
        """Test validation fails when analysis has error."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer(model="openai")
            error_analysis = {"error": "Test error"}
            assert analyzer.validate_analysis(error_analysis) is False

    @patch("script_analyzer.OpenAI")
    def test_analyze_script_convenience_function(self, mock_openai_class):
        """Test the convenience function analyze_script."""
        test_response = {
            "summary": "Test",
            "emotional_tone": {},
            "engagement_potential": {},
            "improvement_suggestions": {},
            "most_suspenseful_moment": {},
        }

        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(test_response)
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            result = analyze_script(
                "This is a test script with enough content to pass minimum length validation."
            )

        assert "summary" in result
