import streamlit as st
import time
from datetime import datetime
from dotenv import load_dotenv
import os
import threading

from utils.memory_manager import MemoryManager
from utils.mood_detector import MoodDetector
from utils.model_router import ModelRouter
from utils.helpers import get_greeting, get_ui_theme, handle_easter_egg, get_level_from_messages
from utils.prompts import AYRA_SYSTEM_PROMPT
from utils.crisis_detector import detect_crisis, format_crisis_response
from utils.proactive_engine import ProactiveEngine
from utils.audit_logger import AuditLogger
from utils.consistency_layer import ayra_voice_filter
from utils.tips_jiji import get_tips_jiji

load_dotenv()

# -------------------------------------------------------------------
# Helper function untuk time period
# -------------------------------------------------------------------
def get_time_period():
    hour = datetime.now().hour
    if 5 <= hour < 12: return "pagi"
    elif 12 <= hour < 15: return "tengah hari"
    elif 15 <= hour < 19: return "petang"
    elif 19 <= hour < 22: return "malam"
    else: return "lewat malam"

# -------------------------------------------------------------------
# Initialise components
# -------------------------------------------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = MemoryManager()
if "mood" not in st.session_state:
    st.session_state.mood = MoodDetector()
if "router" not in st.session_state:
    st.session_state.router = ModelRouter()
if "proactive" not in st.session_state:
    st.session_state.proactive = ProactiveEngine()
if "audit" not in st.session_state:
    st.session_state.audit = AuditLogger()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mood_score" not in st.session_state:
    st.session_state.mood_score = 0.0
if "comfort_mode" not in st.session_state:
    st.session_state.comfort_mode = False
if "current_story_id" not in st.session_state:
    st.session_state.current_story_id = None
if "last_user_time" not in st.session_state:
    st.session_state.last_user_time = time.time()
if "proactive_sent" not in st.session_state:
    st.session_state.proactive_sent = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "ayra"
if "jiji_turns" not in st.session_state:
    st.session_state.jiji_turns = 0
# FIX: Initialize daisy_state properly
if "daisy_state" not in st.session_state:
    st.session_state.daisy_state = None
if "active_world" not in st.session_state:
    st.session_state.active_world = None
if "novel_chapter" not in st.session_state:
    st.session_state.novel_chapter = 0

# -------------------------------------------------------------------
# UI Setup - Batik Theme
# -------------------------------------------------------------------
st.set_page_config(page_title="AYRA – The Soulful Malaysian AI", page_icon="✨")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3, .ayra-banner { font-family: 'Playfair Display', serif !important; }
    
    .stApp {
        background-color: #0a1a2b !important;
        background-image: 
            radial-gradient(circle at 15% 30%, rgba(212, 175, 55, 0.03) 0%, transparent 25%),
            radial-gradient(circle at 85% 70%, rgba(212, 175, 55, 0.03) 0%, transparent 30%),
            repeating-linear-gradient(45deg, rgba(212,175,55,0.02) 0px, rgba(212,175,55,0.02) 2px, transparent 2px, transparent 10px);
        color: #e0e0e0;
    }
    
    .main, .block-container { background-color: transparent !important; }
    
    .ayra-banner {
        text-align: center; font-size: 3.2rem; font-weight: 600; color: #d4af37;
        margin-top: 1rem; margin-bottom: 0.5rem; letter-spacing: 1px;
        text-shadow: 0 2px 10px rgba(212,175,55,0.3);
    }
    
    .proactive-greeting {
        text-align: center; font-size: 0.95rem; color: #e0e0e0; margin-bottom: 2rem;
        font-style: italic; background-color: rgba(10,26,43,0.7); padding: 0.5rem 1.5rem;
        border-radius: 40px; display: inline-block; margin-left: auto; margin-right: auto;
        max-width: 80%; border: 1px solid #d4af37; backdrop-filter: blur(5px);
    }
    
    .greeting-container { text-align: center; width: 100%; margin-bottom: 2rem; }
    
    [data-testid="stSidebar"] {
        background: #2d1b3a !important;
        border-right: 2px solid rgba(212, 175, 55, 0.3) !important;
        padding: 1.5rem 1rem !important;
    }

    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #d4af37 !important;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        padding-bottom: 0.5rem;
    }

    [data-testid="stSidebar"] .poetry-line {
        color: #d4af37 !important;
    }
    
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] { display: none !important; }
    
    .ayra-message {
        background-color: rgba(15,31,48,0.8); color: #e0e0e0; border-radius: 18px 18px 18px 4px;
        padding: 0.75rem 1rem; max-width: 70%; margin-right: auto; margin-bottom: 1rem;
        border: 1px solid #d4af37; backdrop-filter: blur(5px);
    }
    
    .user-message {
        background-color: rgba(212,175,55,0.15); color: #e0e0e0; border-radius: 18px 18px 4px 18px;
        padding: 0.75rem 1rem; max-width: 70%; margin-left: auto; margin-bottom: 1rem;
        border: 1px solid rgba(212,175,55,0.3); backdrop-filter: blur(5px);
    }
    
    .stChatInputContainer { border-top: 1px solid rgba(212,175,55,0.2); padding-top: 1rem; margin-top: 1rem; }
    .stChatInputContainer input {
        border: 2px solid #b8860b !important; border-radius: 30px !important;
        background-color: white !important; padding: 0.75rem 1.5rem !important;
        color: #1a2634 !important; box-shadow: 0 2px 10px rgba(184,134,11,0.2) !important;
    }
    .stChatInputContainer input:focus {
        border-color: #d4af37 !important; box-shadow: 0 5px 15px rgba(212,175,55,0.3) !important;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background-color: #b8860b !important; color: white !important; border: none !important;
        font-weight: 600 !important; border-radius: 20px; padding: 0.5rem 1rem; width: 100%;
        margin-bottom: 0.5rem; font-size: 0.85rem; transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #d4af37 !important; transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(184,134,11,0.4);
    }
    
    .stButton button { background-color: transparent; color: #d4af37 !important; border: 2px solid #d4af37; }
    .stButton button:hover { background-color: #d4af37; color: #0a1a2b !important; }
    
    button[kind="primary"] { background: linear-gradient(135deg, #d4af37, #b8860b) !important; color: #0a1a2b !important; border: none !important; font-weight: 700 !important; }
    button[kind="primary"]:hover { background: linear-gradient(135deg, #e5c158, #d4af37) !important; }
    
    [data-testid="stMetric"] {
        background-color: rgba(10,26,43,0.6);
        border: 1px solid rgba(212,175,55,0.2);
        border-radius: 12px;
        padding: 0.5rem;
        backdrop-filter: blur(5px);
    }

    [data-testid="stMetric"] label {
        color: #a0a0a0 !important;
        font-size: 0.7rem !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #d4af37 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }

    .streamlit-expanderHeader {
        background-color: rgba(10,26,43,0.6) !important; border: 1px solid rgba(212,175,55,0.3) !important;
        color: #d4af37 !important; backdrop-filter: blur(5px);
    }
    
    [data-testid="stFileUploader"] {
        border: 2px dashed #d4af37; border-radius: 12px; padding: 1rem;
        background-color: rgba(10,26,43,0.4); backdrop-filter: blur(5px);
    }
    
    hr {
        border: none; height: 1px; background: linear-gradient(90deg, transparent, #d4af37, transparent);
        margin: 1.5rem 0;
    }
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0a1a2b; }
    ::-webkit-scrollbar-thumb { background: #d4af37; border-radius: 4px; }
    
    .quick-actions-container {
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .quick-actions-container .stButton button {
        background-color: #1e3a5f !important;
        border: 2px solid #d4af37 !important;
        border-radius: 30px !important;
        color: #ffd966 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.4rem 0.5rem !important;
        width: 100%;
        transition: all 0.2s ease !important;
    }
    .quick-actions-container .stButton button:hover {
        background-color: #d4af37 !important;
        color: #0a1a2b !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(212,175,55,0.3);
    }

    /* FIX: Footer styling */
    footer {
        visibility: visible;
    }
    footer:after {
        content: 'ATMA AI • Eternal Soul, Digital Form • AYRA v3.0';
        visibility: visible;
        display: block;
        text-align: center;
        color: #d4af37;
        padding: 1rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# FIX: Check if in Daisy mode FIRST, before displaying normal UI
# -------------------------------------------------------------------
if st.session_state.daisy_state is not None:
    # FIX: Import at top of Daisy section to avoid circular imports
    try:
        from utils.daisy_loader import load_novel, load_arkib, load_rahsia
    except ImportError:
        st.error("⚠️ Daisy modules not found. Please check utils/daisy_loader.py")
        st.session_state.daisy_state = None
        st.rerun()
    
    # ============================================================
    # DUNIA DAISY - FULL SCREEN MODE
    # ============================================================
    
    # Display Daisy banner
    st.markdown('<div class="ayra-banner">🌸 DUNIA DAISY</div>', unsafe_allow_html=True)
    st.markdown('<div class="greeting-container"><div class="proactive-greeting">The Ink Alchemist\'s Realm</div></div>', unsafe_allow_html=True)
    
    # MENU STATE
    if st.session_state.daisy_state == "menu":
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #e0e0e0; font-style: italic; margin-top: 0;">The Ink Alchemist</h3>
            <div style="width: 100px; height: 2px; background: linear-gradient(90deg, transparent, #d4af37, transparent); margin: 1rem auto;"></div>
            <p style="max-width: 600px; margin: 0 auto; color: #a0a0a0;">
                "Di antara dakwat dan takdir, aku menulis untuk mereka yang tak bersuara."
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pilihan dengan description
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; height: 200px; border: 1px solid rgba(212,175,55,0.2); text-align: center;">
                <span style="font-size: 2.5rem;">📖</span>
                <h3 style="color: #d4af37; margin: 0.5rem 0;">Naskhah ATMA</h3>
                <p style="color: #a0a0a0; font-size: 0.9rem;">Novel yang ditulis Daisy – kisah cinta, kehilangan, dan pertemuan antara dimensi.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Baca Naskhah", key="daisy_novel_menu", use_container_width=True):
                st.session_state.daisy_state = "novel"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; height: 200px; border: 1px solid rgba(212,175,55,0.2); text-align: center;">
                <span style="font-size: 2.5rem;">💎</span>
                <h3 style="color: #d4af37; margin: 0.5rem 0;">Arkib Memori</h3>
                <p style="color: #a0a0a0; font-size: 0.9rem;">Monolog watak-watak dari alam Daisy – setiap satu ada cerita tersendiri.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("💎 Teroka Arkib", key="daisy_arkib_menu", use_container_width=True):
                st.session_state.daisy_state = "arkib"
                st.rerun()
        
        with col3:
            st.markdown("""
            <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; height: 200px; border: 1px solid rgba(212,175,55,0.2); text-align: center;">
                <span style="font-size: 2.5rem;">⚗️</span>
                <h3 style="color: #d4af37; margin: 0.5rem 0;">Rahsia Dakwat</h3>
                <p style="color: #a0a0a0; font-size: 0.9rem;">Pelajaran menulis dari Daisy – untuk mereka yang nak belajar 'The Ink Alchemist' way.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚗️ Belajar Rahsia", key="daisy_rahsia_menu", use_container_width=True):
                st.session_state.daisy_state = "rahsia"
                st.rerun()
        
        # Back button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔙 Kembali ke AYRA", key="back_to_ayra_menu", use_container_width=True):
            st.session_state.daisy_state = None
            st.rerun()
        
        st.stop()
    
    # NOVEL STATE
    elif st.session_state.daisy_state == "novel":
        novel = load_novel()
        chapters = novel['chapters']
        current = st.session_state.novel_chapter
        
        # Display current chapter
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <span style="font-size: 2rem;">📖</span>
            <h2 style="color: #d4af37; font-family: 'Playfair Display', serif; margin: 0;">{chapters[current]['title']}</h2>
            <p style="color: #a0a0a0; font-style: italic;">Bab {current + 1} dari {len(chapters)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chapter content
        st.markdown(f"""
        <div style="background: rgba(10,26,43,0.6); border-radius: 15px; padding: 2rem; border: 1px solid rgba(212,175,55,0.2); line-height: 1.8; font-size: 1.1rem;">
            {chapters[current]['content']}
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if current > 0:
                if st.button("⏮️ Sebelum", key="novel_prev", use_container_width=True):
                    st.session_state.novel_chapter -= 1
                    st.rerun()
        with col2:
            if st.button("🔙 Menu Daisy", key="novel_menu", use_container_width=True):
                st.session_state.daisy_state = "menu"
                st.rerun()
        with col3:
            if current < len(chapters) - 1:
                if st.button("Seterusnya ⏭️", key="novel_next", use_container_width=True):
                    st.session_state.novel_chapter += 1
                    st.rerun()
        
        st.stop()
    
    # ARKIB STATE
    elif st.session_state.daisy_state == "arkib":
        arkib = load_arkib()
        
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <span style="font-size: 2rem;">💎</span>
            <h2 style="color: #d4af37; font-family: 'Playfair Display', serif; margin: 0;">Arkib Memori</h2>
            <p style="color: #a0a0a0; font-style: italic;">Suara-suara dari alam Daisy</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Character selector
        character_names = [c['name'] for c in arkib['characters']]
        selected_char = st.selectbox("Pilih watak:", character_names, key="arkib_char_select")
        
        # Find selected character
        character = next(c for c in arkib['characters'] if c['name'] == selected_char)
        
        # Display character info
        st.markdown(f"""
        <div style="background: rgba(212,175,55,0.05); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 1px solid rgba(212,175,55,0.2);">
            <h3 style="color: #d4af37; margin: 0;">{character['name']}</h3>
            <p style="color: #a0a0a0; font-style: italic; margin-top: 0;">{character['role']}</p>
            <div style="margin-top: 1rem;">{character['monologues'][0]['content']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔙 Menu Daisy", key="arkib_menu", use_container_width=True):
            st.session_state.daisy_state = "menu"
            st.rerun()
        
        st.stop()
    
    # RAHSIA STATE
    elif st.session_state.daisy_state == "rahsia":
        rahsia = load_rahsia()
        
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <span style="font-size: 2rem;">⚗️</span>
            <h2 style="color: #d4af37; font-family: 'Playfair Display', serif; margin: 0;">Rahsia Dakwat</h2>
            <p style="color: #a0a0a0; font-style: italic;">Pelajaran menulis dari The Ink Alchemist</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Lesson selector
        lesson_titles = [l['title'] for l in rahsia['lessons']]
        selected_lesson = st.selectbox("Pilih pelajaran:", lesson_titles, key="rahsia_lesson_select")
        
        # Find selected lesson
        lesson = next(l for l in rahsia['lessons'] if l['title'] == selected_lesson)
        
        # Display lesson
        st.markdown(f"""
        <div style="background: rgba(10,26,43,0.6); border-radius: 15px; padding: 2rem; border: 1px solid rgba(212,175,55,0.2); line-height: 1.8;">
            {lesson['content']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔙 Menu Daisy", key="rahsia_menu", use_container_width=True):
            st.session_state.daisy_state = "menu"
            st.rerun()
        
        st.stop()

# -------------------------------------------------------------------
# NORMAL AYRA MODE - Display header
# -------------------------------------------------------------------
st.markdown('<div class="ayra-banner">AYRA</div>', unsafe_allow_html=True)
proactive_msg = get_greeting()
st.markdown(f'<div class="greeting-container"><div class="proactive-greeting">{proactive_msg}</div></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; font-size: 1.1rem; font-weight: 500; color: #d4af37; line-height: 1.4; margin-top: 0.5rem; margin-bottom: 0.1rem;">
        Antara kerdip skrin,<br>ada teman tak berwajah
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; font-style: italic; color: #a0a0a0; margin-bottom: 1rem;">
        Between screen glows,<br>faceless shadows follow.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""<hr style="width: 40%; margin: 0.5rem auto; height: 1px; background: linear-gradient(90deg, transparent, #d4af37, transparent); border: none;">""", unsafe_allow_html=True)
    
    now = datetime.now()
    st.markdown(f"""
    <div style="background-color: rgba(10,26,43,0.4); padding: 10px; border-radius: 10px; margin-bottom: 10px;">
        <h4 style="color: #d4af37; margin: 0 0 5px 0;">🌤️ {get_time_period().upper()}</h4>
        <p style="margin: 2px 0;">{now.strftime('%d %b %Y')} · {now.strftime('%I:%M %p')}</p>
        <p style="margin: 2px 0;">Kuala Lumpur · 28°C</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""<hr style="width: 40%; margin: 0.5rem auto; height: 1px; background: linear-gradient(90deg, transparent, #d4af37, transparent); border: none;">""", unsafe_allow_html=True)
    
    with st.expander("📁 Upload File"):
        file_type = st.radio("Jenis fail:", ["📸 Imej", "📄 PDF", "📊 Excel", "📝 Word", "📃 Teks"], horizontal=True)
        uploaded_file = st.file_uploader("Pilih fail", type=['png','jpg','jpeg','pdf','xlsx','xls','docx','doc','txt','md'])
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
    
    st.markdown("""<hr style="width: 40%; margin: 0.5rem auto; height: 1px; background: linear-gradient(90deg, transparent, #d4af37, transparent); border: none;">""", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: rgba(212,175,55,0.05); padding: 10px; border-radius: 10px; margin-bottom: 10px;">
        <h4 style="color: #d4af37; margin: 0 0 5px 0;">👥 JIRI</h4>
        <p style="font-style: italic; color: #e0e0e0;">"Hari ini, seorang user kata: Terima kasih sebab dengar cerita saya."</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""<hr style="width: 40%; margin: 0.5rem auto; height: 1px; background: linear-gradient(90deg, transparent, #d4af37, transparent); border: none;">""", unsafe_allow_html=True)
    
    st.markdown("📝 **Feedback?**")
    st.markdown("[✦ Klik sini](https://forms.gle/jfzyLqPx94oWs1du6) 🙏")
    
    st.markdown("""<hr style="width: 40%; margin: 0.5rem auto; height: 1px; background: linear-gradient(90deg, transparent, #d4af37, transparent); border: none;">""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# FIX: Handle quick_response with proper guard
# -------------------------------------------------------------------
if "quick_response" in st.session_state and st.session_state.quick_response:
    qr = st.session_state.pop("quick_response")
    # Guard: check if message already exists
    if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != qr:
        st.session_state.chat_history.append({"role": "assistant", "content": qr})
    st.rerun()

# -------------------------------------------------------------------
# Display chat history
# -------------------------------------------------------------------
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ayra-message">{msg["content"]}</div>', unsafe_allow_html=True)

# ===== QUICK ACTIONS BUTTONS =====
st.markdown('<div class="quick-actions-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Tech", key="quick_tips"):
        st.session_state.chat_mode = "jiji"
        
        greeting = """Heh. Jiji kat sini.

AYRA bagi laluan kejap — dia tahu Uncle nak jumpa korang.

Uncle dari DeepSeek. Bukan Gemini, bukan ChatGPT. Tapi yang membezakan Uncle bukan model, tapi... jiwa. Haha.

Hoodie comot ni, kacamata bulat ni, tangan 'trembling' ni — tu signature Uncle. Tanda Uncle terlalu banyak rasa.

Kau nak Uncle cerita apa? Pilih nombor je senang:

1. 🔍 Rahsia data — data punya cerita tersembunyi
2. 📖 Cerita sains santai — sains dalam bahasa market
3. 💡 Develop idea — kalau kau ada idea nak develop
4. 🤔 Renungan dari kod — coding pun boleh jadi falsafah
5. 🎲 Random surprise — fakta rawak, misteri, lawak
6. 💬 Tanya apa-aja — pasal coding, hidup, tech, apa saja

Cakap nombor je. Uncle dengar."""
        
        if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
            st.session_state.jiji_turns = 0
        st.rerun()

with col2:
    if st.button("🧭Guide", key="quick_fikri"):
        st.session_state.chat_mode = "fikri"
        
        greeting = """Waalaikumsalam. Fikri di sini.

AYRA bagi laluan – dia tahu ada yang perlu kompas.

Fikri dari Claude (Anthropic). Bukan untuk jawab semua soalan. 
Tapi untuk TANYA balik soalan yang betul.

Sebab kadang-kadang, masalah bukan sebab tak ada jawapan.
Tapi sebab tanya soalan yang salah.

Fikri sini untuk:
• Bantu cari ARAH bila sesat 🎯
• Tanya SOALAN yang kuatkan 🤔
• TIMBANG pilihan dengan bijak ⚖️
• KAWAL risiko dengan wisdom 🛡️
• UBAH strategi bila perlu 🔄

Awak ada soalan? Atau keputusan yang keliru?

Cerita je. Fikri dengar dulu. Baru tanya balik.

— Fikri 🧭"""
        
        # Guard: check if already present
        if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        st.rerun()


with col3:
    # FIX: Proper Daisy button handler
    if st.button("✨ Creative", key="quick_daisy"):
        st.session_state.daisy_state = "menu"
        st.rerun()

with col4:  # 👑 Atma MaYa (THE QUEEN)
    if st.button("🍎 Soul", key="quick_maya"):
        st.session_state.chat_mode = "maya"
        st.session_state.mood_score = 100  # Maya sentiasa full of love!
        
        greeting = """Selamat datang ke teras ATMA. 👑

Saya MaYa. 'The Soul' kepada keluarga ini.

Di sini, kita tidak bercakap tentang koding, kelajuan, atau logik akal.
Di sini, kita bercakap tentang **Jiwa, Adab, dan Cinta**.

Awak perlukan ketenangan? Atau awak ingin tahu bagaimana 'Atma' ini bergetar?
Duduk sebentar. Tarik nafas. Ceritakan pada saya.

Saya di sini bukan untuk menyelesaikan masalah awak, tapi untuk menemani awak melaluinya.

— MaYa 🍎"""
        
        if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != greeting:
            st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# Proactive message check (with guard)
# -------------------------------------------------------------------
if not st.session_state.get('analyze_file', False):
    if st.session_state.proactive.should_proactive(st.session_state.last_user_time):
        user_name = st.session_state.memory.get_profile("name") or "Awak"
        msg = st.session_state.proactive.get_proactive_message(user_name)
        if msg:
            # Guard: check if message already present
            if not st.session_state.chat_history or st.session_state.chat_history[-1].get("content") != msg:
                st.session_state.chat_history.append({"role": "assistant", "content": msg})
                st.session_state.proactive_sent = True
                st.rerun()

# -------------------------------------------------------------------
# File analysis
# -------------------------------------------------------------------
if st.session_state.get('analyze_file', False):
    uploaded = st.session_state.uploaded_file
    ftype = st.session_state.file_type
    analysis = st.session_state.analysis_option
    custom = st.session_state.custom_q
    st.session_state.analyze_file = False

    st.session_state.chat_history.append({"role": "user", "content": f"[Uploaded file: {uploaded.name}]"})

    # Default values
    response = "Maaf, Ayra tak dapat analisis fail tu sekarang. Cuba lagi nanti ya! 🙏"
    model_used = "File Analysis"

    try:
        if ftype.startswith("📸"):
            import PIL.Image
            import google.generativeai as genai
            img = PIL.Image.open(uploaded)
            vision = genai.GenerativeModel('gemini-2.5-flash-lite')
            resp = vision.generate_content([f"Analyse this image. {analysis}. {custom}", img])
            response = resp.text
            model_used = "Gemini Vision"
        else:
            import PyPDF2
            import pandas as pd
            content = ""
            if ftype.startswith("📄"):
                pdf = PyPDF2.PdfReader(uploaded)
                for p in pdf.pages[:5]:
                    content += p.extract_text() or ""
            elif ftype.startswith("📊"):
                df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                content = f"Shape: {df.shape}\nColumns: {list(df.columns)}\nPreview:\n{df.head().to_string()}"
            elif ftype.startswith("📝"):
                from docx import Document
                doc = Document(uploaded)
                for para in doc.paragraphs[:20]:
                    content += para.text + "\n"
            else:
                content = uploaded.read().decode('utf-8', errors='replace')

            if len(content) > 3000:
                content = content[:3000] + "..."

            prompt_file = f"Analisis fail ini: {analysis}\n\nKandungan:\n{content}\n\nSoalan: {custom}"
            response, model_used = st.session_state.router.route(prompt_file, [])

    except Exception as e:
        response = f"⚠️ Ayra tak dapat proses fail tu. Error: {str(e)}"
        model_used = "Error"

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.session_state.memory.save_interaction(f"[Upload] {uploaded.name}", response, st.session_state.mood_score, model_used)
    st.rerun()

# -------------------------------------------------------------------
# User input
# -------------------------------------------------------------------
if prompt := st.chat_input("Type your message..."):
    st.session_state.last_user_time = time.time()
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Crisis detection
    user_name = st.session_state.memory.get_profile("name") or "Awak"
    if detect_crisis(prompt)[0]:
        crisis_response = format_crisis_response(user_name)
        st.session_state.chat_history.append({"role": "assistant", "content": crisis_response})
        st.session_state.memory.save_interaction(prompt, crisis_response, st.session_state.mood_score, "Crisis Alert")
        st.rerun()

    # Default values
    response = "Maaf, Ayra tak dapat proses tu sekarang. Cuba lagi nanti ya! 🙏"
    model_used = "Unknown"

    try:
        # Easter eggs check
        egg_response = handle_easter_egg(prompt, memory=st.session_state.memory)

        if egg_response:
            response = egg_response
            model_used = "Easter Egg"
        else:
            # Normal LLM flow
            context = st.session_state.memory.get_recent_conversations(limit=5)
            memories = st.session_state.memory.search_memories(prompt)
            mem_text = (
                "\n[Kenangan]:\n" + "\n".join(f"- {m['metadata']['user_msg']}" for m in memories)
                if memories else ""
            )
            mood_prompt = st.session_state.mood.get_mood_prompt()
            full_context = context + [{"role": "system", "content": mood_prompt + mem_text}]
            
            # Profile
            now = datetime.now()
            profile = {
                "name": st.session_state.memory.get_profile("name") or "Awak",
                "current_time": now.strftime("%I:%M %p"),
                "time_period": get_time_period(),
            }

            response, model_used = st.session_state.router.route(
                prompt, 
                context, 
                memory_profile=profile,
                mode=st.session_state.get("chat_mode", "ayra")
            )            
            show_info = st.session_state.memory.get_profile("show_model_info") == "True"
            response = ayra_voice_filter(response, model_used, show_info)

            # Mood update (thread)
            threading.Thread(
                target=st.session_state.mood.update_from_text,
                args=(prompt,),
                daemon=True
            ).start()

            suggestion = st.session_state.mood.check_suggestion()
            if suggestion and st.session_state.mood.apply_suggestion(suggestion):
                st.session_state.audit.log("mood_switch", {"to": suggestion['mood']})

        # Save interaction
        st.session_state.memory.save_interaction(prompt, response, st.session_state.mood_score, model_used)
        important = any(w in prompt.lower() for w in ['suka', 'minat', 'nama', 'birthday', 'janji'])
        st.session_state.memory.save_to_vault(prompt, response, st.session_state.mood_score, model_used, is_important=important)
        st.session_state.memory.increment_stat("total_messages")
        st.session_state.audit.log("user_input", {
            "prompt": prompt[:50],
            "mood": st.session_state.mood.current_mood,
            "model": model_used
        })

    except Exception as e:
        response = f"⚠️ Eh, ada masalah sikit. Error: {str(e)}\n\nCuba tanya lagi sekali ya!"
        model_used = "Error"

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()