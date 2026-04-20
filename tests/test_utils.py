import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import calculate_pitch_ratio
from utils.audio_utils import get_demucs_output_dir, get_demucs_parent_dir
from utils.ffmpeg_utils import resolve_unique_path


class UtilityTests(unittest.TestCase):
    def test_calculate_pitch_ratio(self):
        self.assertAlmostEqual(calculate_pitch_ratio(-1), 0.943874312, places=6)
        self.assertEqual(calculate_pitch_ratio(0), 1.0)

    def test_resolve_unique_path_keeps_new_path(self):
        path = Path("song.wav")
        with patch.object(Path, "exists", return_value=False):
            self.assertEqual(resolve_unique_path(path), path)

    def test_resolve_unique_path_adds_version_suffix(self):
        existing = {"song.wav", "song_v2.wav"}
        path = Path("song.wav")

        with patch.object(Path, "exists", lambda self: self.name in existing):
            self.assertEqual(resolve_unique_path(path).name, "song_v3.wav")

    def test_demucs_output_dir_handles_default_model_folder(self):
        work_dir = Path(r"C:\manabu\temp\htdemucs")
        self.assertEqual(get_demucs_output_dir(work_dir), work_dir)
        self.assertEqual(get_demucs_parent_dir(work_dir), work_dir.parent)

    def test_demucs_output_dir_handles_custom_base_folder(self):
        work_dir = Path(r"C:\audio-work")
        self.assertEqual(get_demucs_output_dir(work_dir), work_dir / "htdemucs")
        self.assertEqual(get_demucs_parent_dir(work_dir), work_dir)


if __name__ == "__main__":
    unittest.main()
