<<<<<<< HEAD
# AI Meeting Assistant

An AI-powered application to streamline meeting workflows by transcribing meeting audio, analyzing transcripts using Groq LLMs, generating voice-narrated summaries with ElevenLabs, and creating styled PDF reports.

## Tech Stack

- **User Interface**: [Gradio](https://github.com/gradio-app/gradio)
- **LLM Processing**: [Groq API](https://github.com/groq/groq-python) (using models like Llama 3)
- **Speech-to-Text**: [OpenAI Whisper](https://github.com/openai/whisper)
- **Text-to-Speech**: [ElevenLabs](https://github.com/elevenlabs/elevenlabs-python)
- **PDF Report Generation**: [ReportLab](https://www.reportlab.com/)

## Project Structure

```text
AI-Meeting-Assistant/
├── app.py                # Main application coordinator (Gradio UI interface)
├── config.py             # Settings and environment configuration
├── modules/
│   ├── speech_to_text.py  # OpenAI Whisper transcription logic
│   ├── llm_processor.py   # Groq API analysis (summarization & action items)
│   ├── voice_generator.py # ElevenLabs TTS rendering
│   └── pdf_generator.py   # ReportLab styled PDF report builder
├── utils/
│   └── helpers.py         # Utility and helper functions
├── outputs/              # Directory for generated PDF/audio outputs
├── assets/
│   └── sample_audio/     # Directory for demo and test audio files
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusion rules
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AI-Meeting-Assistant
   ```

2. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your API credentials:
   ```bash
   cp .env.example .env
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the assistant**:
   ```bash
   python app.py
   ```
=======
# MeetIQ-AI-Powered-Meeting-Insights-and-Documentation-Platform
AI-powered platform that transforms meeting recordings into structured meeting insights, Minutes of Meeting (MoM), voice summaries, and downloadable PDF reports.
>>>>>>> 58856216d8d96e646e97e62108519fa394e28c6e
