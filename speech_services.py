from abc import ABC, abstractmethod
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

class SpeechService(ABC):
    @abstractmethod
    def synthesize_speech_from_text(self, text: str, filename: str):
        pass

class OpenAISpeechService(SpeechService):
    def __init__(self, voice: str, instructions: str = ""):
        from openai import OpenAI
        self.client = OpenAI()
        self.voice = voice
        self.instructions = instructions

    def synthesize_speech_from_text(self, text: str, filename: str):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=self.voice,
            input=text,
            instructions=self.instructions
        )
        return response.read()
        
class GoogleSpeechService(SpeechService):
    def __init__(self, voice_name: str):
        from google.cloud import texttospeech
        self.client = texttospeech.TextToSpeechClient()
        self.voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

    def synthesize_speech_from_text(self, text: str, filename: str):
        from google.cloud import texttospeech
        input_text = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=input_text,
            voice=self.voice_params,
            audio_config=self.audio_config
        )
        return response.audio_content

class AzureSpeechService(SpeechService):
    def __init__(self, voice_name: str):
        import azure.cognitiveservices.speech as speechsdk
        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("SPEECH_KEY"),
            region=os.environ.get("SPEECH_REGION")
        )
        speech_config.speech_synthesis_voice_name = voice_name
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
        self.synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, 
            audio_config=None
        )

    def synthesize_speech_from_text(self, text: str):
        result = self.synthesizer.speak_text_async(text).get()
        if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        else:
            raise RuntimeError(f"Text synthesis failed: {result.reason}")

    def synthesize_speech_from_ssml(self, ssml: str):
        result = self.synthesizer.speak_ssml_async(ssml).get()
        if result.reason == self.speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        else:
            raise RuntimeError(f"SSML synthesis failed: {result.reason}")