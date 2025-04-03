from typing import Optional, Dict
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError
from config.settings import settings

from .base import BaseTranscriptionService, Context

class SpeechmaticsTranscriptionService(BaseTranscriptionService):
    """Speechmatics transcription service implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://asr.api.speechmatics.com/v2"
    
    @property
    def api_key(self) -> Optional[str]:
        if self._initial_api_key:
            return self._initial_api_key
        
        return settings.speechmatics_api_key
        
    async def transcribe(self, audio_path: str, ctx: Context) -> Optional[str]:
        """Implement Speechmatics transcription functionality"""
        if not self._check_api_key("Speechmatics", ctx):
            return None
            
        ctx.log("Using Speechmatics transcription...")
        
        try:
            settings = self._get_connection_settings()
            conf = self._get_transcription_config()
            
            with BatchClient(settings) as client:
                try:
                    job_id = client.submit_job(
                        audio=audio_path,
                        transcription_config=conf,
                    )
                    ctx.log(f'Task {job_id} submitted successfully, waiting for transcription result')
                    
                    transcript = client.wait_for_completion(job_id, transcription_format='txt')
                    ctx.log("Speechmatics transcription completed")
                    return transcript
                    
                except HTTPStatusError as e:
                    if e.response.status_code == 401:
                        ctx.log('Invalid API key - please check SPEECHMATICS_API_KEY!')
                    elif e.response.status_code == 400:
                        ctx.log(f'Request error: {e.response.json().get("detail", "")}')
                    else:
                        ctx.log(f'HTTP error: {e.response.status_code}')
                    return None
                    
        except Exception as e:
            ctx.log(f"Speechmatics transcription failed: {str(e)}")
            return None
            
    def _get_connection_settings(self) -> ConnectionSettings:
        return ConnectionSettings(
            url=self.base_url,
            auth_token=self.api_key,
        )
        
    def _get_transcription_config(self) -> Dict:
        return {
            "type": "transcription",
            "transcription_config": {
                "language": "auto"
            }
        } 