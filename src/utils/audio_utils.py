"""音声ファイル操作ユーティリティ"""
import subprocess
from pathlib import Path
from typing import List, Dict
from config import DOWNLOADS_DIR, WORK_DIR


def get_audio_files() -> List[Path]:
    """
    C:/Users/manab/Downloads/ 配下の .mp3 と .m4a ファイルをリスト
    
    Returns:
        オーディオファイルのPathオブジェクトリスト
    """
    if not DOWNLOADS_DIR.exists():
        return []
    
    audio_files = []
    for ext in ['*.mp3', '*.m4a', '*.wav']:
        audio_files.extend(DOWNLOADS_DIR.glob(ext))
    
    # ファイル名でソート
    return sorted(audio_files)


def get_separated_wavs(song_name: str) -> Dict[str, Path]:
    """
    Demucsで分離済みの .wav ファイルをリスト
    
    Args:
        song_name: 曲名（拡張子除外）
    
    Returns:
        {'vocals': Path, 'no_vocals': Path} 形式の辞書
    """
    song_dir = WORK_DIR / song_name
    
    result = {}
    if (song_dir / 'vocals.wav').exists():
        result['vocals'] = song_dir / 'vocals.wav'
    if (song_dir / 'no_vocals.wav').exists():
        result['no_vocals'] = song_dir / 'no_vocals.wav'
    
    return result


def run_demucs_separation(input_file: Path) -> bool:
    """
    Demucsでボーカル分離を実行
    
    Args:
        input_file: 入力オーディオファイルのPath
    
    Returns:
        成功時True、失敗時False
    """
    try:
        # Demucs実行
        cmd = [
            'python', '-m', 'demucs',
            '--two-stems=vocals',
            '-o', str(WORK_DIR),
            str(input_file)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Demucs error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Exception in run_demucs_separation: {e}")
        return False


def get_song_directories() -> List[str]:
    """
    C:/manabu/temp/htdemucs/ 配下の分離済み曲ディレクトリを取得
    
    Returns:
        ディレクトリ名のリスト
    """
    if not WORK_DIR.exists():
        return []
    
    dirs = [d.name for d in WORK_DIR.iterdir() 
            if d.is_dir() and (d / 'vocals.wav').exists()]
    
    return sorted(dirs)
