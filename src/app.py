"""
Oke Creator Web App
FFmpegを使用したボーカル分離・キー変更ツール
"""
import streamlit as st
from pathlib import Path
import sys
import time

# パスを追加
sys.path.insert(0, str(Path(__file__).parent))

from config import DOWNLOADS_DIR, WORK_DIR, KEY_CHANGES, PITCH_TABLE
from utils.audio_utils import (
    get_audio_files,
    get_demucs_output_dir,
    get_separated_wavs,
    run_demucs_separation,
    get_song_directories
)
from utils.ffmpeg_utils import apply_pitch_change, convert_to_48k, resolve_unique_path


# Streamlit設定
st.set_page_config(
    page_title="Oke Creator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎤 Oke Creator - ボーカル分離 & キー変更ツール")
st.markdown("Demucs + FFmpeg による ボーカル分離・キー変更（テンポ維持・フォルマント考慮）")

# パス設定
with st.sidebar:
    st.header("⚙️ 設定・情報")

    st.subheader("📍 パス設定")
    downloads_dir = Path(
        st.text_input(
            "入力フォルダ",
            value=str(DOWNLOADS_DIR),
            help=".mp3 / .m4a / .wav を探すフォルダ"
        )
    )
    work_dir = Path(
        st.text_input(
            "作業・出力フォルダ",
            value=str(WORK_DIR),
            help="Demucs 分離結果と変換後 WAV の保存先"
        )
    )

    if st.button("📁 作業フォルダを作成", key="create_work_dir"):
        work_dir.mkdir(parents=True, exist_ok=True)
        st.success(f"作業フォルダを作成しました: {work_dir}")

    if not downloads_dir.exists():
        st.warning(f"入力フォルダが存在しません: {downloads_dir}")
    if not work_dir.exists():
        st.warning(f"作業フォルダが存在しません: {work_dir}")

# タブ構成
tab1, tab2 = st.tabs(["ボーカル分離", "キー変更・48kHz変換"])

# ==================== Tab 1: ボーカル分離 ====================
with tab1:
    st.header("📁 Step 1: ボーカル分離")
    
    # 音源ファイル選択
    audio_files = get_audio_files(downloads_dir)
    
    if audio_files:
        file_names = [f.name for f in audio_files]
        selected_file_name = st.selectbox(
            "分離する音声ファイルを選択",
            file_names,
            key="audio_file_select"
        )
        selected_file = next(f for f in audio_files if f.name == selected_file_name)
        
        # ファイル情報表示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ファイル名", selected_file.name)
        with col2:
            st.metric("ファイルサイズ", f"{selected_file.stat().st_size / (1024*1024):.1f} MB")
        with col3:
            st.metric("保存先", str(work_dir))
        
        # Demucs実行
        if st.button("🚀 Demucs で分離を実行", key="run_demucs"):
            with st.spinner("ボーカル分離中... これには数分かかります"):
                start_time = time.time()
                success, demucs_log = run_demucs_separation(selected_file, work_dir)
                elapsed_time = time.time() - start_time
            
            with st.expander("Demucs 実行ログ", expanded=not success):
                st.code(demucs_log or "(ログなし)", language="text")

            if success:
                st.success(f"✅ 分離完了！ ({elapsed_time:.1f}秒)")
                st.info(f"📂 出力先: {work_dir}")
                
                # 分離結果を表示
                song_name = selected_file.stem
                separated_files = get_separated_wavs(song_name, work_dir)
                
                if separated_files:
                    st.markdown("### 分離済みファイル:")
                    col1, col2 = st.columns(2)
                    with col1:
                        if 'vocals' in separated_files:
                            st.code(f"✔️ vocals.wav")
                    with col2:
                        if 'no_vocals' in separated_files:
                            st.code(f"✔️ no_vocals.wav")
            else:
                st.error("❌ Demucs実行中にエラーが発生しました。")
                st.info("確認事項: demucsがインストールされているか確認してください")
    else:
        st.warning(f"⚠️ {downloads_dir} に .mp3 / .m4a / .wav ファイルが見つかりません")


# ==================== Tab 2: キー変更・48kHz変換 ====================
with tab2:
    st.header("🎵 Step 2: キー変更・48kHz WAV変換")
    
    # 分離済み曲を取得
    song_dirs = get_song_directories(work_dir)
    
    if song_dirs:
        selected_song = st.selectbox(
            "処理する曲を選択（分離済みから）",
            song_dirs,
            key="song_select"
        )
        
        # 該当曲のWAVファイルを取得
        separated_files = get_separated_wavs(selected_song, work_dir)
        
        if separated_files:
            st.markdown(f"### 📂 曲: `{selected_song}`")
            
            # WAVファイル選択（no_vocals, vocals, original）
            wav_options = list(separated_files.keys()) + ["original"]
            selected_wav_type = st.radio(
                "処理するファイルを選択",
                wav_options,
                format_func=lambda x: {
                    'vocals': '🎤 Vocals（ボーカルのみ）',
                    'no_vocals': '🎵 No Vocals（カラオケ）',
                    'original': '📌 Original（Step 1前の元ファイル）'
                }.get(x, x),
                key="wav_type_select"
            )
            
            # 選択されたファイルを取得
            if selected_wav_type == 'original':
                # 元ファイルを探す（ダウンロードフォルダから）
                original_files = list(downloads_dir.glob('*'))
                original_files = [f for f in original_files if f.suffix in ['.mp3', '.m4a', '.wav']]
                # 曲名に基づいてフィルタリング
                matching_files = [f for f in original_files if selected_song.lower() in f.name.lower()]
                
                if matching_files:
                    input_wav = matching_files[0]
                    st.warning("⚠️ 元ファイルが見つかりました。キー変更後のサンプルレートは48kHzに統一されます。")
                else:
                    st.error(f"❌ 元ファイルが見つかりません: {selected_song}")
                    input_wav = None
            else:
                input_wav = separated_files[selected_wav_type]
            
            if input_wav:
                st.code(str(input_wav), language="text")
            
            st.divider()
            
            # キー変更オプション
            st.subheader("🎛️ 処理設定")
            
            col1, col2 = st.columns(2)
            
            with col1:
                key_change = st.select_slider(
                    "キー変更（半音）",
                    options=KEY_CHANGES,
                    value=0,
                    key="key_change_slider"
                )
                
                st.info(f"Pitch倍率: **{PITCH_TABLE[key_change]:.6f}**")
            
            with col2:
                include_formant = st.checkbox(
                    "フォルマント考慮（声質保持）",
                    value=(selected_wav_type == 'vocals'),
                    disabled=(selected_wav_type == 'original'),
                    key="formant_checkbox"
                )
                
                if selected_wav_type == 'original':
                    st.caption("📌 元ファイルはフォルマント適用できません")
                elif include_formant:
                    st.caption("🎤 ボーカルの声質を保持します")
            
            st.divider()
            
            # 出力オプション
            st.subheader("💾 出力設定")
            
            col1, col2 = st.columns(2)
            
            with col1:
                output_format = st.radio(
                    "出力フォーマット",
                    ["44.1kHz WAV", "48kHz WAV"],
                    key="output_format"
                )
            
            with col2:
                # Version番号（ユーザー入力可）
                version_input = st.number_input(
                    "バージョン番号",
                    min_value=1,
                    max_value=99,
                    value=1,
                    key="version_number"
                )
            
            # 出力ファイル名の生成（col外で常に更新）
            # 書式: 曲名_種類_キー数字_kHz_vN
            # 例: 03FeelSpecial-Jp ver-_novocals_-3_48kHz_v1.wav
            
            # 処理ファイル種類の表記
            if selected_wav_type == 'original':
                type_str = "original"
            elif selected_wav_type == 'no_vocals':
                type_str = "novocals"
            else:
                type_str = "vocals"
            
            # キーの表記（シンプルに：+3, -2, 0など）
            key_str = f"{key_change:+d}" if key_change != 0 else "0"
            
            # サンプルレート表記
            khz_str = "48kHz" if "48kHz" in output_format else "44kHz"
            
            # 最終的なファイル名生成（オリジナルフォーマット）
            original_base_name = f"{selected_song}_{type_str}_{key_str}_{khz_str}_v{version_input}"
            
            # session_state で初期化・管理
            if "output_filename_text" not in st.session_state:
                st.session_state.output_filename_text = original_base_name
            
            # 再調整ボタンが押されたかチェック（ウィジェット作成前に）
            if st.session_state.get("reset_filename_flag", False):
                st.session_state.output_filename_text = original_base_name
                st.session_state.reset_filename_flag = False
            
            st.subheader("💾 ファイル名設定")
            
            # ファイル名と再調整ボタンを横並び
            col1, col2 = st.columns([0.85, 0.15])
            
            with col1:
                output_filename = st.text_input(
                    "出力ファイル名（拡張子除外）",
                    value=st.session_state.output_filename_text,
                    key="output_filename_text"
                )
            
            with col2:
                st.write("")  # スペース調整
                if st.button("🔄 再調整", key="reset_filename_button", help="オリジナルフォーマットにリセット"):
                    st.session_state.reset_filename_flag = True
                    st.rerun()
            
            requested_output_wav = get_demucs_output_dir(work_dir) / selected_song / f"{output_filename}.wav"
            output_wav = resolve_unique_path(requested_output_wav)
            
            st.markdown(f"**📂 出力先:**")
            st.code(str(output_wav), language="text")
            if output_wav != requested_output_wav:
                st.warning(f"同名ファイルがあるため、上書きせず次の名前で保存します: {output_wav.name}")
            
            st.divider()
            
            # 実行ボタン
            if st.button("🚀 キー変更・変換を実行", key="run_conversion", type="primary"):
                
                # コマンドをプレビュー表示
                st.subheader("📋 実行予定のFFmpegコマンド")
                
                if output_format == "44.1kHz WAV":
                    from utils.ffmpeg_utils import build_ffmpeg_command
                    cmd = build_ffmpeg_command(
                        input_wav,
                        output_wav,
                        key_change,
                        include_formant=include_formant,
                        sample_rate=44100
                    )
                else:
                    from utils.ffmpeg_utils import build_48k_command
                    cmd = build_48k_command(
                        input_wav,
                        output_wav,
                        key_change=key_change,
                        include_formant=include_formant
                    )
                
                cmd_str = ' '.join(cmd)
                st.code(cmd_str, language="powershell")
                
                st.divider()
                
                # 実際に処理を実行
                if output_format == "44.1kHz WAV":
                    with st.spinner("処理中..."):
                        start_time = time.time()
                        success, cmd_log, process_log = apply_pitch_change(
                            input_wav,
                            output_wav,
                            key_change,
                            include_formant=include_formant,
                            sample_rate=44100
                        )
                        elapsed_time = time.time() - start_time
                else:
                    with st.spinner("処理中..."):
                        start_time = time.time()
                        success, cmd_log, process_log = convert_to_48k(
                            input_wav,
                            output_wav,
                            key_change=key_change,
                            include_formant=include_formant
                        )
                        elapsed_time = time.time() - start_time
                
                with st.expander("FFmpeg 実行ログ", expanded=not success):
                    st.code(process_log or "(ログなし)", language="text")

                if success:
                    st.success(f"✅ 変換完了！ ({elapsed_time:.1f}秒)")
                    
                    # ファイル情報表示
                    if output_wav.exists():
                        file_size = output_wav.stat().st_size / (1024*1024)
                        st.metric("出力ファイルサイズ", f"{file_size:.1f} MB")
                        st.code(str(output_wav), language="text")
                else:
                    st.error("❌ 変換中にエラーが発生しました")
        else:
            st.warning(f"⚠️ `{selected_song}` に分離済みファイルが見つかりません")
    else:
        st.warning(f"⚠️ {work_dir} に分離済みの曲が見つかりません")
        st.info("📌 まずは Tab 1 でボーカル分離を実行してください")


# ==================== サイドバー ====================
with st.sidebar:
    st.code(f"入力: {downloads_dir}", language="text")
    st.code(f"作業: {work_dir}", language="text")
    
    st.divider()
    
    st.subheader("🎵 キー変更 早見表")
    pitch_data = {
        "半音": list(PITCH_TABLE.keys()),
        "Pitch倍率": list(PITCH_TABLE.values())
    }
    
    import pandas as pd
    df = pd.DataFrame(pitch_data)
    st.dataframe(df, width="stretch")
    
    st.divider()
    
    st.subheader("💡 使い方")
    st.markdown("""
    **Step 1: ボーカル分離**
    - ダウンロードフォルダから音声ファイルを選択
    - Demucsで分離実行
    - Vocals と No Vocals を生成
    
    **Step 2: キー変更**
    - 分離済みファイルを選択
    - キー変更（-3～+3）を設定
    - 必要に応じてフォルマント考慮
    - 出力フォーマット選択（44.1kHz or 48kHz）
    - 変換実行
    
    **📝 注意:**
    - FFmpeg のインストール必須
    - Demucsのインストール必須
    - 48kHz WAVはダンス本番・PA向け推奨
    """)
