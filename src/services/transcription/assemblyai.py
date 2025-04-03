import requests
import asyncio
from typing import Optional, Dict, List

from .base import BaseTranscriptionService, Context

class AssemblyAITranscriptionService(BaseTranscriptionService):
    """AssemblyAI transcription service implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.assemblyai.com/v2"
        
    async def transcribe(self, audio_path: str, ctx: Context) -> Optional[str]:
        """Implement AssemblyAI transcription functionality"""
        if not self._check_api_key("AssemblyAI", ctx):
            return None
            
        ctx.log("Using AssemblyAI transcription...")
        
        try:
            # Upload file
            upload_url = await self._upload_file(audio_path, ctx)
            if not upload_url:
                return None
                
            transcript_id = await self._request_transcription(upload_url, ctx)
            if not transcript_id:
                return None
                
            return await self._get_transcription_result(transcript_id, ctx)
            
        except Exception as e:
            ctx.log(f"AssemblyAI transcription failed: {str(e)}")
            return None
            
    async def _upload_file(self, audio_path: str, ctx: Context) -> Optional[str]:
        """Upload file to AssemblyAI"""
        headers = self._get_headers()
        
        with open(audio_path, "rb") as audio:
            response = requests.post(
                f"{self.base_url}/upload",
                headers=headers,
                data=audio
            )
            response.raise_for_status()
            upload_url = response.json()["upload_url"]
            ctx.log("File uploaded successfully")
            return upload_url
            
    async def _request_transcription(self, upload_url: str, ctx: Context) -> Optional[str]:
        headers = self._get_headers()
        data = {
            "audio_url": upload_url,
            "speaker_labels": True,  
            "language_code": "zh" 
        }
        
        response = requests.post(
            f"{self.base_url}/transcript",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        transcript_id = response.json()["id"]
        return transcript_id
        
    async def _get_transcription_result(self, transcript_id: str, ctx: Context) -> Optional[str]:
        """Get transcription result"""
        headers = self._get_headers()
        polling_endpoint = f"{self.base_url}/transcript/{transcript_id}"
        
        while True:
            response = requests.get(polling_endpoint, headers=headers)
            response.raise_for_status()
            transcript = response.json()
            
            if transcript["status"] == "completed":
                if "utterances" in transcript and transcript["utterances"]:
                    segments = []
                    for utterance in transcript["utterances"]:
                        speaker = utterance.get("speaker", "Unknown")
                        text = utterance.get("text", "")
                        segments.append(f"Speaker {speaker}: {text}")
                    result = "\n".join(segments)
                else:
                    result = transcript.get("text", "")
                
                ctx.log("AssemblyAI transcription completed")
                return result
                
            elif transcript["status"] == "error":
                error_msg = transcript.get("error", "Unknown error")
                ctx.log(f"AssemblyAI transcription failed: {error_msg}")
                return None
                
            await asyncio.sleep(3)
            
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "authorization": self.api_key
        } 