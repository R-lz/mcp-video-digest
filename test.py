import asyncio
from src.main import VideoDigest
from src.services.download.youtube import YouTubeDownloader
from src.services.transcription.deepgram import DeepgramTranscriptionService
from src.services.transcription.gladia import GladiaTranscriptionService
from src.services.transcription.speechmatics import SpeechmaticsTranscriptionService
from src.services.transcription.assemblyai import AssemblyAITranscriptionService
import os
from dotenv import load_dotenv
import pathlib

class TestContext:
    def log(self, message):
        print(f"[测试] {message}")

async def test_youtube_download():
    print("\n=== 测试 YouTube 下载 ===")
    downloader = YouTubeDownloader()
    ctx = TestContext()
    
    try:
        url = "https://www.youtube.com/watch?v=Q3ceynNniR0" 
        result = await downloader.download(url, ctx)
        print(f"下载成功: {result}")
        
        if os.path.exists(result):
            print(f"文件大小: {os.path.getsize(result)} 字节")
        else:
            print("文件不存在！")
            
    except Exception as e:
        print(f"下载失败: {str(e)}")

async def test_transcription_services():
    print("\n=== 测试转录服务 ===")
    ctx = TestContext()
    
    test_audio = "temp_audio.webm" 
    
    # 测试 Deepgram
    print("\n测试 Deepgram:")
    deepgram = DeepgramTranscriptionService()
    try:
        result = await deepgram.transcribe(test_audio, ctx)
        print(f"Deepgram 转录结果: {result[:100]}...")
    except Exception as e:
        print(f"Deepgram 转录失败: {str(e)}")
    
    print("\n测试 Gladia:")
    gladia = GladiaTranscriptionService()
    try:
        result = await gladia.transcribe(test_audio, ctx)
        print(f"Gladia 转录结果: {result[:100]}...")
    except Exception as e:
        print(f"Gladia 转录失败: {str(e)}")
    
    print("\n测试 Speechmatics:")
    speechmatics = SpeechmaticsTranscriptionService()
    try:
        result = await speechmatics.transcribe(test_audio, ctx)
        print(f"Speechmatics 转录结果: {result[:100]}...")
    except Exception as e:
        print(f"Speechmatics 转录失败: {str(e)}")
    
    print("\n测试 AssemblyAI:")
    assemblyai = AssemblyAITranscriptionService()
    try:
        result = await assemblyai.transcribe(test_audio, ctx)
        print(f"AssemblyAI 转录结果: {result[:100]}...")
    except Exception as e:
        print(f"AssemblyAI 转录失败: {str(e)}")

async def test_video_digest():
    print("\n=== 测试完整视频处理流程 ===")
    service = VideoDigest()
    ctx = TestContext()
    
    try:
        url = "https://www.youtube.com/watch?v=Q3ceynNniR0" 
        result = await service.process_video(url, ctx)
        print(f"处理结果: {result}")
        
    except Exception as e:
        print(f"处理失败: {str(e)}")

async def main():
    root_dir = pathlib.Path(__file__).parent.absolute()
    env_path = root_dir / '.env'
    print(f"正在加载环境变量文件: {env_path}")
    if env_path.exists():
        load_dotenv(env_path)
        print("环境变量文件加载成功")
    else:
        print(f"警告: 环境变量文件不存在: {env_path}")
    
    required_vars = [
        "DEEPGRAM_API_KEY",
        "GLADIA_API_KEY",
        "SPEECHMATICS_API_KEY",
        "ASSEMBLYAI_API_KEY"
    ]
    
    print("\n当前环境变量值:")
    for var in required_vars:
        value = os.getenv(var)
        print(f"{var}: {'已设置' if value else '未设置'}")
    
    await test_youtube_download()
    #await test_transcription_services()
    #await test_video_digest()

if __name__ == "__main__":
    asyncio.run(main()) 