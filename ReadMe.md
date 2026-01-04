# oke-creator 🎤🎶  
Demucs + FFmpeg による  
**ボーカル分離／キー変更（テンポ維持・フォルマント考慮）ワークフロー**

---

## 概要
このリポジトリは、以下を目的とした **実験・実運用ログ兼レシピ集** です。

- iTunes / Apple Music 由来の **.m4a 音源**
- **Demucs** によるボーカル分離（vocals / no_vocals）
- **FFmpeg + rubberband** によるキー変更
  - 半音単位（-1, -2, -3, …）
  - テンポ維持
  - フォルマント（声質）考慮
- ダンス本番・口パク用途を想定した **48kHz WAV 出力**

---

## 動作環境
- OS: **Windows 10 / 11**
- Python: **3.x（64bit）**
- FFmpeg:  
  - 配置先：  
    ```
    F:\tools\ffmpeg\bin
    ```
  - `ffmpeg.exe` が上記ディレクトリに存在
  - 環境変数 `PATH` に `F:\tools\ffmpeg\bin` を追加済み

確認：
```powershell
ffmpeg -version


Python 仮想環境（venv）セットアップ
1. venv 作成
cd C:\manabu\develop\python3\oke-creator
python -m venv .venv

2. venv 有効化（Windows）
.venv\Scripts\activate


プロンプトに (.venv) が付けばOK。

必要ライブラリのインストール
#pip install --upgrade pip
python.exe -m pip install --upgrade pip 
pip install demucs torchcodec


確認：

python -m demucs --help

1. ボーカル分離（Demucs）
Korean version
python -m demucs --two-stems=vocals -o C:\manabu\temp ^
"C:\Users\manab\Downloads\01 FeelSpecial.m4a"


出力例：

htdemucs/
└─ 01 FeelSpecial/
   ├─ vocals.wav
   └─ no_vocals.wav

2. ❌ NG例：asetrate によるキー変更（テンポが遅くなる）
key -3（44.1kHz）
ffmpeg -i "C:\manabu\temp\htdemucs\01 FeelSpecial\no_vocals.wav" ^
-filter:a "asetrate=44100*0.8409,aresample=44100" ^
"C:\manabu\temp\htdemucs\01 FeelSpecial\karaoke_key-3.wav"

key -3（48kHz）
ffmpeg -i "C:\manabu\temp\htdemucs\01 FeelSpecial\no_vocals.wav" ^
-filter:a "asetrate=48000*0.8409,aresample=48000" ^
"C:\manabu\temp\htdemucs\01 FeelSpecial\karaoke_key-3_48k.wav"


❗ 問題点

曲の長さが 3:25 → 約4:06

テンポが遅くなり、ダンス用途に不適

3. ✅ 正解：rubberband によるキー変更（テンポ維持）
key -3（カラオケ）
ffmpeg -i "C:\manabu\temp\htdemucs\01 FeelSpecial\no_vocals.wav" ^
-filter:a "rubberband=pitch=0.840896415" ^
"C:\manabu\temp\htdemucs\01 FeelSpecial\karaoke_key-3_v2.wav"


テンポ維持

曲の長さは元と同じ

4. Feel Special JP ver で再実施
分離
python -m demucs --two-stems=vocals -o C:\manabu\temp ^
"C:\Users\manab\Downloads\03FeelSpecial-Jp ver-.m4a"

key -3（カラオケ）
ffmpeg -i "C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\no_vocals.wav" ^
-filter:a "rubberband=pitch=0.840896415" ^
"C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\jp_karaoke_key-3_v2.wav"

key -3（ボーカル：フォルマント考慮）
ffmpeg -i "C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\vocals.wav" ^
-filter:a "rubberband=pitch=0.840896415:formant=1.0" ^
"C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\vocals_jp_karaoke_key-3_v3.wav"

原曲（m4a）も key -3
ffmpeg -i "C:\Users\manab\Downloads\03FeelSpecial-Jp ver-.m4a" ^
-filter:a "rubberband=pitch=0.840896415" ^
-c:a aac -b:a 256k ^
"C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\Feel_Special_key-3.m4a"

5. key -1 に変更する場合
カラオケ key -1
ffmpeg -i "C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\no_vocals.wav" ^
-filter:a "rubberband=pitch=0.943874312" ^
"C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\jp_karaoke_key-1_v3.wav"

ボーカル key -1
ffmpeg -i "C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\vocals.wav" ^
-filter:a "rubberband=pitch=0.943874312" ^
"C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\jp_vocal_key-1_v3.wav"

原曲 key -1（wav）
ffmpeg -i "C:\Users\manab\Downloads\03FeelSpecial-Jp ver-.m4a" ^
-filter:a "rubberband=pitch=0.943874312" ^
"C:\manabu\temp\htdemucs\03FeelSpecial-Jp ver-\jp_Feel_Special_key-1_orig.wav"

6. 48kHz WAV で出力（本番・PA向け）
ffmpeg -i input.wav ^
-filter:a "rubberband=pitch=0.943874312:formant=1.0" ^
-ar 48000 -ac 2 ^
output_48k.wav

7. 半音キー変更 早見表（超重要）
半音	pitch倍率
-1	0.943874
-2	0.890899
-3	0.840896
-4	0.793701

計算式：

2^(n/12)

8. ベストプラクティスまとめ

❌ asetrate 単体 → テンポがズレる

✅ rubberband → テンポ維持

🎤 歌声あり → formant=1.0 を基本に微調整

🎶 ダンス本番 → 48kHz WAV 推奨

🧪 実験ログはそのまま再現可能な形で残す

注意事項

原曲の著作権・利用条件に注意

本リポジトリは 技術検証・個人利用目的


