# modules/voice_generator.py
# Voice Generator module using ElevenLabs API.
# Converts meeting summaries into natural-sounding speech audio files.

import os
import time
import requests
import config

def generate_voice(
    summary_text: str, 
    voice_id: str = None, 
    model_id: str = None, 
    output_filename: str = None
) -> str:
    """
    Converts plain text summary into an MP3 audio file using ElevenLabs API.
    
    Args:
        summary_text (str): The plain text summary to convert.
        voice_id (str, optional): ElevenLabs voice ID. Defaults to config settings.
        model_id (str, optional): ElevenLabs model ID. Defaults to 'eleven_multilingual_v2'.
        output_filename (str, optional): Custom filename for the output file.
        
    Returns:
        str: Absolute or relative local path to the generated MP3 file, or a user-friendly error message.
    """
    # 1. Input validations
    if not summary_text or not summary_text.strip():
        return "Error: Input text for voice generation is empty."
        
    api_key = config.ELEVENLABS_API_KEY
    if not api_key:
        return "Error: ElevenLabs API Key is missing. Please configure ELEVENLABS_API_KEY in the .env file."
        
    # Retrieve configuration and default values
    v_id = voice_id or config.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"
    m_id = model_id or getattr(config, 'ELEVENLABS_MODEL', 'eleven_multilingual_v2')
    
    # 2. Setup output directories
    # Combine root outputs directory with 'audio' subdirectory
    output_dir = os.path.join(config.OUTPUT_DIR, "audio")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    if not output_filename:
        # Prevent file overwrite collision using timestamp suffixes
        timestamp = int(time.time())
        output_filename = f"voice_summary_{timestamp}.mp3"
        
    output_path = os.path.join(output_dir, output_filename)
    
    # 3. Prepare API Call parameters
    # Using the direct ElevenLabs REST endpoint for stable, version-independent network requests
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{v_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    payload = {
        "text": summary_text,
        "model_id": m_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    # 4. Invoke API and process response stream
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Check HTTP response codes and translate to clean messages
        if response.status_code == 401:
            return "Error: Unauthorized access. Please check if your ElevenLabs API Key is valid."
        elif response.status_code == 429:
            return "Error: ElevenLabs rate limit exceeded or quota exhausted."
        elif response.status_code != 200:
            return f"Error: ElevenLabs API returned status code {response.status_code}. Details: {response.text}"
            
        # 5. Write file content to disk
        with open(output_path, "wb") as f:
            f.write(response.content)
            
        return output_path
        
    except requests.exceptions.RequestException as re:
        return f"Error: Network communication failed during TTS generation. Details: {str(re)}"
    except Exception as e:
        return f"Error: Unable to save generated audio. Details: {str(e)}"

# ==========================================
# Testing / Example Block
# ==========================================
if __name__ == "__main__":
    print("====================================================")
    print("Voice Generator Module - Offline Testing")
    print("====================================================")
    
    test_text = "Hello! This is a voice summary demonstration from the AI Meeting Assistant."
    
    print("\n[Test 1] Testing empty text error handler:")
    print(generate_voice(""))
    
    print("\n[Test 2] To test the ElevenLabs API, ensure ELEVENLABS_API_KEY is configured in the .env file.")
    if config.ELEVENLABS_API_KEY:
        print("API Key detected. Calling ElevenLabs API...")
        result_path = generate_voice(test_text)
        print(f"Result: {result_path}")
    else:
        print("API Key not found. Skipping live API test call.")
