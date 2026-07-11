# modules/llm_processor.py
# LLM Processor module using the Groq API.
# This module converts meeting transcripts into structured Minutes of Meeting (MoM) in JSON format.

import os
import json
import config
from groq import Groq

# ==========================================
# System Prompt Definition
# ==========================================
SYSTEM_PROMPT = """You are an experienced Corporate Meeting Secretary.
Your job is to analyze the provided meeting transcript and convert it into structured, professional Minutes of Meeting (MoM).

You must adhere to the following rules:
1. Write in a formal, professional corporate tone.
2. Never invent or assume facts. Only extract information directly stated or clearly implied in the transcript.
3. If any field or specific detail (such as a task owner, deadline, or decision) is missing or not discussed in the transcript, set its value to "Not Mentioned".
4. Ensure the output is a valid JSON object matching the requested schema exactly.

You must return a JSON object with this exact structure:
{
    "meeting_title": "String representing the main topic discussed, or 'Not Mentioned'",
    "executive_summary": "A concise paragraph summarizing the purpose, key highlights, and main outcome of the meeting.",
    "discussion_points": ["Point 1 discussed", "Point 2 discussed", ...],
    "decisions": ["Decision 1 made", "Decision 2 made", ...],
    "action_items": [
        {
            "task": "Description of the task assigned",
            "owner": "Name of the person/team responsible, or 'Not Mentioned'",
            "deadline": "Time-frame, deadline date, or 'Not Mentioned'"
        }
    ],
    "next_steps": ["Next step 1", "Next step 2", ...],
    "risks": ["Identified risk, challenge, or bottleneck, or 'Not Mentioned'", ...],
    "overall_sentiment": "Overall tone of the meeting (e.g. Collaborative, Tense, Positive, Neutral)",
    "keywords": ["keyword1", "keyword2", ...]
}
"""

def analyze_transcript(transcript_text: str, meeting_metadata: dict = None) -> dict:
    """
    Analyzes raw meeting transcript using Groq API to extract minutes of meeting.
    
    Args:
        transcript_text (str): The raw speech-to-text transcript.
        meeting_metadata (dict, optional): Contextual metadata (e.g. title, date, type) to guide the LLM.
        
    Returns:
        dict: A dictionary containing structured meeting minutes or an error dictionary.
    """
    # 1. Check for empty transcript input
    if not transcript_text or not transcript_text.strip():
        return {
            "error": "Input transcript is empty. Please provide a transcript to analyze."
        }
        
    # 2. Check for API key existence
    if not config.GROQ_API_KEY:
        return {
            "error": "Groq API key is missing. Please set GROQ_API_KEY in the .env configuration file."
        }
        
    try:
        # Initialize Groq client
        client = Groq(api_key=config.GROQ_API_KEY)
        
        # Build user prompt with optional metadata context
        user_content = ""
        if meeting_metadata:
            user_content += "--- Meeting Context ---\n"
            for key, val in meeting_metadata.items():
                if val:
                    user_content += f"{key}: {val}\n"
            user_content += "-----------------------\n\n"
            
        user_content += f"--- Meeting Transcript ---\n{transcript_text}\n--------------------------"
        
        # 3. Request LLM Completion using JSON Mode
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            model=config.GROQ_MODEL,
            temperature=0.2, # Low temperature for high factual consistency
            response_format={"type": "json_object"} # Force valid JSON response
        )
        
        raw_response = response.choices[0].message.content
        
        # 4. Parse JSON output
        parsed_data = json.loads(raw_response)
        return parsed_data
        
    except json.JSONDecodeError as jde:
        return {
            "error": f"Failed to parse model response as JSON. Details: {str(jde)}",
            "raw_response": raw_response if 'raw_response' in locals() else None
        }
    except Exception as e:
        return {
            "error": f"Groq API call failed. Details: {str(e)}"
        }

# ==========================================
# Testing / Example Block
# ==========================================
if __name__ == "__main__":
    print("====================================================")
    print("LLM Processor Module - Offline Testing")
    print("====================================================")
    
    # Example transcript for local testing
    test_transcript = (
        "Alice: Thanks for joining. Let's finalize the launch date for Project Alpha. We need to go live by August 15th.\n"
        "Bob: That's doable, but we need to complete the security audits. I can handle the security audit by July 30th.\n"
        "Alice: Great. Let's make sure the marketing campaign kicks off on August 1st. Charlie, can you confirm the budget?\n"
        "Charlie: Yes, the budget is approved. However, we have a risk of server bottleneck if traffic spikes 5x.\n"
        "Alice: Okay, Bob, let's schedule load tests as next steps. The overall mood is good, let's do this!"
    )
    
    test_metadata = {
        "Meeting Title": "Project Alpha Launch Coordination",
        "Date": "2026-07-03",
        "Team": "Launch Committee",
        "Meeting Type": "Project Review"
    }
    
    print("\n[Test 1] Testing empty transcript validation:")
    print(json.dumps(analyze_transcript(""), indent=2))
    
    print("\n[Test 2] To test the Groq API call, ensure your GROQ_API_KEY is configured in the .env file.")
    if config.GROQ_API_KEY:
        print("API Key detected. Calling Groq API...")
        result = analyze_transcript(test_transcript, test_metadata)
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
    else:
        print("API Key not found. Skipping live API test call.")
