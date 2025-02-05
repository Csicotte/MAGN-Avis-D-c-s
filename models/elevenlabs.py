# models/elevenlabs_api.py

import os
import uuid
import tempfile
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import streamlit as st

class ElevenLabsAPI:
    VOICES = {
        "Matilda": "XrExE9yKIg1WjnnlVkGX",
        "George": "JBFqnCBsd6RMkjVDRZzb"
    }

    def __init__(self, api_key):
        self.client = ElevenLabs(api_key=api_key)
        # Create temporary directory instead of fixed audio_files
        self.temp_dir = tempfile.mkdtemp()

    def text_to_speech_stream(self, text: str, voice_id: str, language_code: str = "fr") -> str:
        """Convert text to speech and save to file"""
        try:
             # Generate unique filename in temp directory
            filename = os.path.join(self.temp_dir, f"audio_{uuid.uuid4()}.mp3")
            
            # Get the audio stream
            audio_stream = self.client.text_to_speech.convert(
                voice_id=voice_id,
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=1.0,
                    similarity_boost=1.0,
                    style=1.0,
                    use_speaker_boost=True,
                ),
            )
            
            # Write to temporary file
            with open(filename, 'wb') as f:
                for chunk in audio_stream:
                    if chunk:
                        f.write(chunk)
            
            return filename
            
        except Exception as e:
            st.error(f"Error generating audio: {str(e)}")
            return None