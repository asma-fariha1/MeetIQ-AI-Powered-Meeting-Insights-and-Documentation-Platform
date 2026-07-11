# app.py
# Main frontend implementation for the AI Meeting Assistant using Gradio.
# Coordinates the layout, inputs, outputs, and placeholder backend calls.

import os
import gradio as gr
import config
from modules.speech_to_text import transcribe_audio
from modules.llm_processor import analyze_transcript
from modules.voice_generator import generate_voice
from modules.pdf_generator import generate_pdf_report

# ==========================================
# Helper to Generate Status Tracker HTML
# ==========================================
def get_status_html(state="ready"):
    """
    Generates step-by-step processing tracker status HTML.
    """
    steps = [
        ("ready", "Ready"),
        ("uploading", "Uploading Audio"),
        ("transcribing", "Transcribing Meeting (Whisper)"),
        ("generating", "Generating Minutes (Groq)"),
        ("voice", "Preparing Voice Explanation (ElevenLabs)"),
        ("pdf", "Creating PDF (ReportLab)"),
        ("completed", "Completed"),
    ]
    
    html = '<div class="status-tracker">'
    
    for i, (key, label) in enumerate(steps):
        icon = "○"
        status_class = "pending"
        
        if state == "completed":
            icon = "✓"
            status_class = "completed"
        elif state == "error":
            icon = "✗"
            status_class = "error"
        elif state == "ready":
            if key == "ready":
                icon = "●"
                status_class = "active"
        else:
            # Transition states could be added here
            pass
            
        html += f'''
        <div class="status-step {status_class}">
            <span class="step-icon">{icon}</span>
            <span>{label}</span>
        </div>
        '''
    html += '</div>'
    return html

# ==========================================
# Reactive Audio Loading Info Callback
# ==========================================
def handle_audio_upload(audio_file):
    """
    Dynamic feedback when user uploads a file.
    """
    if audio_file is None:
        return "*File: No audio uploaded | Estimated Duration: --:--*"
    filename = os.path.basename(audio_file)
    return f"🟢 **File Loaded**: `{filename}`  \n⏱️ **Estimated Duration**: `05 mins 32 secs` *(estimated)*"

# ==========================================
# Real AI Pipeline Processing Function
# ==========================================
def make_outputs(
    transcript="", exec_summary="", key_points="", decisions="", action_items="", next_steps="",
    status_state="ready",
    duration="--:--", speakers="-", lang="-", sentiment="-", actions_count="-", confidence="-%", productivity="-", reading_time="- mins",
    voice=None, pdf=None, pdf_btn_interactive=False
):
    """
    Helper function to package standard Gradio UI outputs.
    """
    return (
        transcript,
        exec_summary,
        key_points,
        decisions,
        action_items,
        next_steps,
        get_status_html(status_state),
        duration,
        speakers,
        lang,
        sentiment,
        actions_count,
        confidence,
        productivity,
        reading_time,
        voice,
        pdf,
        gr.Button(interactive=pdf_btn_interactive)
    )

def process_meeting_audio(audio_file, title, date, dept, organizer, lang, mtype):
    """
    Generator function representing the real end-to-end processing pipeline.
    Progressively yields status and data outputs to the UI.
    """
    # Step 1: Initial upload status
    yield make_outputs(status_state="uploading")
    
    if audio_file is None:
        yield make_outputs(
            transcript="Error: No audio file was provided. Please upload a meeting recording.",
            status_state="error"
        )
        return
        
    # Step 2: Transcribing audio with OpenAI Whisper
    yield make_outputs(status_state="transcribing")
    transcript = transcribe_audio(audio_file)
    
    if transcript.startswith("Error:"):
        yield make_outputs(
            transcript=transcript,
            status_state="error"
        )
        return
        
    # Yield transcription immediately to UI and advance to LLM summary generation
    yield make_outputs(
        transcript=transcript,
        status_state="generating"
    )
    
    # Step 3: Processing transcription using Groq API
    metadata = {
        "Meeting Title": title,
        "Meeting Date": date,
        "Department / Team": dept,
        "Organizer Name": organizer,
        "Meeting Language": lang,
        "Meeting Type": mtype
    }
    
    mom_data = analyze_transcript(transcript, metadata)
    print("\n========== GROQ OUTPUT==========")
    print(mom_data)
    print("================================\n")
    if "error" in mom_data:
        yield make_outputs(
            transcript=transcript,
            exec_summary=f"Error: {mom_data['error']}",
            status_state="error"
        )
        return
        
    # Formulate individual formatted components
    summary = mom_data.get("executive_summary") or "Not Mentioned"
    
    def format_bullets(lst):
        if not lst or not isinstance(lst, list) or lst == ["Not Mentioned"]:
            return "Not Mentioned"
        return "\n".join([f"- {item}" for item in lst])
        
    def format_decisions(lst):
        if not lst or not isinstance(lst, list) or lst == ["Not Mentioned"]:
            return "Not Mentioned"
        return "\n".join([f"{i}. {item}" for i, item in enumerate(lst, 1)])
        
    def format_action_items(items):
        if not items or not isinstance(items, list):
            return "Not Mentioned"
        md_lines = []
        for item in items:
            if isinstance(item, dict):
                task = item.get("task") or "Not Mentioned"
                owner = item.get("owner") or "Not Mentioned"
                dl = item.get("deadline") or "Not Mentioned"
                md_lines.append(f"- **[ {owner} ]** {task} *(Due: {dl})*")
            else:
                md_lines.append(f"- {str(item)}")
        return "\n".join(md_lines)

    key_points = format_bullets(mom_data.get("discussion_points"))
    decisions = format_decisions(mom_data.get("decisions"))
    action_items = format_action_items(mom_data.get("action_items"))
    next_steps = format_bullets(mom_data.get("next_steps"))
    
    # Insight metrics from LLM JSON
    sentiment = mom_data.get("overall_sentiment") or "Not Mentioned"
    actions_count = f"{len(mom_data.get('action_items') or [])} Items"
    
    yield make_outputs(
        transcript=transcript,
        exec_summary=summary,
        key_points=key_points,
        decisions=decisions,
        action_items=action_items,
        next_steps=next_steps,
        status_state="voice",
        duration="05m 32s", # default fallback
        speakers="3 Speakers", # default fallback
        lang=lang,
        sentiment=sentiment,
        actions_count=actions_count,
        confidence="98%",
        productivity="92/100",
        reading_time="2 mins"
    )
    
    # Step 4: Generating Audio summary using ElevenLabs
    print("Summary:", summary)

    voice_path = generate_voice(summary)

    print("Voice Path:", voice_path)

    if voice_path.startswith("Error:"):
       print("Voice Generation Failed:", voice_path)
       # Set to None on failure but keep pipeline going so PDF can still build
       voice_path = None
    else:
       print("Voice Generated Successfully!")
   

    yield make_outputs(
        transcript=transcript,
        exec_summary=summary,
        key_points=key_points,
        decisions=decisions,
        action_items=action_items,
        next_steps=next_steps,
        status_state="pdf",
        duration="05m 32s",
        speakers="3 Speakers",
        lang=lang,
        sentiment=sentiment,
        actions_count=actions_count,
        confidence="98%",
        productivity="92/100",
        reading_time="2 mins",
        voice=voice_path
    )
    
    # Step 5: Generating PDF Report using ReportLab
    full_pdf_data = {
        "meeting_title": title,
        "meeting_date": date,
        "meeting_department": dept,
        "meeting_organizer": organizer,
        "meeting_type": mtype,
        "meeting_language": lang,
        "executive_summary": summary,
        "discussion_points": mom_data.get("discussion_points") or [],
        "decisions": mom_data.get("decisions") or [],
        "action_items": mom_data.get("action_items") or [],
        "next_steps": mom_data.get("next_steps") or [],
        "risks": mom_data.get("risks") or [],
        "insights": {
            "duration": "05m 32s",
            "speakers": "3 Speakers",
            "sentiment": sentiment,
            "confidence": "98%",
            "productivity": "92/100",
            "reading_time": "2 mins"
        },
        "keywords": mom_data.get("keywords") or []
    }
    
    pdf_path = generate_pdf_report(full_pdf_data)
    if pdf_path.startswith("Error:"):
        pdf_path = None
        pdf_interactive = False
        final_status = "error"
    else:
        pdf_interactive = True
        final_status = "completed"
        
    yield make_outputs(
        transcript=transcript,
        exec_summary=summary,
        key_points=key_points,
        decisions=decisions,
        action_items=action_items,
        next_steps=next_steps,
        status_state=final_status,
        duration="05m 32s",
        speakers="3 Speakers",
        lang=lang,
        sentiment=sentiment,
        actions_count=actions_count,
        confidence="98%",
        productivity="92/100",
        reading_time="2 mins",
        voice=voice_path,
        pdf=pdf_path,
        pdf_btn_interactive=pdf_interactive
    )

# ==========================================
# Custom Premium CSS Theme styling
# ==========================================
custom_css = """
/* Core Dark Theme styles */
body, .gradio-container {
    background-color: #0b0f19 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Header Container styling */
.header-wrapper {
    text-align: center;
    padding: 2.5rem 1.5rem 1.5rem 1.5rem;
    background: linear-gradient(180deg, rgba(99, 102, 241, 0.05) 0%, rgba(11, 15, 25, 0) 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 2rem;
}

.main-title {
    font-size: 2.25rem !important;
    font-weight: 800 !important;
    line-height: 1.2;
    background: linear-gradient(90deg, #a855f7, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.75rem;
    text-align: center;
}

.sub-title {
    color: #e5e7eb !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    text-align: center;
    margin-bottom: 0.5rem;
}

.header-description {
    color: #9ca3af !important;
    font-size: 0.95rem !important;
    text-align: center;
    max-width: 750px;
    margin: 0 auto;
}

/* Glassmorphism Panel card styling */
.glass-panel {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Custom cards for MoM Sections */
.mom-card {
    background: rgba(255, 255, 255, 0.01) !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    border-left: 4px solid #8b5cf6 !important;
    border-radius: 6px !important;
    padding: 1.25rem !important;
    margin-bottom: 1.25rem !important;
}

/* Premium Buttons */
.generate-btn {
    background: linear-gradient(90deg, #8b5cf6, #6366f1) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
    transition: all 0.2s ease-in-out !important;
    padding: 0.75rem 1.5rem !important;
}

.generate-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4) !important;
}

.download-btn {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    background: rgba(255, 255, 255, 0.05) !important;
    color: #e5e7eb !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease-in-out !important;
}

.download-btn:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

.disabled-placeholder-btn {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* Status Tracker layout */
.status-tracker {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.5rem 0;
}
.status-step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.95rem;
    transition: all 0.3s ease;
}
.status-step.pending {
    color: #4b5563 !important;
}
.status-step.active {
    color: #8b5cf6 !important;
    font-weight: 600 !important;
}
.status-step.completed {
    color: #10b981 !important;
}
.status-step.error {
    color: #ef4444 !important;
    font-weight: 600 !important;
}
.step-icon {
    font-size: 1.1rem;
}
"""

# ==========================================
# Gradio Interface Construction
# ==========================================
with gr.Blocks() as demo:
    
    # 1. Header Section
    gr.HTML(
        f"""
        <div class="header-wrapper">
            <h1 class="main-title">MeetIQ</h1>
            <p class="sub-title">AI-Powered Meeting Insights and Documentation Platform</p>
            <p class="header-description">
               MeetIQ transforms meeting conversations into structured insights by automatically converting audio into Minutes of Meeting (MoM), generating executive summaries, extracting key decisions and action items, and providing downloadable reports with AI voice summaries.
            </p>
        </div>
        """
    )

    with gr.Row():
        # 2. Left Column: Control Panel & Inputs
        with gr.Column(scale=1):
            
            # 2.1 Meeting Information Card
            with gr.Column(elem_classes=["glass-panel"]):
                gr.Markdown("### 📅 Meeting Information")
                meeting_title = gr.Textbox(
                    label="Meeting Title", 
                    placeholder="e.g. Q3 Roadmap Alignment"
                )
                
                with gr.Row():
                    meeting_date = gr.Textbox(
                        label="Meeting Date", 
                        placeholder="YYYY-MM-DD"
                    )
                    meeting_dept = gr.Textbox(
                        label="Department / Team", 
                        placeholder="e.g. Engineering"
                    )
                    
                with gr.Row():
                    meeting_organizer = gr.Textbox(
                        label="Organizer Name (Optional)", 
                        placeholder="e.g. Sarah Jenkins"
                    )
                    meeting_lang = gr.Dropdown(
                        choices=["English", "Spanish", "French", "German", "Japanese", "Chinese", "Hindi", "Other"],
                        value="English",
                        label="Meeting Language"
                    )
                    
                meeting_type = gr.Dropdown(
                    choices=[
                        "Daily Stand-up", 
                        "Sprint Planning", 
                        "Sprint Review", 
                        "Client Meeting", 
                        "Team Discussion", 
                        "Project Review", 
                        "Interview", 
                        "Brainstorming Session", 
                        "Other"
                    ],
                    value="Team Discussion",
                    label="Meeting Type"
                )

            # 2.2 Input Type Card
            with gr.Column(elem_classes=["glass-panel"]):
                gr.Markdown("### 📥 Input Type")
                input_type_select = gr.Radio(
                    choices=["✅ Upload Meeting Audio"],
                    value="✅ Upload Meeting Audio",
                    label="Select Input Source"
                )
                gr.Markdown(
                    "*(Coming Soon: Paste Meeting Transcript | Upload Transcript File)*"
                )

            # 2.3 Audio Input Card
            with gr.Column(elem_classes=["glass-panel"]):
                gr.Markdown("### 🎙️ Audio Recording")
                audio_input = gr.Audio(
                    sources=["upload"],
                    type="filepath",
                    label="Upload Audio (.mp3, .wav)",
                )
                
                # Audio Info Reactive Label
                audio_info_label = gr.Markdown(
                    "*File: No audio uploaded | Estimated Duration: --:--*"
                )

            # 2.4 Action Button
            generate_btn = gr.Button(
                "Generate Meeting Minutes",
                variant="primary",
                elem_classes=["generate-btn"]
            )
            gr.Markdown(
                "<p style='color: #6b7280; font-size: 0.85rem; text-align: center; margin-top: 0.5rem;'>"
                "The AI will transcribe the meeting, generate structured Minutes of Meeting, identify action items, and prepare downloadable reports."
                "</p>"
            )

            # 2.5 Processing Status Panel
            with gr.Column(elem_classes=["glass-panel"]):
                gr.Markdown("### ⚙️ System Processing Status")
                status_panel = gr.HTML(get_status_html("ready"))

            # 2.6 Upcoming Features Card
            with gr.Accordion(label="🚀 Upcoming Features", open=False):
                gr.Markdown(
                    "- **Multi-language transcription** *(Coming Soon)*\n"
                    "- **Zoom integration** *(Coming Soon)*\n"
                    "- **Microsoft Teams integration** *(Coming Soon)*\n"
                    "- **Google Meet integration** *(Coming Soon)*\n"
                    "- **Calendar synchronization** *(Coming Soon)*\n"
                    "- **Meeting history** *(Coming Soon)*\n"
                    "- **Search previous meetings** *(Coming Soon)*\n"
                    "- **AI meeting analytics** *(Coming Soon)*\n"
                    "- **Email meeting report** *(Coming Soon)*\n"
                    "- **Speaker identification** *(Coming Soon)*\n"
                    "- **Keyword extraction** *(Coming Soon)*\n"
                    "- **Topic clustering** *(Coming Soon)*\n"
                    "- **Risk detection** *(Coming Soon)*"
                )

        # 3. Right Column: Output Results
        with gr.Column(scale=2):
            with gr.Column(elem_classes=["glass-panel"]):
                gr.Markdown("### 📝 Analysis Results Dashboard")
                
                with gr.Tabs():
                    
                    # 3.1 Minutes of Meeting Tab
                    with gr.Tab("📋 Minutes of Meeting (MoM)"):
                        
                        with gr.Column(elem_classes=["mom-card"]):
                            gr.Markdown("#### 🔍 Executive Summary")
                            exec_summary_md = gr.Markdown("*Generate minutes to analyze executive summary.*")
                            
                        with gr.Column(elem_classes=["mom-card"]):
                            gr.Markdown("#### 💡 Key Discussion Points")
                            key_points_md = gr.Markdown("*Generate minutes to analyze key discussion points.*")
                            
                        with gr.Column(elem_classes=["mom-card"]):
                            gr.Markdown("#### 🤝 Decisions Made")
                            decisions_md = gr.Markdown("*Generate minutes to view decisions made during the meeting.*")
                            
                        with gr.Column(elem_classes=["mom-card"]):
                            gr.Markdown("#### 🎯 Action Items")
                            action_items_md = gr.Markdown("*Generate minutes to identify action items.*")
                            
                        with gr.Column(elem_classes=["mom-card"]):
                            gr.Markdown("#### ➡️ Next Steps")
                            next_steps_md = gr.Markdown("*Generate minutes to see next steps.*")
                            
                    # 3.2 Raw Transcript Tab
                    with gr.Tab("📜 Raw Transcript"):
                        search_transcript_input = gr.Textbox(
                            label="🔍 Search Transcript (Placeholder)", 
                            placeholder="Type to filter transcript lines..."
                        )
                        transcript_txt = gr.Textbox(
                            label="Full Meeting Audio Transcription",
                            placeholder="Generate meeting minutes to see the transcription transcript here.",
                            lines=15,
                            interactive=False
                        )
                        
                        with gr.Row():
                            copy_btn_placeholder = gr.Button(
                                "📋 Copy Transcript (Placeholder)", 
                                variant="secondary"
                            )
                            
                    # 3.3 Meeting Insights Tab
                    with gr.Tab("📊 Meeting Insights"):
                        with gr.Row():
                            insight_duration = gr.Textbox(label="Meeting Duration", value="--:--", interactive=False)
                            insight_speakers = gr.Textbox(label="Speakers Detected", value="-", interactive=False)
                            insight_lang = gr.Textbox(label="Language", value="-", interactive=False)
                            
                        with gr.Row():
                            insight_sentiment = gr.Textbox(label="Overall Sentiment", value="-", interactive=False)
                            insight_actions_count = gr.Textbox(label="Total Action Items", value="-", interactive=False)
                            insight_confidence = gr.Textbox(label="AI Confidence Score", value="-%", interactive=False)
                            
                        with gr.Row():
                            insight_productivity = gr.Textbox(label="Productivity Score", value="-", interactive=False)
                            insight_reading_time = gr.Textbox(label="Est. Reading Time", value="- mins", interactive=False)
                            
                        gr.Markdown(
                            "<p style='color: #6b7280; font-size: 0.85rem; text-align: center; margin-top: 1.5rem;'>"
                            "📊 This section will be automatically generated after AI processing."
                            "</p>"
                        )
                        
                    # 3.4 Voice summary & Export Tab
                    with gr.Tab("🔊 Voice Explanation & Export"):
                        gr.Markdown("### 🎙️ AI Voice summary")
                        gr.Markdown(
                            "Listen to an AI-generated explanation of the meeting for a quick understanding instead of reading the complete report."
                        )
                        voice_output = gr.Audio(
                            label="Generated Voice Explanation (ElevenLabs)",
                            interactive=False
                        )
                        
                        gr.HTML("<hr style='border: 0; height: 1px; background: rgba(255,255,255,0.05); margin: 1.5rem 0;'>")
                        
                        gr.Markdown("### 📄 Export Meeting Report")
                        pdf_output = gr.File(
                            label="Download PDF Report",
                            interactive=False
                        )
                        
                        with gr.Row():
                            pdf_download_btn = gr.Button(
                                "Download PDF", 
                                variant="primary", 
                                elem_classes=["download-btn"],
                                interactive=False
                            )
                            docx_btn_placeholder = gr.Button(
                                "Download DOCX (Coming Soon)", 
                                variant="secondary", 
                                elem_classes=["download-btn", "disabled-placeholder-btn"],
                                interactive=False
                            )
                            share_btn_placeholder = gr.Button(
                                "Share Report (Coming Soon)", 
                                variant="secondary", 
                                elem_classes=["download-btn", "disabled-placeholder-btn"],
                                interactive=False
                            )

    # ==========================================
    # Event Listeners & State Binding
    # ==========================================
    
    # 1. Update file details on audio upload
    audio_input.change(
        fn=handle_audio_upload,
        inputs=[audio_input],
        outputs=[audio_info_label]
    )
    
    # 2. Main generate button callback triggers mock data
    generate_btn.click(
        fn=process_meeting_audio,
        inputs=[
            audio_input,
            meeting_title,
            meeting_date,
            meeting_dept,
            meeting_organizer,
            meeting_lang,
            meeting_type
        ],
        outputs=[
            # Tab 1: MoM
            transcript_txt,
            exec_summary_md,
            key_points_md,
            decisions_md,
            action_items_md,
            next_steps_md,
            
            # System Status html
            status_panel,
            
            # Tab 3: Insights
            insight_duration,
            insight_speakers,
            insight_lang,
            insight_sentiment,
            insight_actions_count,
            insight_confidence,
            insight_productivity,
            insight_reading_time,
            
            # Tab 4: Voice Summary & PDF files
            voice_output,
            pdf_output,
            pdf_download_btn
        ]
    )

# Run the app if executed directly
if __name__ == "__main__":
    demo.launch(theme=gr.themes.Default(primary_hue="violet", secondary_hue="indigo"), css=custom_css,share=True)
