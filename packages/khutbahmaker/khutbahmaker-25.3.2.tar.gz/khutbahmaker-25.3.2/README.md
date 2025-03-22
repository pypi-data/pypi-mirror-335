# khutbahmaker

Generate Islamic Friday sermons (khutbah) using AI (#GodamSahur 2025).

![KhutbahMaker Web UI](assets/thumb.webp)

## Installation

```bash
pip install khutbahmaker
```

## Key Features

- 📝 **Content Generation**
  - Topic-based Khutbah Generation
  - Multiple Language Support
  - Adjustable Length Options
  - Various Tone Settings
- 📊 **Output Formats**
  - Professional PDF Generation
  - Clean Markdown Text
  - RTL Support for Arabic
  - Beautiful Typography
- 🌐 **Flexible Integration**
  - Interactive Web UI
  - Python Library
  - Customizable Settings

## Usage

### Python Library

```python
from khutbahmaker import KhutbahMaker

# Initialize
client = KhutbahMaker(
    mode="default",                               # Mode (default/webui)
    api_key="YOUR_KEY",                           # AI service API key
    model="gemini-2.0-flash-thinking-exp-01-21"   # AI model to use
    timeout=180                                   # AI request timeout in seconds
)

# Generate khutbah
pdf_file, markdown_text = client.generate_khutbah(
    topic="Ramadan Preparation",   # Main topic/theme
    length="Short",                # short/medium/long
    tone="Inspirational",          # Tone of the khutbah
    language="Bahasa Malaysia"     # Target language
)
```

### Web UI

Start the Gradio web interface:

```python
client = KhutbahMaker(mode="webui")
# OR
client.start_webui(
    host="0.0.0.0",      # Server host
    port=5488,           # Server port
    browser=True,        # Launch browser
    upload_size="4MB",   # Max upload size
    public=False,        # Enable public URL
    limit=10             # Max concurrent requests
)
```

## Configuration

### Target Languages
- Bahasa Malaysia
- Arabic
- English
- Mandarin
- Tamil

### Khutbah Lengths
- **Short**: 10-15 minutes
- **Medium**: 15-20 minutes
- **Long**: 20-30 minutes

### Tone Options
- Scholarly
- Inspirational
- Practical
- Reflective
- Motivational
- Educational
- Historical
- Narrative

### PDF Result Format
- Professional Title
- Opening Praises
- Quranic Verses & Hadith
- Main Content
- Practical Advice
- Closing Prayers
- RTL Support for Arabic

## License

See [LICENSE](LICENSE) for details.
