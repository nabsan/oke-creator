"""設定ファイル"""
import os
from pathlib import Path


def _load_env_file() -> None:
    """Load simple KEY=VALUE entries from the project-level .env file."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_env_file()

# パス設定
DOWNLOADS_DIR = Path(os.environ.get("OKE_DOWNLOADS_DIR", r"C:\Users\manab\Downloads"))
WORK_DIR = Path(os.environ.get("OKE_WORK_DIR", r"C:\manabu\temp\htdemucs"))

# 半音キー変更の pitch 倍率計算
def calculate_pitch_ratio(semitones: int) -> float:
    """
    半音数からpitch倍率を計算
    計算式: 2^(n/12)
    
    Args:
        semitones: 半音数（-3～+3の範囲）
    
    Returns:
        pitch倍率
    """
    return 2 ** (semitones / 12)


# 事前計算した pitch 倍率テーブル
PITCH_TABLE = {
    -3: 0.840896,
    -2: 0.890899,
    -1: 0.943874,
    0: 1.0,
    1: 1.059463,
    2: 1.122462,
    3: 1.189207,
}

# キー変更の選択肢
KEY_CHANGES = [-3, -2, -1, 0, 1, 2, 3]
