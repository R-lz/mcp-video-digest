import os
import requests
import asyncio
from typing import Optional, Dict

from .base import BaseTranscriptionService, Context

class GladiaTranscriptionService(BaseTranscriptionService):
    """Gladia transcription service implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.gladia.io/v2"
        
    async def transcribe(self, audio_path: str, ctx: Context) -> Optional[str]:
        if not self._check_api_key("Gladia", ctx):
            return None
            
        ctx.log("Using Gladia transcription...")
        
        try:
            audio_url = await self._upload_file(audio_path, ctx)
            if not audio_url:
                return None
                
            result_url = await self._request_transcription(audio_url, ctx)
            if not result_url:
                return None
                
            return await self._get_transcription_result(result_url, ctx)
            
        except Exception as e:
            ctx.log(f"Gladia transcription failed: {str(e)}")
            return None
            
    async def _upload_file(self, audio_path: str, ctx: Context) -> Optional[str]:
        upload_url = f"{self.base_url}/upload"
        headers = self._get_headers()
        
        with open(audio_path, "rb") as audio:
            files = {
                "audio": (
                    os.path.basename(audio_path),
                    audio,
                    "audio/mp4" if audio_path.endswith('.mp4') else "audio/wav"
                )
            }
            response = requests.post(upload_url, headers=headers, files=files)
            
            if response.status_code != 200:
                ctx.log(f"Upload failed: {response.status_code} - {response.text}")
                return None
                
            result = response.json()
            audio_url = result.get("audio_url")
            if not audio_url:
                ctx.log("No audio_url found in upload response")
                return None
                
            return audio_url
            
    async def _request_transcription(self, audio_url: str, ctx: Context) -> Optional[str]:
        transcribe_url = f"{self.base_url}/pre-recorded"
        headers = {**self._get_headers(), "Content-Type": "application/json"}
        
        data = {
            "audio_url": audio_url,
            "detect_language": True,
            "diarization": True,
            "language": "auto",
            "punctuation_enhanced": True
        }
        
        response = requests.post(transcribe_url, headers=headers, json=data)
        
        if response.status_code not in [200, 201]:
            ctx.log(f"Transcription request failed: {response.status_code} - {response.text}")
            return None
            
        result = response.json()
        result_url = result.get("result_url")
        
        if not result_url:
            ctx.log("No result URL found")
            return None
            
        return result_url
        
    async def _get_transcription_result(self, result_url: str, ctx: Context) -> Optional[str]:
        """Get transcription result"""
        headers = self._get_headers()
        max_retries = 30
        
        for _ in range(max_retries):
            response = requests.get(result_url, headers=headers)
            
            if response.status_code != 200:
                ctx.log(f"Get result failed: {response.status_code} - {response.text}")
                return None
                
            result = response.json()
            status = result.get("status")
            
            if status == "done":
                transcription = result.get("result", {}).get("transcription", {})
                utterances = transcription.get("utterances", [])
                if utterances:
                    text = " ".join(u.get("text", "") for u in utterances)
                    ctx.log("Gladia transcription completed")
                    return text
                else:
                    ctx.log("No text content found in transcription result")
                    return None
            elif status == "error":
                ctx.log(f"Transcription failed: {result.get('error', 'Unknown error')}")
                return None
            elif status == "processing":
                ctx.log("Processing...")
                
            await asyncio.sleep(10)
            
        ctx.log("Transcription timeout")
        return None
        
    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-gladia-key": self.api_key,
            "Accept": "application/json"
        } 