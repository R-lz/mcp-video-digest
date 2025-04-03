import os
from typing import Optional
import yt_dlp
from ..transcription.base import Context

class YouTubeDownloader:
    """YouTube video downloader"""
    
    def __init__(self):
        self.ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "temp_audio.%(ext)s",
            "quiet": True,
            "cookiefile": "cookies.txt",
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            }
        }
        
    async def download(self, url: str, ctx: Context) -> Optional[str]:
        """
            Download the audio part of the video
        
        Args:
            url: video URL
            ctx: context object
            
        Returns:
            Optional[str]: the path of the downloaded file, or None if failed
        """
        ctx.log("Start downloading video...")
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                ctx.log(f"Download completed, file path: {downloaded_file}")
                return downloaded_file
                
        except Exception as e:
            ctx.log(f"Download failed: {str(e)}")
            return None 