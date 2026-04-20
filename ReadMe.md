# Oke Creator

Demucs + FFmpeg による、ボーカル分離とキー変更のための Streamlit アプリです。

- Demucs で `vocals.wav` / `no_vocals.wav` を生成
- FFmpeg + rubberband でテンポを維持したままキー変更
- ボーカル向けにフォルマント考慮を選択可能
- 44.1kHz / 48kHz WAV 出力に対応
- 同名の出力ファイルがある場合は上書きせず、`_v2`, `_v3` のように別名保存

## 起動方法

推奨は `run_app.bat` です。

```powershell
cd S:\tools\codex\oke-creator
.\run_app.bat
```

手動で起動する場合:

```powershell
cd S:\tools\codex\oke-creator
.\.venv\Scripts\python.exe -m streamlit run .\src\app.py --server.address 127.0.0.1 --server.port 8501
```

ブラウザで開く URL:

```text
http://127.0.0.1:8501
```

## 停止方法

起動したターミナルで `Ctrl+C` を押します。

バックグラウンドで残っている場合:

```powershell
Get-NetTCPConnection -LocalPort 8501 -State Listen
Stop-Process -Id <PID>
```

## パス設定

入力フォルダと作業フォルダは、アプリのサイドバーから変更できます。

起動時のデフォルト値は `.env` でも指定できます。`.env.example` をコピーして `.env` を作成してください。

```powershell
Copy-Item .\.env.example .\.env
```

設定例:

```env
OKE_DOWNLOADS_DIR=C:\Users\manab\Downloads
OKE_WORK_DIR=C:\manabu\temp\htdemucs
```

`OKE_WORK_DIR` は Demucs の `htdemucs` 出力フォルダを指す想定です。別のベースフォルダを指定した場合は、その配下の `htdemucs` をアプリが参照します。

## 前提

- Windows 10 / 11
- Python 仮想環境 `.venv`
- FFmpeg が `PATH` から実行できること
- Demucs が `.venv` にインストールされていること

確認コマンド:

```powershell
.\.venv\Scripts\python.exe -m demucs --help
ffmpeg -version
```

## テスト

```powershell
cd S:\tools\codex\oke-creator
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## ドキュメント整理

- `ReadMe.md`: 現在の入口。このファイルを優先して参照します。
- `README2.md`: 既存の詳細ユーザーガイド。履歴込みの補足資料です。
- `src/README.md`: 実装ファイル構成の補足です。

## 注意

音源の著作権と利用条件に注意してください。このリポジトリは技術検証・個人利用を主目的としています。
