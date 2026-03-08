#!/usr/bin/env python3
"""
YouTube 视频处理器 - 复用 B 站流程
"""

import subprocess
import re
from pathlib import Path
from typing import Optional, Tuple


def download_youtube_audio(
    video_url: str,
    output_dir: str,
    verbose: bool = False
) -> Optional[str]:
    """
    下载 YouTube 视频音频（无需 cookies）
    
    Args:
        video_url: YouTube 视频链接
        output_dir: 输出目录
        verbose: 是否显示详细输出
    
    Returns:
        音频文件路径，失败返回 None
    """
    
    output_template = str(Path(output_dir) / "youtube_%(id)s.%(ext)s")
    
    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "-o", output_template,
        video_url
    ]
    
    if verbose:
        print(f"🔧 执行命令：{' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=not verbose, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ 下载失败：{result.stderr}")
            return None
        
        # 查找生成的文件
        video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_url)
        if video_id_match:
            video_id = video_id_match.group(1)
            audio_files = list(Path(output_dir).glob(f"youtube_{video_id}.*"))
            if audio_files:
                return str(audio_files[0])
        
        # 返回最新的音频文件
        audio_files = list(Path(output_dir).glob("youtube_*.m4a"))
        if audio_files:
            return str(max(audio_files, key=lambda p: p.stat().st_mtime))
        
        return None
        
    except Exception as e:
        print(f"❌ 下载出错：{e}")
        return None


def download_youtube_subtitles(
    video_url: str,
    output_dir: str,
    languages: list = ['en', 'zh-Hans'],
    verbose: bool = False
) -> Tuple[Optional[str], bool]:
    """
    下载 YouTube 官方字幕
    
    Args:
        video_url: YouTube 视频链接
        output_dir: 输出目录
        languages: 字幕语言列表
        verbose: 是否显示详细输出
    
    Returns:
        (字幕文件路径, 是否成功)
    """
    
    output_template = str(Path(output_dir) / "youtube_%(id)s")
    
    # 先尝试下载指定语言的字幕
    for lang in languages:
        cmd = [
            "yt-dlp",
            "--write-sub",
            "--sub-lang", lang,
            "--skip-download",
            "-o", output_template,
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # 查找字幕文件
                video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', video_url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    sub_files = list(Path(output_dir).glob(f"youtube_{video_id}.*.{lang}.vtt"))
                    if sub_files:
                        return str(sub_files[0]), True
        
        except Exception:
            continue
    
    return None, False


def process_youtube_video(
    video_url: str,
    output_dir: str = "./output",
    prefer_official_sub: bool = True,
    verbose: bool = False
) -> dict:
    """
    处理 YouTube 视频（完整流程）
    
    Args:
        video_url: YouTube 视频链接
        output_dir: 输出目录
        prefer_official_sub: 是否优先使用官方字幕
        verbose: 是否显示详细输出
    
    Returns:
        处理结果
    """
    
    result = {
        "video_url": video_url,
        "audio_path": None,
        "subtitle_path": None,
        "transcript_path": None,
        "method": None  # 'official_sub' 或 'whisper'
    }
    
    # 1. 尝试下载官方字幕
    if prefer_official_sub:
        print("📺 尝试下载官方字幕...")
        sub_path, success = download_youtube_subtitles(video_url, output_dir, verbose=verbose)
        
        if success:
            print(f"✅ 找到官方字幕：{sub_path}")
            result["subtitle_path"] = sub_path
            result["method"] = "official_sub"
            
            # 转换 VTT 为纯文本
            transcript_path = Path(output_dir) / f"youtube_transcript.txt"
            convert_vtt_to_text(sub_path, str(transcript_path))
            result["transcript_path"] = str(transcript_path)
            
            return result
    
    # 2. 如果没有官方字幕，下载音频并使用 Whisper
    print("⚠️  未找到官方字幕，使用 Whisper 转录...")
    
    # 下载音频
    audio_path = download_youtube_audio(video_url, output_dir, verbose)
    if not audio_path:
        print("❌ 音频下载失败")
        return result
    
    result["audio_path"] = audio_path
    print(f"✅ 音频已下载：{audio_path}")
    
    # 使用 Whisper 转录
    from transcriber import transcribe_audio
    transcript_path = transcribe_audio(audio_path, output_dir, verbose)
    
    if transcript_path:
        result["transcript_path"] = transcript_path
        result["method"] = "whisper"
        print(f"✅ 转录完成：{transcript_path}")
    
    return result


def convert_vtt_to_text(vtt_path: str, output_path: str):
    """将 VTT 字幕转换为纯文本"""
    
    import re
    
    with open(vtt_path, 'r', encoding='utf-8') as f:
        vtt_content = f.read()
    
    # 移除时间戳和 VTT 标记
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', vtt_content)
    text = re.sub(r'WEBVTT.*\n', '', text)
    text = re.sub(r'NOTE.*\n', '', text)
    
    # 移除多余空行
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean_text = '\n'.join(lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(clean_text)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python src/youtube_processor.py <YouTube 视频链接>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    result = process_youtube_video(video_url, verbose=True)
    
    print("\n" + "="*60)
    print("处理结果：")
    print("="*60)
    for key, value in result.items():
        print(f"{key}: {value}")
