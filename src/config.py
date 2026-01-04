"""設定ファイル"""
from pathlib import Path
import math

# パス設定
DOWNLOADS_DIR = Path(r"C:\Users\manab\Downloads")
WORK_DIR = Path(r"C:\manabu\temp\htdemucs")

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
