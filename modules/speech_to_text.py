# modules/speech_to_text.py
# Speech-to-Text module using OpenAI Whisper.
# This module converts audio recordings (.mp3, .wav) into plain text.

import os
import whisper

# Global variable to cache the loaded Whisper model (lazy loading)
_whisper_model = None

def get_model(model_name: str = "base") -> whisper.Whisper:
    """
    Loads and caches the Whisper model to avoid reloading overhead on subsequent runs.
    
    Args:
        model_name (str): Size of the Whisper model to load ('tiny', 'base', 'small', etc.)
        
    Returns:
        whisper.Whisper: The loaded Whisper model instance.
    """
    global _whisper_model
    if _whisper_model is None:
        # Load Whisper model; 'base' offers a good balance between processing speed and accuracy.
        _whisper_model = whisper.load_model(model_name)
    return _whisper_model

def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    """
    Transcribes an audio file into plain text transcript using OpenAI Whisper.
    
    Args:
        audio_path (str): The local system path to the audio file (.mp3 or .wav).
        model_name (str): The Whisper model size. Defaults to 'base'.
        
    Returns:
        str: Plain text transcript on success, or a user-friendly error message string on failure.
    """
    # 1. Verify file existence
    if not os.path.exists(audio_path):
        return f"Error: The audio file was not found at the path: '{audio_path}'."
        
    # 2. Check for empty audio files
    try:
        if os.path.getsize(audio_path) == 0:
            return "Error: The uploaded audio file is empty (0 bytes)."
    except Exception as e:
        return f"Error: Unable to verify file attributes. Details: {str(e)}"
        
    # 3. Check for supported audio file extension (.mp3, .wav)
    _, ext = os.path.splitext(audio_path)
    ext = ext.lower()
    if ext not in [".mp3", ".wav"]:
        return f"Error: Unsupported format '{ext}'. Please upload either an MP3 or WAV file."
        
    # 4. Attempt Whisper transcription
    try:
        # Retrieve the cached model
        model = get_model(model_name)
        
        # Transcribe the audio file.
        # Setting fp16=False prevents CPU compilation warnings on systems without CUDA support.
        result = model.transcribe(audio_path, fp16=False)
        
        # Extract transcribed text
        transcript = result.get("text", "").strip()
        
        # Guard against silent audio files returning empty strings
        if not transcript:
            return "Warning: Transcription completed, but no speech was detected in the audio file."
            
        return transcript
        
    except Exception as e:
        # Return a user-friendly error description instead of raising technical exceptions
        return f"Error: Failed to process the audio file. The file may be corrupted or in an invalid format. Details: {str(e)}"

# ==========================================
# Testing / Example Block
# ==========================================
if __name__ == "__main__":
    # This block shows how to invoke this module programmatically, independent of Gradio.
    import tempfile
    
    print("====================================================")
    # Testing mock error states to verify clean error handling
    print("Speech-to-Text Module - Error Handling Test Suite")
    print("====================================================")
    
    # Test 1: File not found
    print("\n[Test 1] Testing missing file handling:")
    print(transcribe_audio("non_existent_file.wav"))
    
    # Test 2: Unsupported file format
    print("\n[Test 2] Testing unsupported file extension handling:")
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_txt:
        temp_txt.write(b"Mock transcript text content")
        temp_txt_path = temp_txt.name
    try:
        print(transcribe_audio(temp_txt_path))
    finally:
        os.remove(temp_txt_path)
        
    # Test 3: Empty audio file
    print("\n[Test 3] Testing empty audio file handling:")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_empty:
        temp_empty_path = temp_empty.name
    try:
        print(transcribe_audio(temp_empty_path))
    finally:
        os.remove(temp_empty_path)

    print("\n[Status] Test suite finished. Call transcribe_audio(file_path) to start transcription.")
