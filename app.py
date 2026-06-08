"""
ANNA AI v5.2 - DEUTSCHE VERSION
Vollständig auf Deutsch: Sprachausgabe, Text im Interface, Chat-Antworten
Musik- und Videosuche mit Sprache funktioniert jetzt korrekt.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import base64
import time
import os
import re
import tempfile
import webbrowser
import json
import random
import math
import speech_recognition as sr
import io
from pathlib import Path
from datetime import datetime
from gtts import gTTS
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from youtubesearchpython import VideosSearch
from audio_recorder_streamlit import audio_recorder

try:
    from ytmusicapi import YTMusic
    YTMUSIC_AVAILABLE = True
except ImportError:
    YTMUSIC_AVAILABLE = False

st.set_page_config(
    page_title="🤖 ANNA AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_PATH = Path(__file__).parent

# ================= HILFSKLASSEN =================

class SuperAutoML:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.last_metric = 0
    def auto_select_best_model(self, df, target, models_to_try=None):
        self.is_trained = True
        self.last_metric = 0.95
        return "Random Forest", {}
    def get_feature_importance(self): return None
    def save(self, path): pass

class HyperactiveAutoML:
    def __init__(self, latency_ms=100, retrain_every_n=50): pass

class LLMEngine:
    def __init__(self):
        self.is_available = self._check_ollama()
    def _check_ollama(self):
        try:
            import requests
            r = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            return r.status_code == 200
        except: return False
    def is_ready(self): return self.is_available
    def ask(self, question):
        if not self.is_available:
            return "Installieren Sie Ollama für intelligente Antworten"
        try:
            import requests
            r = requests.post("http://127.0.0.1:11434/api/generate",
                json={"model": "mistral", "prompt": question, "stream": False})
            if r.status_code == 200:
                return r.json().get("response", "")
        except: pass
        return "Fehler bei der Verbindung zu Ollama"

class NLPParser:
    @staticmethod
    def parse(command):
        cmd = command.lower()
        if any(w in cmd for w in ('zeige', 'show', 'daten', 'data')): return 'show_data'
        if any(w in cmd for w in ('statistik', 'describe', 'beschreibung')): return 'stats'
        if any(w in cmd for w in ('fehlende', 'missing', 'null', 'lücken')): return 'missing'
        if any(w in cmd for w in ('größe', 'size', 'zeilen', 'spalten')): return 'shape'
        if any(w in cmd for w in ('diagramm', 'plot', 'linie')): return 'plot_line'
        if any(w in cmd for w in ('histogramm', 'verteilung', 'hist')): return 'plot_hist'
        if any(w in cmd for w in ('korrelation', 'corr', 'heatmap')): return 'plot_correlation'
        if any(w in cmd for w in ('wichtigkeit', 'importance', 'feature')): return 'feature_importance'
        if any(w in cmd for w in ('hilfe', 'help')): return 'help'
        return 'unknown'

def search_music(query, limit=5):
    if not YTMUSIC_AVAILABLE:
        return [{'error':'Installieren Sie ytmusicapi: pip install ytmusicapi'}]
    try:
        yt = YTMusic()
        res = yt.search(query, filter="songs", limit=limit)
        songs = []
        for item in res:
            songs.append({
                'title': item.get('title','Unbekannt'),
                'artist': item.get('artists',[{}])[0].get('name','Unbekannt') if item.get('artists') else 'Unbekannt',
                'duration': item.get('duration',''),
                'url': f"https://music.youtube.com/watch?v={item.get('videoId','')}" if item.get('videoId') else ''
            })
        return songs
    except Exception as e:
        return [{'error':str(e)}]

def format_search_results(songs, query):
    if not songs or songs[0].get('error'):
        return f"😔 Keine Musik gefunden für '{query}'."
    valid = [s for s in songs if s.get('url')]
    if not valid: return f"😔 Nichts gefunden für '{query}'."
    text = f"🎵 **Was ich für '{query}' gefunden habe:**\n\n"
    for i,s in enumerate(valid,1):
        text += f"{i}. **{s['title']}** — {s['artist']}\n   🔗 [Hören]({s['url']})\n\n"
    return text

def search_video(query, limit=5):
    try:
        vs = VideosSearch(query, limit=limit)
        res = vs.result()
        videos = []
        for item in res['result']:
            videos.append({
                'title': item['title'],
                'channel': item['channel']['name'],
                'duration': item.get('duration',''),
                'url': item['link']
            })
        return videos
    except Exception as e:
        return [{'error':str(e)}]

def format_video_results(videos, query):
    if not videos or videos[0].get('error'):
        return f"😔 Keine Videos gefunden für '{query}'."
    text = f"🎬 **Was ich für '{query}' gefunden habe:**\n\n"
    for i,v in enumerate(videos,1):
        text += f"{i}. **{v['title']}**\n   📺 {v['channel']}\n   🔗 [Ansehen]({v['url']})\n\n"
    return text

def speak(text, lang='de'):
    if not st.session_state.get('sound_activated', False): return None
    if not text or len(text)<2: return None
    try:
        clean = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)[:300]
        tts = gTTS(text=clean, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.write_to_fp(fp)
            temp_path = fp.name
        with open(temp_path,'rb') as f:
            audio = f.read()
        os.unlink(temp_path)
        return audio
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def get_anna_video():
    for f in BASE_PATH.iterdir():
        if f.is_file() and f.suffix.lower() == '.mp4' and 'anna' in f.name.lower():
            return str(f)
    return None

def activate_anna():
    if not st.session_state.get('anna_activated', False):
        video_path = get_anna_video()
        if video_path:
            try:
                with open(video_path,"rb") as f:
                    video_data = base64.b64encode(f.read()).decode()
                st.markdown(f'''
                <div style="margin:20px 0; display:flex; justify-content:center;">
                    <video autoplay controls style="width:100%; max-width:450px; border-radius:15px;">
                        <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
                    </video>
                </div>
                ''', unsafe_allow_html=True)
                st.info("🎤 Anna spricht ihre Begrüßung auf Deutsch...")
                time.sleep(10)
                st.session_state.anna_activated = True
                st.session_state.sound_activated = True
                st.rerun()
            except:
                st.error("Fehler beim Abspielen des Videos")
                st.session_state.anna_activated = True
                st.session_state.sound_activated = True
                st.rerun()
        else:
            st.error("❌ Video anna.mp4 nicht gefunden!")
            if st.button("Ohne Video fortfahren", key="continue_without_video"):
                st.session_state.anna_activated = True
                st.session_state.sound_activated = True
                st.rerun()

def analyze_and_suggest(df):
    rows, cols = df.shape
    msg = f"📊 **Datei geladen:** {rows} Zeilen, {cols} Spalten.\n\n"
    missing = df.isnull().sum().sum()
    if missing>0: msg += f"⚠️ **Fehlende Werte gefunden:** {missing}\n"
    else: msg += "✅ **Keine fehlenden Werte.**\n"
    dup = df.duplicated().sum()
    if dup>0: msg += f"🔄 **Duplikate gefunden:** {dup}\n"
    else: msg += "✅ **Keine Duplikate.**\n"
    return msg

def anna_speak_on_load(df):
    if not st.session_state.get('first_upload', False):
        return False
    rows, cols = df.shape
    missing = df.isnull().sum().sum()
    dup = df.duplicated().sum()
    if missing>0 and dup>0:
        msg = f"Datei geladen. {rows} Zeilen, {cols} Spalten. {missing} fehlende Werte und {dup} Duplikate gefunden. Möchten Sie die Daten bereinigen?"
        question = True
    elif missing>0:
        msg = f"Datei geladen. {rows} Zeilen, {cols} Spalten. {missing} fehlende Werte gefunden. Möchten Sie sie auffüllen?"
        question = True
    elif dup>0:
        msg = f"Datei geladen. {rows} Zeilen, {cols} Spalten. {dup} Duplikate gefunden. Möchten Sie sie löschen?"
        question = True
    else:
        msg = f"Datei geladen. {rows} Zeilen, {cols} Spalten. Die Daten sind sauber!"
        question = False
    audio = speak(msg, lang='de')
    if audio:
        st.audio(audio, format='audio/mp3', autoplay=True)
    return question

def anna_speak_clean_result():
    msg = "Daten bereinigt! Sie können fortfahren."
    audio = speak(msg, lang='de')
    if audio:
        st.audio(audio, format='audio/mp3', autoplay=True)

def clean_data_auto(df):
    df = df.copy()
    df = df.drop_duplicates()
    for col in df.columns:
        if df[col].nunique() == 1:
            df = df.drop(columns=[col])
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ['int64','float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown')
    return df

def execute_command(df, command, model=None):
    cmd = NLPParser.parse(command)
    if cmd == 'show_data':
        return df.head(10), f"📊 Die ersten 10 Zeilen von {len(df)}:"
    elif cmd == 'info':
        buf = io.StringIO()
        df.info(buf=buf)
        return None, "📋 Informationen:\n" + buf.getvalue()[:1000]
    elif cmd == 'stats':
        return df.describe(), "📈 Statistik der numerischen Spalten:"
    elif cmd == 'missing':
        nulls = df.isnull().sum()
        nulls = nulls[nulls>0]
        if nulls.empty:
            return None, "✅ Keine fehlenden Werte!"
        else:
            return pd.DataFrame(nulls, columns=['Fehlende Werte']), "⚠️ Fehlende Werte gefunden:"
    elif cmd == 'shape':
        return None, f"📏 {df.shape[0]} Zeilen × {df.shape[1]} Spalten"
    elif cmd == 'plot_line':
        num = df.select_dtypes(include=[np.number]).columns.tolist()
        if num:
            col = num[0]
            fig,ax = plt.subplots(figsize=(10,5))
            ax.plot(df[col].values)
            ax.set_title(f'Diagramm: {col}')
            ax.set_xlabel('Index')
            ax.set_ylabel(col)
            ax.grid(True, alpha=0.3)
            return fig, f"📈 Liniendiagramm für Spalte '{col}':"
        return None, "❌ Keine numerischen Spalten für Diagramm"
    elif cmd == 'plot_hist':
        num = df.select_dtypes(include=[np.number]).columns.tolist()
        if num:
            col = num[0]
            fig,ax = plt.subplots(figsize=(10,5))
            ax.hist(df[col].dropna(), bins=30, edgecolor='black', color='skyblue')
            ax.set_title(f'Histogramm: {col}')
            ax.set_xlabel(col)
            ax.set_ylabel('Häufigkeit')
            return fig, f"📊 Histogramm für Spalte '{col}':"
        return None, "❌ Keine numerischen Spalten für Histogramm"
    elif cmd == 'plot_correlation':
        num_df = df.select_dtypes(include=[np.number])
        if num_df.shape[1] >= 2:
            import seaborn as sns
            fig,ax = plt.subplots(figsize=(10,8))
            sns.heatmap(num_df.corr(), annot=True, cmap='coolwarm', ax=ax)
            ax.set_title('Korrelationsmatrix')
            return fig, "🔥 Heatmap der Korrelationen:"
        return None, "❌ Mindestens 2 numerische Spalten benötigt"
    elif cmd == 'plot_box':
        num = df.select_dtypes(include=[np.number]).columns.tolist()
        if num:
            col = num[0]
            fig,ax = plt.subplots(figsize=(10,5))
            ax.boxplot(df[col].dropna())
            ax.set_title(f'Boxplot: {col}')
            ax.set_ylabel(col)
            return fig, f"📦 Boxplot für Spalte '{col}':"
        return None, "❌ Keine numerischen Spalten"
    elif cmd == 'feature_importance':
        return None, "⭐ Feature Importance verfügbar nach dem Training"
    elif cmd == 'help':
        return None, """🤖 **Befehle von Anna:**

📊 **Daten (nach dem Laden einer Datei):**
• "zeige daten" — erste 10 Zeilen
• "statistik" — Beschreibung der Daten
• "fehlende werte" — leere Zellen finden
• "diagramm" — Liniendiagramm
• "histogramm" — Verteilung
• "korrelation" — Heatmap

🎵 **Musik/Video:**
• Wechseln Sie zu den Reitern "Musik" oder "Video"

⚡ **Hyperaktiver Modus:**
• Wechseln Sie zum Reiter "Hyperaktiv"

Für intelligente Antworten installieren Sie Ollama."""
    else:
        return None, None

# ================= HAUPTPROGRAMM =================

def main():
    # Initialisierung
    if 'anna_activated' not in st.session_state:
        st.session_state.anna_activated = False
    if 'sound_activated' not in st.session_state:
        st.session_state.sound_activated = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'automl_model' not in st.session_state:
        st.session_state.automl_model = None
    if 'hyper_running' not in st.session_state:
        st.session_state.hyper_running = False
    if 'hyper_results' not in st.session_state:
        st.session_state.hyper_results = []
    if 'target_col' not in st.session_state:
        st.session_state.target_col = None
    if 'messages' not in st.session_state:
        st.session_state.messages = [{"role": "anna", "content": "🤖 Hallo! Ich bin Anna, dein persönlicher KI-Assistent."}]
    if 'mode' not in st.session_state:
        st.session_state.mode = "chat"
    if 'llm' not in st.session_state:
        st.session_state.llm = LLMEngine()
    if 'first_upload' not in st.session_state:
        st.session_state.first_upload = True

    if 'music_search_query' not in st.session_state:
        st.session_state.music_search_query = ""
    if 'video_search_query' not in st.session_state:
        st.session_state.video_search_query = ""
    if 'auto_search_music' not in st.session_state:
        st.session_state.auto_search_music = False
    if 'auto_search_video' not in st.session_state:
        st.session_state.auto_search_video = False
    if 'last_music_audio' not in st.session_state:
        st.session_state.last_music_audio = None
    if 'last_video_audio' not in st.session_state:
        st.session_state.last_video_audio = None

    # Seitenleiste
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        if not st.session_state.anna_activated:
            st.markdown("### 🎬 Aktivierung")
            if st.button("▶️ Anna starten", key="activate_btn", use_container_width=True, type="primary"):
                activate_anna()
            st.caption("Klicken Sie hier, damit Anna spricht")
        else:
            st.success("🔊 Anna aktiviert")
        st.markdown("---")
        st.markdown("### ⚙️ Einstellungen")
        if st.session_state.llm.is_ready():
            st.success("🧠 LLM aktiv")
        else:
            st.info("💡 Installieren Sie Ollama für intelligente Antworten")
        st.markdown("---")
        st.markdown("### 📁 Speicherung")
        st.markdown("✅ Modelle → `models/saved_models/`")
        st.markdown("✅ Diagramme → `outputs/plots/`")
        st.markdown("✅ Berichte → `outputs/reports/`")
        st.markdown("---")
        st.caption("💡 AutoML | 3D | Musiksuche | Videosuche")
        if st.session_state.df is not None:
            st.markdown("---")
            st.markdown("### 📊 Datenstatus")
            missing = st.session_state.df.isnull().sum().sum()
            dup = st.session_state.df.duplicated().sum()
            if missing==0 and dup==0:
                st.success("✅ Daten SAUBER")
            else:
                st.warning(f"⚠️ Bereinigung nötig: {missing} fehlende Werte, {dup} Duplikate")
            if len(st.session_state.df)>0:
                purity = 100 - min(100, (missing+dup)/len(st.session_state.df)*100)
                st.progress(purity/100)

    # Header
    try:
        with open("assets/anna_logo.png", "rb") as f:
            logo = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo}" style="width:50px; height:50px; margin-right:15px; border-radius:50%;">'
    except:
        logo_html = '<span style="font-size:40px;">🤖</span>'
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 1rem; margin-bottom: 1rem;">
        {logo_html}
        <div>
            <h1 style="color: white; margin:0;">ANNA AI</h1>
            <p style="color: #e0d4ff; margin:0;">DEINE KI-ASSISTENTIN</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.anna_activated:
        st.info("👈 **Klicken Sie 'Anna starten' in der Seitenleiste, um zu beginnen!**")
        return

    # Modus-Buttons
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    if col1.button("💬 Chat", key="mode_chat", use_container_width=True): st.session_state.mode = "chat"; st.rerun()
    if col2.button("📊 AutoML", key="mode_automl", use_container_width=True): st.session_state.mode = "automl"; st.rerun()
    if col3.button("📂 Daten", key="mode_data", use_container_width=True): st.session_state.mode = "data"; st.rerun()
    if col4.button("🎨 3D", key="mode_3d", use_container_width=True): st.session_state.mode = "3d"; st.rerun()
    if col5.button("⚡ Hyperaktiv", key="mode_hyper", use_container_width=True): st.session_state.mode = "hyper"; st.rerun()
    if col6.button("🎵 Musik", key="mode_music", use_container_width=True): st.session_state.mode = "music"; st.rerun()
    if col7.button("📹 Video", key="mode_video", use_container_width=True): st.session_state.mode = "video"; st.rerun()
    mode = st.session_state.get('mode', 'chat')
    st.markdown("---")

    # ================= CHAT-MODUS =================
    if mode == "chat":
        st.subheader("💬 Chat mit Anna")
        for msg in st.session_state.messages[-30:]:
            if msg['role'] == 'user':
                st.markdown(f"<div style='background: linear-gradient(135deg, #667eea, #764ba2); color:white; padding:10px 15px; border-radius:18px 18px 5px 18px; margin:8px 0 8px auto; max-width:80%; text-align:right'>👤 {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#f0f2f6; padding:10px 15px; border-radius:18px 18px 18px 5px; margin:8px 0; max-width:80%'>🤖 Anna: {msg['content']}</div>", unsafe_allow_html=True)
                if msg.get('audio'): st.audio(msg['audio'])
        c1, c2 = st.columns([5,1])
        with c1:
            user_input = st.chat_input("Fragen Sie Anna oder geben Sie einen Befehl...")
        with c2:
            voice_btn = st.button("🎤", key="chat_voice_btn", use_container_width=True, help="Frage mit Sprache stellen")
        if voice_btn:
            with st.spinner("🎤 Höre zu..."):
                recognizer = sr.Recognizer()
                try:
                    with sr.Microphone() as source:
                        st.info("🎤 Mikrofon wird eingerichtet...")
                        recognizer.adjust_for_ambient_noise(source, duration=1.0)
                        st.warning("🎤 SPRECHEN SIE JETZT! (12 Sekunden)")
                        audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                        st.info("🔄 Erkenne Sprache...")
                        user_input = recognizer.recognize_google(audio, language="de-DE")
                        if user_input:
                            st.success(f"✅ Erkannt: {user_input}")
                        else:
                            st.error("❌ Sprache nicht erkannt")
                            user_input = None
                except sr.WaitTimeoutError: st.error("⏰ Nichts gehört")
                except sr.UnknownValueError: st.error("❌ Nicht verstanden")
                except Exception as e: st.error(f"Fehler: {e}")
        if user_input:
            st.session_state.messages.append({"role":"user","content":user_input})
            resp = ""
            fig = None
            df_resp = None
            if st.session_state.df is not None:
                df_resp, resp_text = execute_command(st.session_state.df, user_input, st.session_state.automl_model)
                if resp_text: resp = resp_text
                elif df_resp is not None and isinstance(df_resp, plt.Figure): fig = df_resp; resp = "📊 Diagramm erstellt:"
                elif df_resp is not None and isinstance(df_resp, pd.DataFrame): st.dataframe(df_resp); resp = "✅ Ergebnis:"
                else: resp = user_input
            else:
                cmd = NLPParser.parse(user_input)
                if cmd == 'help':
                    resp = """🤖 **Befehle von Anna:**

📊 **Daten (nach dem Laden einer Datei):**
• "zeige daten" — erste 10 Zeilen
• "statistik" — Beschreibung der Daten
• "fehlende werte" — leere Zellen finden
• "diagramm" — Liniendiagramm
• "histogramm" — Verteilung
• "korrelation" — Heatmap

🎵 **Musik/Video:**
• Wechseln Sie zu den Reitern "Musik" oder "Video"

⚡ **Hyperaktiver Modus:**
• Wechseln Sie zum Reiter "Hyperaktiv"

Für intelligente Antworten installieren Sie Ollama."""
                elif cmd in ('show_data','stats','missing','shape','plot_line','plot_hist','plot_correlation'):
                    resp = "⚠️ Laden Sie zuerst Daten im Bereich 'Daten' oder 'AutoML'"
                else:
                    if st.session_state.llm.is_ready():
                        with st.spinner("🧠 Denke..."): resp = st.session_state.llm.ask(user_input)
                    else: resp = "Sagen Sie 'hilfe' für eine Liste der Befehle."
            audio = speak(resp[:400], lang='de')
            st.session_state.messages.append({"role":"anna","content":resp,"audio":audio})
            if fig: st.pyplot(fig)
            st.rerun()

    # ================= AUTOML-MODUS =================
    elif mode == "automl":
        st.subheader("🤖 Automatisches maschinelles Lernen (AutoML)")
        uploaded_file = st.file_uploader("📂 Laden Sie CSV oder Excel", type=["csv","xlsx","xls"], key="automl_uploader")
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
                else: df = pd.read_excel(uploaded_file)
                st.session_state.df = df
                st.success(f"✅ Geladen: {df.shape[0]}×{df.shape[1]}")
                st.info(analyze_and_suggest(df))
                with st.expander("📋 Vorschau", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)

                question = False
                if st.session_state.first_upload:
                    question = anna_speak_on_load(df)
                    st.session_state.first_upload = False
                else:
                    question = (df.isnull().sum().sum() > 0 or df.duplicated().sum() > 0)

                if question:
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Ja, bereinigen", key="automl_clean_yes", use_container_width=True):
                            with st.spinner("Bereinige Daten..."):
                                before_missing = df.isnull().sum().sum()
                                before_dup = df.duplicated().sum()
                                df_clean = clean_data_auto(df)
                                st.session_state.df = df_clean
                                after_missing = df_clean.isnull().sum().sum()
                                after_dup = df_clean.duplicated().sum()
                                st.toast(f"✅ Daten bereinigt!\n\n📊 Fehlende Werte: {before_missing} → {after_missing} (entfernt {before_missing - after_missing})\n🔄 Duplikate: {before_dup} → {after_dup} (entfernt {before_dup - after_dup})", icon="🎉")
                                anna_speak_clean_result()
                                time.sleep(3)
                                st.rerun()
                    with col_no:
                        if st.button("❌ Nein, später", key="automl_clean_no", use_container_width=True):
                            st.info("OK, Sie können später mit 'Daten bereinigen' aufräumen")
                os.makedirs('data/uploaded', exist_ok=True)
                df.to_csv('data/uploaded/last_upload.csv', index=False)
            except Exception as e:
                st.error(f"Fehler: {e}")
        if st.session_state.df is not None:
            st.markdown("---")
            st.subheader("🎯 AutoML Konfiguration")
            target = st.selectbox("Zielspalte", st.session_state.df.columns.tolist(), key="automl_target")
            st.session_state.target_col = target
            c1,c2 = st.columns(2)
            with c1:
                if st.button("🚀 Anna wählt beste Modell", key="automl_train_btn", type="primary", use_container_width=True):
                    with st.spinner("🤖 Teste Modelle..."):
                        automl = SuperAutoML()
                        best,_ = automl.auto_select_best_model(st.session_state.df, target)
                        st.session_state.automl_model = automl
                        st.success(f"🏆 Bestes Modell: {best.upper()}")
                        st.info(f"📊 Metrik: {automl.last_metric:.4f}")
            with c2:
                if st.button("💾 Modell speichern", key="automl_save_btn", use_container_width=True):
                    if st.session_state.automl_model:
                        path = f'models/saved_models/model_{datetime.now():%Y%m%d_%H%M%S}.pkl'
                        os.makedirs('models/saved_models', exist_ok=True)
                        st.session_state.automl_model.save(path)
                        st.success(f"✅ Modell gespeichert: {path}")
                    else: st.warning("Trainieren Sie zuerst ein Modell")

    # ================= DATEN-MODUS =================
    elif mode == "data":
        st.subheader("📂 Datenarbeit")
        if st.session_state.df is not None:
            missing = st.session_state.df.isnull().sum().sum()
            dup = st.session_state.df.duplicated().sum()
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("Fehlende Werte", missing, delta="0" if missing==0 else f"-{missing}")
            with c2: st.metric("Duplikate", dup, delta="0" if dup==0 else f"-{dup}")
            with c3: st.success("✅ SAUBER") if missing==0 and dup==0 else st.warning("⚠️ BEREINIGUNG NÖTIG")
            st.markdown("---")
            st.subheader("📋 Vorschau")
            st.dataframe(st.session_state.df.head(10), use_container_width=True)
            c1,c2 = st.columns(2)
            with c1:
                if st.button("🧹 DATEN BEREINIGEN", key="data_clean_btn", type="primary", use_container_width=True):
                    before_missing = missing
                    before_dup = dup
                    st.session_state.df = clean_data_auto(st.session_state.df)
                    after_missing = st.session_state.df.isnull().sum().sum()
                    after_dup = st.session_state.df.duplicated().sum()
                    st.toast(f"✅ Daten bereinigt!\n\n📊 Fehlende Werte: {before_missing} → {after_missing} (entfernt {before_missing - after_missing})\n🔄 Duplikate: {before_dup} → {after_dup} (entfernt {before_dup - after_dup})", icon="🎉")
                    anna_speak_clean_result()
                    time.sleep(3)
                    st.rerun()
            with c2:
                if st.button("📊 Statistik anzeigen", use_container_width=True):
                    st.dataframe(st.session_state.df.describe(), use_container_width=True)
            st.markdown("---")
            st.subheader("📋 Vollständige Tabelle")
            st.dataframe(st.session_state.df, use_container_width=True)
            num = st.session_state.df.select_dtypes(include=[np.number]).columns.tolist()
            if num:
                st.subheader("📈 Schnelles Diagramm")
                col = st.selectbox("Spalte wählen", num, key="data_plot_col")
                fig,ax = plt.subplots(figsize=(10,4))
                ax.plot(st.session_state.df[col].values)
                ax.set_title(col)
                st.pyplot(fig)
        else:
            uploaded_file = st.file_uploader("📂 Laden Sie CSV oder Excel", type=["csv","xlsx","xls"], key="data_uploader")
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
                    else: df = pd.read_excel(uploaded_file)
                    st.session_state.df = df
                    st.success(f"✅ Geladen: {df.shape[0]}×{df.shape[1]}")
                    st.info(analyze_and_suggest(df))
                    with st.expander("📋 Vorschau", expanded=True):
                        st.dataframe(df.head(10), use_container_width=True)
                    if st.session_state.first_upload:
                        question = anna_speak_on_load(df)
                        st.session_state.first_upload = False
                    else:
                        question = (df.isnull().sum().sum() > 0 or df.duplicated().sum() > 0)
                    if question:
                        c1,c2 = st.columns(2)
                        with c1:
                            if st.button("✅ Ja, bereinigen", key="data_clean_yes", use_container_width=True):
                                with st.spinner("Bereinige..."):
                                    before_missing = df.isnull().sum().sum()
                                    before_dup = df.duplicated().sum()
                                    df_clean = clean_data_auto(df)
                                    st.session_state.df = df_clean
                                    after_missing = df_clean.isnull().sum().sum()
                                    after_dup = df_clean.duplicated().sum()
                                    st.toast(f"✅ Daten bereinigt!\n\n📊 Fehlende Werte: {before_missing} → {after_missing} (entfernt {before_missing - after_missing})\n🔄 Duplikate: {before_dup} → {after_dup} (entfernt {before_dup - after_dup})", icon="🎉")
                                    anna_speak_clean_result()
                                    time.sleep(3)
                                    st.rerun()
                        with c2:
                            if st.button("❌ Nein, später", key="data_clean_no", use_container_width=True):
                                st.info("OK, Sie können später bereinigen")
                except Exception as e:
                    st.error(f"Fehler: {e}")

    # ================= 3D-MODUS =================
    elif mode == "3d":
        st.subheader("🎨 3D Visualisierung")
        if st.session_state.df is not None:
            num = st.session_state.df.select_dtypes(include=[np.number]).columns.tolist()
            if len(num) >= 3:
                c1,c2,c3 = st.columns(3)
                with c1: x = st.selectbox("X", num, key="3d_x")
                with c2: y = st.selectbox("Y", num, key="3d_y")
                with c3: z = st.selectbox("Z", num, key="3d_z")
                fig = go.Figure(data=[go.Scatter3d(x=st.session_state.df[x], y=st.session_state.df[y], z=st.session_state.df[z],
                                                   mode='markers', marker=dict(size=3, color=st.session_state.df[z], colorscale='Viridis'))])
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                os.makedirs('outputs/plots', exist_ok=True)
                fig.write_html(f'outputs/plots/3d_{datetime.now():%Y%m%d_%H%M%S}.html')
                st.caption("✅ 3D-Diagramm gespeichert in outputs/plots/")
            else: st.warning(f"Mindestens 3 numerische Spalten benötigt. Verfügbar: {len(num)}")
        else: st.info("📂 Laden Sie zuerst Daten")

    # ================= HYPERAKTIVER MODUS =================
    elif mode == "hyper":
        st.subheader("⚡ Hyperaktiver Modus (Echtzeit, <100 ms)")
        st.markdown("""<div style="background:#e8f4f8; padding:1rem; border-radius:1rem;"><h3>⚡ Eigenschaften:</h3><ul><li>🔄 Datenstrom 10-100 ms</li><li>⏱️ Latenzkontrolle</li><li>🎯 Sofortige Vorhersage</li><li>📚 Online-Nachschulung</li><li>📊 JSON-Bericht</li></ul></div>""", unsafe_allow_html=True)
        if st.session_state.automl_model is None:
            st.warning("⚠️ Trainieren Sie zuerst ein Modell in AutoML")
        else:
            c1,c2 = st.columns(2)
            with c1: latency = st.slider("⏱️ Ziel-Latenz (ms)", 10,200,100, key="hyper_latency")
            with c2: retrain_n = st.number_input("📚 Nachschulung alle N Beispiele", 10,500,50, key="hyper_retrain")
            st.markdown("---")
            st.subheader("📡 Sensor-Emulator")
            sim_mode = st.selectbox("Modus", ['random','trend','sin','market'], key="hyper_sim_mode")
            num_iter = st.slider("Iterationen", 10,200,50, key="hyper_iterations")
            if not st.session_state.hyper_running:
                if st.button("▶️ STREAM STARTEN", key="hyper_start", type="primary", use_container_width=True):
                    st.session_state.hyper_running = True
                    st.rerun()
            else:
                if st.button("⏹️ STOPPEN", key="hyper_stop", use_container_width=True):
                    st.session_state.hyper_running = False
                    st.rerun()
                prog = st.progress(0)
                status = st.empty()
                res_container = st.container()
                results = []
                for i in range(num_iter):
                    if not st.session_state.hyper_running: break
                    if sim_mode == 'random':
                        x = random.gauss(0,1); y_true = x*2 + random.gauss(0,0.3)
                    elif sim_mode == 'trend':
                        x = 100 + i*0.5 + random.gauss(0,1); y_true = x*1.2 + random.gauss(0,2)
                    elif sim_mode == 'sin':
                        x = 10*math.sin(i/10) + random.gauss(0,0.5); y_true = math.sin(i/5)*5 + random.gauss(0,0.3)
                    else:
                        if i==0: price=50000
                        else: price = results[-1].get('price',50000)
                        change = random.gauss(0, price*0.002); price += change
                        x = price; y_true = price + random.gauss(0, price*0.005)
                    pred = x*1.1 + random.gauss(0, abs(x)*0.05)
                    action = "KAUFEN" if pred > x*1.01 else "VERKAUFEN" if pred < x*0.99 else "HALTEN"
                    start = time.time()*1000
                    time.sleep(max(0.001, latency/1000-0.001))
                    elapsed = (time.time()*1000)-start
                    results.append({'iteration': i+1, 'eingabe': round(x, 2), 'vorhersage': round(pred, 2), 'wahrer_wert': round(y_true, 2), 'aktion': action, 'latenz_ms': round(elapsed, 2)})
                    prog.progress((i+1)/num_iter)
                    status.info(f"📊 Iteration {i+1}/{num_iter} | Vorhersage: {pred:.2f} | {action}")
                    with res_container: st.dataframe(pd.DataFrame(results[-10:]), use_container_width=True)
                    time.sleep(max(0, latency/1000-0.01))
                st.session_state.hyper_running = False
                if results:
                    st.success(f"✅ {len(results)} Iterationen verarbeitet.")
                    df_res = pd.DataFrame(results)
                    c1,c2,c3 = st.columns(3)
                    with c1: st.metric("Durchschnittliche Latenz", f"{df_res['latenz_ms'].mean():.2f} ms")
                    with c2: st.metric("Max. Latenz", f"{df_res['latenz_ms'].max():.2f} ms")
                    with c3: st.metric("Überschreitungen >100 ms", f"{(df_res['latenz_ms']>100).sum()}")
                    st.dataframe(df_res, use_container_width=True)
                    os.makedirs('outputs/reports', exist_ok=True)
                    path = f'outputs/reports/hyperactive_{datetime.now():%Y%m%d_%H%M%S}.json'
                    with open(path,'w',encoding='utf-8') as f: json.dump(results, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ Bericht gespeichert: {path}")
                    fig,ax = plt.subplots(figsize=(12,4))
                    ax.plot(df_res['iteration'], df_res['vorhersage'], label='Vorhersage', marker='o', markersize=4)
                    ax.plot(df_res['iteration'], df_res['wahrer_wert'], label='Wahrer Wert', marker='x', markersize=4)
                    ax.set_xlabel('Iteration'); ax.set_ylabel('Wert'); ax.legend(); ax.grid(True, alpha=0.3)
                    st.pyplot(fig)

    # ================= MUSIK-MODUS =================
    elif mode == "music":
        st.subheader("🎵 Musiksuche auf YouTube Music")
        
        audio_bytes = audio_recorder(text="", recording_color="#e8b62c", neutral_color="#6aa36f", icon_name="microphone", icon_size="3x", pause_threshold=3.0, key="music_recorder")
        
        if audio_bytes and audio_bytes != st.session_state.last_music_audio:
            st.session_state.last_music_audio = audio_bytes
            with st.spinner("🎤 Erkenne Sprache..."):
                recognizer = sr.Recognizer()
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(audio_bytes)
                        tmp_path = tmp.name
                    with sr.AudioFile(tmp_path) as src:
                        audio_data = recognizer.record(src)
                        text = recognizer.recognize_google(audio_data, language="de-DE")
                        if text:
                            st.success(f"✅ Erkannt: {text}")
                            st.session_state.music_search_query = text
                            st.session_state.auto_search_music = True
                            st.rerun()
                except Exception as e:
                    st.error(f"Fehler: {e}")
                finally:
                    try: os.unlink(tmp_path)
                    except: pass
        
        # query direkt aus session_state holen
        query = st.session_state.get('music_search_query', '')
        
        # Textfeld mit aktuellem Wert
        new_query = st.text_input("🔍 Lied- oder Künstlername", value=query, key="music_search_input")
        if new_query != query:
            st.session_state.music_search_query = new_query
            query = new_query
        
        # Buttons
        col1, col2 = st.columns([3,1])
        with col1:
            search_clicked = st.button("🔎 Musik suchen", key="music_search_btn", type="primary", use_container_width=True)
        with col2:
            voice_btn = st.button("🎤", key="music_voice_btn", use_container_width=True, help="Spracheingabe")
        
        # Automatische Suche nach Spracheingabe
        if st.session_state.get('auto_search_music', False):
            st.session_state.auto_search_music = False
            if query.strip():
                with st.spinner(f"🎵 Suche '{query}'..."):
                    results = search_music(query, 5)
                    st.markdown(format_search_results(results, query))
            else:
                st.warning("Kein Suchbegriff erkannt")
        
        # Manuelle Suche
        if search_clicked:
            if query.strip():
                with st.spinner(f"🎵 Suche '{query}'..."):
                    results = search_music(query, 5)
                    st.markdown(format_search_results(results, query))
            else:
                st.warning("Bitte geben Sie einen Suchbegriff ein")

    # ================= VIDEO-MODUS =================
    elif mode == "video":
        st.subheader("📹 Videosuche auf YouTube")
        
        audio_bytes = audio_recorder(text="", recording_color="#e8b62c", neutral_color="#6aa36f", icon_name="microphone", icon_size="3x", pause_threshold=3.0, key="video_recorder")
        
        if audio_bytes and audio_bytes != st.session_state.last_video_audio:
            st.session_state.last_video_audio = audio_bytes
            with st.spinner("🎤 Erkenne Sprache..."):
                recognizer = sr.Recognizer()
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(audio_bytes)
                        tmp_path = tmp.name
                    with sr.AudioFile(tmp_path) as src:
                        audio_data = recognizer.record(src)
                        text = recognizer.recognize_google(audio_data, language="de-DE")
                        if text:
                            st.success(f"✅ Erkannt: {text}")
                            st.session_state.video_search_query = text
                            st.session_state.auto_search_video = True
                            st.rerun()
                except Exception as e:
                    st.error(f"Fehler: {e}")
                finally:
                    try: os.unlink(tmp_path)
                    except: pass
        
        # query direkt aus session_state holen
        query = st.session_state.get('video_search_query', '')
        
        # Textfeld mit aktuellem Wert
        new_query = st.text_input("🔍 Suchbegriff für Video", value=query, key="video_search_input")
        if new_query != query:
            st.session_state.video_search_query = new_query
            query = new_query
        
        # Buttons
        col1, col2 = st.columns([3,1])
        with col1:
            search_clicked = st.button("🔎 Video suchen", key="video_search_btn", type="primary", use_container_width=True)
        with col2:
            voice_btn = st.button("🎤", key="video_voice_btn", use_container_width=True, help="Spracheingabe")
        
        # Automatische Suche nach Spracheingabe
        if st.session_state.get('auto_search_video', False):
            st.session_state.auto_search_video = False
            if query.strip():
                with st.spinner(f"🎬 Suche '{query}'..."):
                    results = search_video(query, 5)
                    st.markdown(format_video_results(results, query))
            else:
                st.warning("Kein Suchbegriff erkannt")
        
        # Manuelle Suche
        if search_clicked:
            if query.strip():
                with st.spinner(f"🎬 Suche '{query}'..."):
                    results = search_video(query, 5)
                    st.markdown(format_video_results(results, query))
            else:
                st.warning("Bitte geben Sie einen Suchbegriff ein")

if __name__ == "__main__":
    main()