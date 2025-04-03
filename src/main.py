from mcp.server.fastmcp import FastMCP
from src.services.download.youtube import YouTubeDownloader
from src.services.transcription.base import Context
from src.services.transcription.deepgram import DeepgramTranscriptionService
from src.services.transcription.gladia import GladiaTranscriptionService
from src.services.transcription.speechmatics import SpeechmaticsTranscriptionService
from src.services.transcription.assemblyai import AssemblyAITranscriptionService
from config.settings import settings
import os

mcp = FastMCP(
    name='video-digest',
    instructions="This server provides video transcription services"
)

class MCPContext:
    def __init__(self, mcp_instance):
        self.mcp = mcp_instance
        
    def log(self, message: str) -> None:
        print(f"[VideoDigest] {message}")


class VideoDigest:
    """Video content processing service"""
    
    def __init__(self):
        self.downloader = YouTubeDownloader()
        
        # Initialize transcription services
        self.transcription_services = [
            DeepgramTranscriptionService(),
            GladiaTranscriptionService(),
            SpeechmaticsTranscriptionService(),
            AssemblyAITranscriptionService()
        ]
        
        # 确保临时目录存在
        settings.ensure_temp_dir()
        
    def has_valid_service(self) -> bool:
        return any(service.api_key for service in self.transcription_services)
        
    async def process_video(self, url: str, ctx=None) -> str:
        """Process video content"""
        if not self.has_valid_service():
            raise ValueError("All API keys are empty, please provide at least one valid key!")
            
        try:
            # Download audio
            audio_path = await self.downloader.download(url, ctx)
            if not audio_path:
                raise ValueError("Download failed!")
                
            try:
                # Try each transcription service in priority order
                for service in self.transcription_services:
                    if not service.api_key:
                        continue
                        
                    try:
                        result = await service.transcribe(audio_path, ctx)
                        if result:
                            return f"Transcription content: {result}"
                    except Exception as e:
                        if ctx:
                            ctx.log(f"{service.__class__.__name__} transcription failed: {str(e)}")
                        continue
                        
                raise ValueError("All transcription services failed")
                
            finally:
                # 清理临时文件
                if settings.cleanup_temp and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                        if ctx:
                            ctx.log("Temporary file cleaned up")
                    except Exception as e:
                        if ctx:
                            ctx.log(f"Failed to clean up temporary file: {str(e)}")
                            
        except Exception as e:
            if ctx:
                ctx.log(f"Processing failed: {str(e)}")
            raise

# Create service instance
service = VideoDigest()

@mcp.tool(description="Process video content and generate text record")
async def get_video_content(url: str):
    ctx = MCPContext(mcp)
    return await service.process_video(url,ctx=ctx)

if __name__ == "__main__":
    print("Starting video transcription service...")    
    mcp.run(transport="sse")