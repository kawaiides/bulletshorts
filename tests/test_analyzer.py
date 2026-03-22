"""
Unit tests for the script analyzer module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from script_analyzer import ScriptAnalyzer, analyze_script


class TestScriptAnalyzer:
    """Tests for the ScriptAnalyzer class."""

    @patch("script_analyzer.Anthropic")
    def test_analyzer_initialization(self, mock_anthropic):
        """Test that analyzer initializes with API key."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            assert analyzer.client is not None
            mock_anthropic.assert_called_once_with(api_key="test_key")

    def test_analyzer_missing_api_key(self):
        """Test that analyzer raises error without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                ScriptAnalyzer()

    @patch("script_analyzer.Anthropic")
    def test_empty_script_validation(self, mock_anthropic):
        """Test that empty scripts are rejected."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            with pytest.raises(ValueError, match="empty"):
                analyzer.analyze_script("")

    @patch("script_analyzer.Anthropic")
    def test_script_too_short(self, mock_anthropic):
        """Test that very short scripts are rejected."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            with pytest.raises(ValueError, match="too short"):
                analyzer.analyze_script("Hi!")

    @patch("script_analyzer.Anthropic")
    def test_analyze_script_success(self, mock_anthropic_class):
        """Test successful script analysis with mocked Claude response."""
        # Mock Claude response
        mock_response = MagicMock()
        mock_response.content[0].text = json.dumps(
            {
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
        )

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            result = analyzer.analyze_script("This is a test script about two characters meeting.")

        assert "summary" in result
        assert "emotional_tone" in result
        assert "engagement_potential" in result
        assert result["engagement_potential"]["overall_score"] == 8

    @patch("script_analyzer.Anthropic")
    def test_analyze_script_with_markdown_json(self, mock_anthropic_class):
        """Test analysis when Claude returns JSON wrapped in markdown."""
        mock_response = MagicMock()
        mock_response.content[0].text = (
            "```json\n"
            + json.dumps(
                {
                    "summary": "Test summary",
                    "emotional_tone": {},
                    "engagement_potential": {},
                    "improvement_suggestions": {},
                    "most_suspenseful_moment": {},
                }
            )
            + "\n```"
        )

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            result = analyzer.analyze_script("This is a test script with enough content to pass validation requirements.")

        assert "summary" in result
        assert result["summary"] == "Test summary"

    @patch("script_analyzer.Anthropic")
    def test_analyze_script_invalid_json(self, mock_anthropic_class):
        """Test handling of invalid JSON response from Claude."""
        mock_response = MagicMock()
        mock_response.content[0].text = "This is not valid JSON response at all"

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            result = analyzer.analyze_script("This is a test script with enough content to pass validation.")

        assert "error" in result
        assert "Failed to parse" in result["error"]

    @patch("script_analyzer.Anthropic")
    def test_validate_analysis_success(self, mock_anthropic):
        """Test validation of complete analysis."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            valid_analysis = {
                "summary": "Test",
                "emotional_tone": {},
                "engagement_potential": {},
                "improvement_suggestions": {},
                "most_suspenseful_moment": {},
            }
            assert analyzer.validate_analysis(valid_analysis) is True

    @patch("script_analyzer.Anthropic")
    def test_validate_analysis_missing_key(self, mock_anthropic):
        """Test validation fails with missing keys."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            invalid_analysis = {"summary": "Test"}
            assert analyzer.validate_analysis(invalid_analysis) is False

    @patch("script_analyzer.Anthropic")
    def test_validate_analysis_with_error(self, mock_anthropic):
        """Test validation fails when analysis has error."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            analyzer = ScriptAnalyzer()
            error_analysis = {"error": "Test error"}
            assert analyzer.validate_analysis(error_analysis) is False

    @patch("script_analyzer.Anthropic")
    def test_analyze_script_convenience_function(self, mock_anthropic_class):
        """Test the convenience function analyze_script."""
        mock_response = MagicMock()
        mock_response.content[0].text = json.dumps(
            {
                "summary": "Test",
                "emotional_tone": {},
                "engagement_potential": {},
                "improvement_suggestions": {},
                "most_suspenseful_moment": {},
            }
        )

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            result = analyze_script("This is a test script with enough content to pass minimum length validation.")

        assert "summary" in result
