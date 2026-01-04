"""FFmpegユーティリティ"""
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from config import PITCH_TABLE


def build_ffmpeg_command(
    input_wav: Path,
    output_wav: Path,
    key_change: int,
    include_formant: bool = False,
    sample_rate: int = 44100
) -> list:
    """
    FFmpegコマンドを構築（キー変更）
    
    Args:
        input_wav: 入力 WAV ファイルパス
        output_wav: 出力 WAV ファイルパス
        key_change: キー変更（-3～+3の半音）
        include_formant: フォルマント考慮（ボーカル向け）
        sample_rate: サンプルレート（デフォルト44100）
    
    Returns:
        FFmpegコマンドリスト
    """
    pitch_ratio = PITCH_TABLE.get(key_change, 1.0)
    
    if include_formant:
        audio_filter = f"rubberband=pitch={pitch_ratio}:formant=1.0"
    else:
        audio_filter = f"rubberband=pitch={pitch_ratio}"
    
    cmd = [
        'ffmpeg',
        '-i', str(input_wav),
        '-filter:a', audio_filter,
        '-ar', str(sample_rate),
        '-y',
        str(output_wav)
    ]
    return cmd


def apply_pitch_change(
    input_wav: Path,
    output_wav: Path,
    key_change: int,
    include_formant: bool = False,
    sample_rate: int = 44100
) -> Tuple[bool, str]:
    """
    FFmpeg + rubberband で pitch 変更を実行
    
    Args:
        input_wav: 入力 WAV ファイルパス
        output_wav: 出力 WAV ファイルパス
        key_change: キー変更（-3～+3の半音）
        include_formant: フォルマント考慮（ボーカル向け）
        sample_rate: サンプルレート（デフォルト44100）
    
    Returns:
        (成功時True、失敗時False, コマンド文字列)
    """
    try:
        if not input_wav.exists():
            print(f"Input file not found: {input_wav}")
            return False, ""
        
        # コマンドを構築
        cmd = build_ffmpeg_command(input_wav, output_wav, key_change, include_formant, sample_rate)
        cmd_str = ' '.join(cmd)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True, cmd_str
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False, cmd_str
            
    except Exception as e:
        print(f"Exception in apply_pitch_change: {e}")
        return False, ""


def build_48k_command(
    input_wav: Path,
    output_wav: Path,
    key_change: Optional[int] = None,
    include_formant: bool = False
) -> list:
    """
    FFmpegコマンドを構築（48kHz変換）
    
    Args:
        input_wav: 入力 WAV ファイルパス
        output_wav: 出力 WAV ファイルパス
        key_change: キー変更（オプション）
        include_formant: フォルマント考慮
    
    Returns:
        FFmpegコマンドリスト
    """
    cmd = [
        'ffmpeg',
        '-i', str(input_wav),
        '-ar', '48000',
        '-ac', '2',
        '-y',
    ]
    
    if key_change is not None and key_change != 0:
        pitch_ratio = PITCH_TABLE.get(key_change, 1.0)
        if include_formant:
            audio_filter = f"rubberband=pitch={pitch_ratio}:formant=1.0"
        else:
            audio_filter = f"rubberband=pitch={pitch_ratio}"
        cmd.extend(['-filter:a', audio_filter])
    
    cmd.append(str(output_wav))
    return cmd


def convert_to_48k(
    input_wav: Path,
    output_wav: Path,
    key_change: Optional[int] = None,
    include_formant: bool = False
) -> Tuple[bool, str]:
    """
    WAVを48kHzに変換（キー変更有無選択可）
    
    Args:
        input_wav: 入力 WAV ファイルパス
        output_wav: 出力 WAV ファイルパス
        key_change: キー変更（オプション）
        include_formant: フォルマント考慮
    
    Returns:
        (成功時True、失敗時False, コマンド文字列)
    """
    try:
        if not input_wav.exists():
            print(f"Input file not found: {input_wav}")
            return False, ""
        
        cmd = build_48k_command(input_wav, output_wav, key_change, include_formant)
        cmd_str = ' '.join(cmd)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True, cmd_str
        else:
            print(f"FFmpeg error: {result.stderr}")
            return False, cmd_str
            
    except Exception as e:
        print(f"Exception in convert_to_48k: {e}")
        return False, ""
