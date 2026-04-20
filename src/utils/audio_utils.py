"""音声ファイル操作ユーティリティ"""
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from config import DOWNLOADS_DIR, WORK_DIR

DEMUCS_MODEL_NAME = "htdemucs"


def get_demucs_output_dir(work_dir: Path = WORK_DIR) -> Path:
    """Return the directory where Demucs writes song folders."""
    return work_dir if work_dir.name == DEMUCS_MODEL_NAME else work_dir / DEMUCS_MODEL_NAME


def get_demucs_parent_dir(work_dir: Path = WORK_DIR) -> Path:
    """Return the parent directory to pass to `demucs -o`."""
    return work_dir.parent if work_dir.name == DEMUCS_MODEL_NAME else work_dir


def get_audio_files(downloads_dir: Path = DOWNLOADS_DIR) -> List[Path]:
    """
    指定されたフォルダ配下の .mp3 / .m4a / .wav ファイルをリスト
    
    Returns:
        オーディオファイルのPathオブジェクトリスト
    """
    if not downloads_dir.exists():
        return []
    
    audio_files = []
    for ext in ['*.mp3', '*.m4a', '*.wav']:
        audio_files.extend(downloads_dir.glob(ext))
    
    # ファイル名でソート
    return sorted(audio_files)


def get_separated_wavs(song_name: str, work_dir: Path = WORK_DIR) -> Dict[str, Path]:
    """
    Demucsで分離済みの .wav ファイルをリスト
    
    Args:
        song_name: 曲名（拡張子除外）
    
    Returns:
        {'vocals': Path, 'no_vocals': Path} 形式の辞書
    """
    song_dir = get_demucs_output_dir(work_dir) / song_name
    
    result = {}
    if (song_dir / 'vocals.wav').exists():
        result['vocals'] = song_dir / 'vocals.wav'
    if (song_dir / 'no_vocals.wav').exists():
        result['no_vocals'] = song_dir / 'no_vocals.wav'
    
    return result


def run_demucs_separation(input_file: Path, work_dir: Path = WORK_DIR) -> Tuple[bool, str]:
    """
    Demucsでボーカル分離を実行
    
    Args:
        input_file: 入力オーディオファイルのPath
    
    Returns:
        (成功時True、失敗時False, ログ文字列)
    """
    try:
        # Demucs実行
        cmd = [
            sys.executable, '-m', 'demucs',
            '--two-stems=vocals',
            '-n', DEMUCS_MODEL_NAME,
            '-o', str(get_demucs_parent_dir(work_dir)),
            str(input_file)
        ]
        cmd_str = ' '.join(cmd)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True, build_process_log(cmd_str, result.stdout, result.stderr)
        else:
            return False, build_process_log(cmd_str, result.stdout, result.stderr)
            
    except Exception as e:
        return False, f"Exception in run_demucs_separation: {e}"


def get_song_directories(work_dir: Path = WORK_DIR) -> List[str]:
    """
    C:/manabu/temp/htdemucs/ 配下の分離済み曲ディレクトリを取得
    
    Returns:
        ディレクトリ名のリスト
    """
    demucs_output_dir = get_demucs_output_dir(work_dir)
    if not demucs_output_dir.exists():
        return []
    
    dirs = [d.name for d in demucs_output_dir.iterdir()
            if d.is_dir() and (d / 'vocals.wav').exists()]
    
    return sorted(dirs)


def build_process_log(command: str, stdout: str, stderr: str) -> str:
    return "\n".join(
        part
        for part in [
            f"$ {command}",
            "\n[stdout]\n" + stdout.strip() if stdout.strip() else "",
            "\n[stderr]\n" + stderr.strip() if stderr.strip() else "",
        ]
        if part
    )
