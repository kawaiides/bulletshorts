# Script Analyzer - AI-Powered Storytelling Insights

An intelligent script analysis system powered by Claude that generates deep insights about scripts' narrative structure, emotional impact, and engagement potential.

## Features

- 📖 **Story Summaries**: Concise 3-4 line summaries capturing the essence of your script
- 💭 **Emotional Analysis**: Identification of dominant emotions and the emotional arc throughout the script
- ⭐ **Engagement Scoring**: 0-10 engagement potential score with breakdown of:
  - Opening Hook
  - Character Conflict
  - Tension & Pacing
  - Cliffhanger/Resolution
- 💡 **Improvement Suggestions**: Actionable feedback on pacing, dialogue, character development, and story structure
- 🎬 **Suspenseful Moments**: Identification of the most suspenseful or cliffhanger moment
- 🌐 **OpenRouter Free Models**: Optional zero-cost inference via the `openrouter/free` router

## System Architecture

```
┌─────────────┐
│   User     │
│  Uploads   │
│  Script    │
└──────┬──────┘
       │
       ▼
┌────────────────────┐
│  Streamlit App     │
│   (app.py)        │
├────────────────────┤
│ - Input handling   │
│ - Results display  │
│ - UI formatting    │
└──────┬─────────────┘
       │
       ▼
┌────────────────────┐
│ ScriptAnalyzer     │
│ (script_analyzer.py)
├────────────────────┤
│ - Orchestration    │
│ - JSON parsing     │
│ - Error handling   │
└──────┬─────────────┘
       │
       ▼
┌────────────────────┐
│  Claude API        │
│  (Anthropic)      │
├────────────────────┤
│ - Analysis         │
│ - Insights         │
│ - Structured JSON  │
└────────────────────┘
```

The `ScriptAnalyzer` can target OpenAI, Gemini, Claude, or OpenRouter's free router depending on the selected model.

## Installation & Setup

### Prerequisites
- Python 3.10+
- Anthropic API key (free or paid tier)
- OpenRouter API key (optional, for the `openrouter/free` router)

### Step 1: Get an API Key
1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API keys and create a new key
4. Copy the key (you'll need it in Step 3)

### Step 1b: (Optional) Get an OpenRouter Key
1. Go to [https://openrouter.ai/](https://openrouter.ai/) and sign up for a free account
2. Head to the API keys dashboard and create a new key
3. Store the key safely; it will power the `openrouter/free` router in this app

### Step 2: Clone/Setup the Project
```bash
cd bulletshorts
```

### Step 3: Configure Environment
Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=your_api_key_here
OPENROUTER_API_KEY=your_openrouter_key_here  # Optional: required only for the free router
```

Replace `your_api_key_here` with the actual API key from Step 1.

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

You may want to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

The app will open in your browser (typically at `http://localhost:8501`)

## How to Use

1. **Input Your Script**: Choose one of three methods:
   - **Paste Text**: Copy and paste your script directly
   - **Upload File**: Upload a `.txt` file containing your script
   - **Use Sample**: Run analysis on the included sample script

2. **Click "Analyze Script"**: The system will send your script to Claude for analysis

3. **Review Results**: The app displays:
   - Story summary
   - Emotional breakdown
   - Engagement potential score
   - Improvement suggestions
   - Most suspenseful moment

## Prompt Design & Model Integration

### System Prompt Strategy
The system prompt establishes Claude's role as an expert screenwriting analyst and defines the five key analysis dimensions. This ensures consistent, focused analysis across all submissions.

**Key Features:**
- Clear role definition: "expert screenwriting analyst"
- Specific analysis dimensions: summary, emotions, engagement, improvements, suspenseful moments
- Structured output requirement: JSON format for reliable parsing
- Quality guidelines: "be specific, concrete, and insightful"

### User Prompt Strategy
The user prompt includes:
1. The full script text (clearly marked)
2. A detailed JSON schema showing expected output format
3. Specific instructions to reference actual dialogue/scenes
4. Clear scoring guidelines (0-10 scales with explanations)

### Why Structured Output?
Claude is prompted to return JSON-formatted responses for several reasons:
- **Reliability**: Easier to parse and extract specific insights
- **Consistency**: Same structure across all analyses
- **Usability**: Format naturally matches the Streamlit display requirements
- **Error Handling**: Invalid JSON is caught and reported to the user

### Model Choice
Claude (Opus 4.6) remains the default due to its reasoning skills, long context window, and structured output reliability—qualities that match the five analysis dimensions.

OpenRouter's `openrouter/free` router is also available for zero-cost experimentation. It automatically rotates among free models that support reasoning and structured outputs, so the delivered responses may vary slightly in tone/quality but keep costs at $0/token.

## Technical Implementation Details

### Core Modules

#### `prompts.py`
Defines the system and user prompts. Separated for:
- Easy testing and iteration
- Clear prompt engineering visibility
- Quick updates to prompt strategies

#### `script_analyzer.py`
Handles all Claude API interactions:
- Creates `ScriptAnalyzer` class with initialization and analysis methods
- Validates input (minimum length, non-empty)
- Calls Claude API with structured prompts
- Parses JSON responses (handles markdown-wrapped JSON)
- Includes graceful error handling

#### `app.py`
Streamlit web interface:
- Multiple input methods (paste, upload, sample)
- Real-time error messages
- Organized result display with collapsible sections
- Visual engagement score with progress bar
- Session state management for smooth UX

### Error Handling

The system handles several error scenarios:
1. **Empty/Short Scripts**: ValueError raised with helpful message
2. **Missing API Key**: Immediate user notification
3. **Invalid JSON**: Falls back to displaying raw response with parse error
4. **API Errors**: Caught and displayed to user
5. **Markdown-Wrapped JSON**: Automatically extracted and parsed

## Limitations

### Current Limitations
1. **Script Length**: Designed for 1-3 page scripts; very long scripts (10+ pages) may be truncated or analyzed less thoroughly
2. **English Only**: Prompts and analysis assume English-language scripts
3. **Narrative Scripts Only**: Designed for dialogue-heavy scripts; may not work well for non-narrative content (essays, poetry, etc.)
4. **Context Window**: Limited to Claude's context window (~200k tokens, but using ~2k token limit for responses)
5. **Cultural Context**: May miss cultural-specific nuances or references not apparent from dialogue alone
6. **Real-time Limitations**: Each analysis takes 5-15 seconds (API latency), no streaming currently

### Analysis Limitations
- Engagement scores are Claude's interpretation; may not perfectly correlate with actual audience engagement
- Emotional analysis reflects Claude's perception; human readers may identify different dominant emotions
- Improvement suggestions are recommendations, not prescriptions—creative choices are subjective

## Possible Improvements

### Short-term (Easy Additions)
1. **Result Export**: Add buttons to export analysis as PDF, JSON, or Markdown
2. **Prompt Customization**: Allow users to adjust analysis focus (e.g., "focus on dialogue quality")
3. **Multi-language Support**: Extend prompts to support non-English scripts
4. **Result History**: Track previous analyses in a session (with delete option)
5. **Caching**: Cache identical script analyses to reduce API costs

### Medium-term (Moderate Effort)
1. **Streaming Output**: Stream Claude's response in real-time in Streamlit
2. **Comparison Mode**: Analyze multiple script versions and compare results side-by-side
3. **Genre-Specific Analysis**: Tailored prompts for comedy, drama, horror, thriller scripts
4. **Collaboration Features**: Share analysis results and gather team feedback
5. **File Format Support**: Handle .pdf, .docx, .fountain (screenwriting format) files

### Long-term (Significant Effort)
1. **Custom Model Fine-tuning**: Fine-tune Claude on examples of excellent scripts
2. **Visual Analytics**: Charts and graphs for emotional arc, pacing, character interactions
3. **Revision Suggestions**: AI-powered script revisions based on feedback
4. **Benchmark Database**: Compare scripts against successful productions in same genre
5. **Integration with Industry Tools**: Sync with screenwriting software (Final Draft, Celtx, etc.)

## Testing

### Running Unit Tests
```bash
pytest tests/
```

### Manual Testing
1. Start the Streamlit app: `streamlit run app.py`
2. Test with the sample script: Click "Use Sample" and analyze
3. Test with custom text: Paste a short dialogue scene
4. Test with file upload: Create a text file and upload it

### Test Cases Covered
- ✅ API key validation
- ✅ Empty/short script rejection
- ✅ JSON parsing (including markdown-wrapped JSON)
- ✅ Analysis validation
- ✅ Error handling

## Project Structure
```
bulletshorts/
├── app.py                          # Streamlit web interface
├── script_analyzer.py              # Core analysis logic
├── prompts.py                      # Prompt definitions
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (API key)
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── sample_scripts/
│   └── scene_reunion.txt           # Sample script for testing
├── tests/
│   ├── __init__.py
│   └── test_analyzer.py            # Unit tests for analyzer
```

## Technology Stack
- **LLM**: Claude Opus 4.6 (Anthropic)
- **Frontend**: Streamlit 1.42.1
- **Backend**: Python 3.10+
- **API Client**: anthropic 0.39.0
- **Testing**: pytest 7.4.4
- **Environment**: python-dotenv 1.0.1
- **HTTP Client**: requests (used for OpenRouter's router)

## Performance Characteristics

### API Calls
- **Per Analysis**: 1 API call to the selected provider (Claude, OpenAI, Gemini, or OpenRouter's free router)
- **Cost**: ~$0.01-0.05 per analysis when using Claude (OpenRouter's `openrouter/free` router is $0 input/output tokens)
- **Time**: 5-15 seconds per analysis

### Scalability Considerations
The current implementation is suitable for:
- ✅ Individual creators testing scripts
- ✅ Small writing groups (10-50 users/day)
- ⚠️ Larger teams would benefit from caching and rate limiting

### Cost Optimization
To reduce costs:
- Implement result caching
- Use batch API requests for multiple scripts
- Consider Claude 3.5 Haiku for faster, cheaper analysis of simpler aspects

## Future Development Roadmap

| Phase | Feature | Timeline |
|-------|---------|----------|
| V1 | Core analysis, Streamlit UI | ✅ Complete |
| V2 | Export, caching, customization | 1-2 weeks |
| V3 | Real-time streaming, comparisons | 2-4 weeks |
| V4 | Fine-tuning, advanced analytics | 1-2 months |

## Troubleshooting

### API Key Not Found
**Error**: "ANTHROPIC_API_KEY not found"
**Solution**: Ensure .env file exists and contains `ANTHROPIC_API_KEY=your_key`

### OpenRouter Key Not Found
**Error**: "OPENROUTER_API_KEY not found"
**Solution**: Add `OPENROUTER_API_KEY=your_key` to `.env` if you plan to use the free OpenRouter models; otherwise select Claude/OpenAI/Gemini.

### OpenRouter 400 Bad Request
**Error**: `400 Client Error: Bad Request`
**Solution**: Ensure the OpenRouter payload follows the documented schema (e.g., `reasoning` must be an object like `{"enabled": true}` instead of a bare boolean). This keeps the router happy with structured output expectations.

### Token/Authenticity Errors
**Error**: "Invalid authentication" or token-related errors
**Solution**: Verify your API key is correct at https://console.anthropic.com/

### Script Too Short
**Error**: "Script text is too short (minimum 50 characters)"
**Solution**: Provide a longer script or more dialogue

### JSON Parse Errors
**Error**: "Failed to parse Claude's response as JSON"
**Solution**: Usually temporary; retry the analysis. If persistent, check API status

## Contributing

To contribute improvements:
1. Test thoroughly with different script types
2. Document any prompt changes
3. Update this README
4. Ensure tests pass: `pytest tests/`

## License

This project is part of the Bullet AI Engineer assignment (2024-2025).

## Contact & Support

- API Issues: Check [Anthropic Status](https://status.anthropic.com/)
- Feature Requests: Document in project issues
- Questions: Review this README or consult the code comments

---

**Built with ❤️ using Claude API**

Last Updated: 2024
