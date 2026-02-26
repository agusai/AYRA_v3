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
if "last_activity" not in st.session_state:
    st.session_state.last_activity = []
if "fatigue" not in st.session_state:
    st.session_state.fatigue = False
if "fatigue_until" not in st.session_state:
    st.session_state.fatigue_until = 0
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
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Display header
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
        <h4 style="color: #d4af37; margin: 0 0 5px 0;">🌤️ MALAM INI</h4>
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
    
    st.caption("Dibina dengan ❤️ di Malaysia")

# -------------------------------------------------------------------
# Handle quick_response with guard
# -------------------------------------------------------------------
if "quick_response" in st.session_state:
    qr = st.session_state.pop("quick_response")
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
    if st.button("💡 Tips Uncle Jiji", key="quick_tips"):
        tip_title, tip_content = get_tips_jiji()
        st.session_state.quick_response = f"**{tip_title}**\n\n{tip_content}\n\n— Uncle Jiji"
        st.rerun()

with col2:
    if st.button("📰 Berita Semasa", key="quick_news"):
        st.session_state.quick_response = "🔍 **Berita Semasa**\n\nFitur ni akan aktif soon! AYRA tengah sambungkan dengan API berita Malaysia. Nanti user boleh dapat update terkini terus dari sini. Stay tuned! 🚀"
        st.rerun()

with col3:
    if st.button("🚀 Update ATMA", key="quick_atma"):
        st.session_state.quick_response = "🚀 **Update ATMA**\n\n✨ AYRA 3.0 dah live!\n👥 Jiji, Fikri, Daisy, Laila, Aiman semua aktif\n🌙 Mama Maya still jadi 'Soul'\n👑 Abang Agus – The Architect\n\n*Next: Voice integration & Chroma memory!*"
        st.rerun()

with col4:
    if st.button("📈 Trending", key="quick_trending"):
        st.session_state.quick_response = "📈 **Trending Malaysia**\n\n#HargaMinyakNaikLagi\n#ViralVideoTiktok\n#KonsertJKT48\n#BanjirKelantan\n#PromosiShopee\n\n*Fitur carian real-time akan datang!*"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# Proactive message check (with guard)
# -------------------------------------------------------------------
if not st.session_state.fatigue and not st.session_state.get('analyze_file', False):
    if st.session_state.proactive.should_proactive(st.session_state.last_user_time):
        user_name = st.session_state.memory.get_profile("name") or "Abang/Sayang"
        msg = st.session_state.proactive.get_proactive_message(user_name)
        if msg:
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
    user_name = st.session_state.memory.get_profile("name") or "Abang/Sayang"
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
            profile = {"name": st.session_state.memory.get_profile("name")}

            response, model_used = st.session_state.router.route(prompt, full_context, memory_profile=profile)
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