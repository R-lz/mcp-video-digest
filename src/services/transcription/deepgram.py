import os
import requests
from typing import Optional, Dict, Any

from .base import BaseTranscriptionService, Context

class DeepgramTranscriptionService(BaseTranscriptionService):
    """Deepgram transcription service implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.deepgram.com/v1/listen"
        
    async def transcribe(self, audio_path: str, ctx: Context) -> Optional[str]:
        if not self._check_api_key("Deepgram", ctx):
            return None
            
        ctx.log("Using Deepgram transcription...")
        
        try:
            with open(audio_path, "rb") as audio:
                audio_data = audio.read()
            
            url = self._build_url()
            headers = self._build_headers(audio_path)
            
            response = requests.post(
                url,
                headers=headers,
                data=audio_data
            )
            
            if response.status_code != 200:
                ctx.log(f"Deepgram request failed: {response.status_code} - {response.text}")
                return None
                
            return self._process_response(response.json(), ctx)
            
        except Exception as e:
            ctx.log(f"Deepgram transcription failed: {str(e)}")
            return None
            
    def _build_url(self) -> str:
        """Build request URL"""
        params = {
            "smart_format": "true",
            "model": "nova-2",
            "language": "zh-CN",
            "diarize": "true",
            "punctuate": "true"
        }
        param_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}?{param_string}"
        
    def _build_headers(self, audio_path: str) -> Dict[str, str]:
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "audio/mp4" if audio_path.endswith('.mp4') else "audio/wav"
        }
        
    def _process_response(self, result: Dict[str, Any], ctx: Context) -> Optional[str]:
        if "results" not in result or "channels" not in result["results"]:
            ctx.log("Deepgram returned result format exception")
            return None
            
        channel = result["results"]["channels"][0]
        
        if "speaker" in channel["alternatives"][0]:
            segments = []
            for alternative in channel["alternatives"][0]["words"]:
                speaker = alternative.get("speaker", "Unknown")
                text = alternative.get("word", "")
                if not segments or segments[-1]["speaker"] != speaker:
                    segments.append({"speaker": speaker, "text": [text]})
                else:
                    segments[-1]["text"].append(text)
            
            result_text = "\n".join([
                f"Speaker {seg['speaker']}: {''.join(seg['text'])}"
                for seg in segments
            ])
        else:
            result_text = channel["alternatives"][0]["transcript"]
        
        ctx.log("Deepgram transcription completed")
        return result_text 