import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

class Settings:
    """Application settings"""
    
    def __init__(self):
        # Get the project root directory
        self.root_dir = Path(__file__).parent.parent.absolute()
        
        # Load environment variables
        env_path = self.root_dir / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Environment variables loaded: {env_path}")
        else:
            print(f"Warning: Environment variables file not found: {env_path}")
        
        # API Keys
        self.speechmatics_api_key: Optional[str] = os.getenv("SPEECHMATICS_API_KEY")
        self.gladia_api_key: Optional[str] = os.getenv("GLADIA_API_KEY")
        self.assemblyai_api_key: Optional[str] = os.getenv("ASSEMBLYAI_API_KEY")
        self.deepgram_api_key: Optional[str] = os.getenv("DEEPGRAM_API_KEY")
        
        # Temporary file configuration
        self.temp_dir: str = str(self.root_dir / "temp")
        self.cleanup_temp: bool = True
        
    def ensure_temp_dir(self):
        """Ensure the temporary directory exists"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            print(f"Temporary directory created: {self.temp_dir}")
            
    def has_valid_service(self) -> bool:
        """Check if there is a valid transcription service"""
        return any([
            self.speechmatics_api_key,
            self.gladia_api_key,
            self.assemblyai_api_key,
            self.deepgram_api_key
        ])
            
# Create a global configuration instance
settings = Settings() 