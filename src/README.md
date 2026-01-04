# Oke Creator - Web App Edition

FFmpeg + Demucs によるボーカル分離・キー変更ツールのWebアプリ版です。

## 📋 機能

- ✅ **ボーカル分離**: Demucsを使用してVocals / No Vocalに分離
- ✅ **キー変更**: -3～+3の半音単位でキー変更（テンポ維持）
- ✅ **フォルマント考慮**: ボーカルの声質を保持
- ✅ **48kHz WAV出力**: ダンス本番・PA向け出力対応
- ✅ **Webベースの使いやすいUI**: Streamlitで実装

## 🚀 セットアップ

### 1. 必要なライブラリのインストール

```bash
cd C:\manabu\develop\python3\oke-creator
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install demucs torch torchcodec streamlit pandas
```

### 2. FFmpegのインストール確認

```powershell
ffmpeg -version
```

`F:\tools\ffmpeg\bin` に配置済みで、環境変数PATHに追加されている必要があります。

## 🎯 使い方

### 方法1: バッチファイルで起動（推奨）

```bash
run_app.bat
```

### 方法2: 手動で起動

```bash
.venv\Scripts\activate
streamlit run src/app.py
```

ブラウザで http://localhost:8501 に自動的に開きます。

## 📁 ディレクトリ構造

```
src/
├── app.py              # Streamlit Webアプリのメイン
├── config.py           # 設定・pitch倍率テーブル
└── utils/
    ├── __init__.py
    ├── audio_utils.py  # Demucs分離実行
    └── ffmpeg_utils.py # FFmpeg実行（キー変更・48kHz変換）
```

## 🎛️ 使用方法の詳細

### Tab 1: ボーカル分離

1. `C:\Users\manab\Downloads\` から .mp3 / .m4a ファイルを選択
2. 「Demucs で分離を実行」ボタンをクリック
3. 処理完了後、`C:\manabu\temp\htdemucs\曲名\` に以下が生成されます:
   - `vocals.wav` - ボーカルのみ
   - `no_vocals.wav` - ボーカル除外

### Tab 2: キー変更・48kHz変換

1. 分離済み曲を選択
2. 処理対象（Vocals / No Vocals）を選択
3. キー変更を設定（-3～+3）
4. 必要に応じてフォルマント考慮をチェック
5. 出力フォーマットを選択（44.1kHz / 48kHz）
6. 「キー変更・変換を実行」ボタンをクリック

## 🎵 キー変更 pitch 倍率参照表

| 半音 | Pitch倍率 |
|------|-----------|
| -3   | 0.840896  |
| -2   | 0.890899  |
| -1   | 0.943874  |
|  0   | 1.0       |
| +1   | 1.059463  |
| +2   | 1.122462  |
| +3   | 1.189207  |

※計算式: `2^(n/12)`

## 💡 ベストプラクティス

✅ **推奨:**
- `rubberband` フィルタを使用（テンポ維持）
- 48kHz WAV でダンス本番向け出力
- ボーカルは `formant=1.0` で声質を保持

❌ **非推奨:**
- `asetrate` 単体でのキー変更（テンポがズレる）

## 📝 設定ファイル

### config.py

パス、pitch倍率テーブル、キー選択肢を集中管理:

```python
DOWNLOADS_DIR = Path(r"C:\Users\manab\Downloads")
WORK_DIR = Path(r"C:\manabu\temp\htdemucs")

PITCH_TABLE = {
    -3: 0.840896,
    -2: 0.890899,
    ...
}
```

カスタマイズが必要な場合はこのファイルを編集してください。

## 🔧 トラブルシューティング

### Demucsのエラー

```
確認: python -m demucs --help
```

インストール状況を確認し、必要に応じて再インストール:

```bash
pip install --upgrade demucs
```

### FFmpegのエラー

```
確認: ffmpeg -version
```

環境変数PATHを確認し、FFmpegへのパスが正しく設定されているか確認してください。

### Streamlitが起動しない

```bash
pip install --upgrade streamlit
streamlit run src/app.py
```

## 📄 ライセンス

このプロジェクトは個人利用・技術検証目的です。  
音源の著作権・利用条件に注意してください。

## 📚 参考

- [Demucs](https://github.com/facebookresearch/demucs)
- [FFmpeg](https://ffmpeg.org/)
- [Streamlit](https://streamlit.io/)
