# 🎙️ MeetIQ — AI-Powered Meeting Insights & Documentation Platform

### Turn raw meeting audio into structured Minutes of Meeting, voice summaries, and polished PDF reports — automatically.

![Python](https://img.shields.io/badge/Python-100%25-blue?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange?logo=gradio&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq%20(Llama%203)-purple)
![Whisper](https://img.shields.io/badge/STT-OpenAI%20Whisper-black)
![ElevenLabs](https://img.shields.io/badge/TTS-ElevenLabs-black)
![ReportLab](https://img.shields.io/badge/PDF-ReportLab-red)
![License](https://img.shields.io/badge/License-MIT-green)

> Nobody re-reads a 45-minute meeting recording to find out what was decided. MeetIQ listens to it for you — then hands back a clean summary, action items, a spoken recap, and a shareable PDF report.

---

## 💡 Why This Project Exists

Meetings generate decisions, but those decisions live and die in someone's memory (or get lost entirely) unless someone manually writes minutes afterward. MeetIQ automates that entire workflow — **transcription → analysis → documentation → voice recap** — turning a raw audio file into artifacts a team can actually act on and archive.

---

## ✨ What It Can Do

| Capability | Description |
|---|---|
| 🎧 **Speech-to-Text** | Transcribes meeting audio into accurate text using OpenAI Whisper |
| 🧠 **AI-Powered Analysis** | Groq's LLM (Llama 3) processes the transcript to extract summaries, key discussion points, and action items |
| 🗣️ **Voice Summaries** | Generates a natural-sounding spoken recap of the meeting using ElevenLabs TTS |
| 📄 **PDF Report Generation** | Compiles everything into a styled, downloadable PDF (Minutes of Meeting) via ReportLab |
| 🖥️ **Simple Web Interface** | A Gradio UI ties the whole pipeline together — upload audio, get insights back, no manual note-taking |

---

## 🏗️ How It Works

```
🎧 Meeting Audio
        │
        ▼
📝 Speech-to-Text  ───────────────▶  OpenAI Whisper transcribes the recording
        │
        ▼
🧠 LLM Processing  ───────────────▶  Groq API (Llama 3) summarizes, extracts
        │                            key points & action items
        ▼
🗣️ Voice Generation ─────────────▶  ElevenLabs converts the summary to speech
        │
        ▼
📄 PDF Report ───────────────────▶  ReportLab builds a styled Minutes-of-Meeting doc
        │
        ▼
🖥️ Delivered through the Gradio web interface
```

Each stage lives in its own module — clean separation between transcription, reasoning, voice generation, and reporting — so the pipeline is easy to extend (swap models, add integrations, etc.) without touching unrelated code.

---

## 🛠️ Tech Stack

- **Language:** Python
- **User Interface:** [Gradio](https://github.com/gradio-app/gradio)
- **LLM Processing:** [Groq API](https://github.com/groq/groq-python) (Llama 3 models) — summarization & action-item extraction
- **Speech-to-Text:** [OpenAI Whisper](https://github.com/openai/whisper)
- **Text-to-Speech:** [ElevenLabs](https://github.com/elevenlabs/elevenlabs-python)
- **PDF Report Generation:** [ReportLab](https://www.reportlab.com/)

---

## 📂 Project Structure

```
MeetIQ/
├── app.py                    # Main application coordinator (Gradio UI)
├── config.py                 # Settings & environment configuration
├── modules/
│   ├── speech_to_text.py     # Whisper transcription logic
│   ├── llm_processor.py      # Groq API analysis (summarization & action items)
│   ├── voice_generator.py    # ElevenLabs TTS rendering
│   └── pdf_generator.py      # ReportLab styled PDF report builder
├── utils/
│   └── helpers.py            # Utility & helper functions
├── outputs/                  # Generated PDF/audio outputs
├── assets/sample_audio/      # Demo & test audio files
├── requirements.txt          # Python dependencies
├── .env.example               # Environment variables template
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/asma-fariha1/MeetIQ-AI-Powered-Meeting-Insights-and-Documentation-Platform.git
cd MeetIQ-AI-Powered-Meeting-Insights-and-Documentation-Platform
```

### 2. Configure environment
Create `.env` and add your API credentials (Groq, ElevenLabs)

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the assistant
```bash
python app.py
```

Open the local Gradio URL, upload a meeting recording (or try one from `assets/sample_audio/`), and get back a summary, voice recap, and PDF report.

---

## 🎯 What This Project Demonstrates

For anyone reviewing this repo — here's the skill set behind it:

- Building **modular, production-style pipelines** (STT → LLM → TTS → document generation) instead of a single monolithic script
- Integrating **multiple AI APIs** (Groq, Whisper, ElevenLabs) into one coherent workflow
- Working with **LLMs for structured extraction** — turning unstructured speech into summaries and actionable items
- Programmatic **document generation** (styled PDFs via ReportLab)
- Shipping a usable, **interactive product** (Gradio) rather than just notebook code
- Managing configuration and secrets cleanly via `.env` / `config.py`

---

## 📬 Let's Connect

If you're a recruiter, hiring manager, or fellow developer and this project interests you, I'd be happy to discuss the ideas behind it, the design decisions I made, what I learned while building it, and how I plan to improve it in the future. I'd love to connect and hear your feedback.


**Asma Fariha** — [GitHub](https://github.com/asma-fariha1)
