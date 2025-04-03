from abc import ABC, abstractmethod
from typing import Optional, Protocol
from config.settings import settings

class Context(Protocol):
    def log(self, message: str) -> None:
        ...

class BaseTranscriptionService(ABC):
    """Base class for transcription services"""
    
    def __init__(self, api_key: Optional[str] = None):
        self._initial_api_key = api_key
        
    @property
    def api_key(self) -> Optional[str]:
        return self._initial_api_key
        
    @abstractmethod
    async def transcribe(self, audio_path: str, ctx: Context) -> Optional[str]:
        """
        Transcribe audio file
        
        """
        pass
        
    def _check_api_key(self, service_name: str, ctx: Context) -> bool:
        """Check if API key exists"""
        if not self.api_key:
            ctx.log(f"{service_name} API key is empty, skipping")
            return False
        return True 