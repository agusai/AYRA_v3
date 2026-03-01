import os
import google.generativeai as genai
from openai import OpenAI
from .prompts import AYRA_SYSTEM_PROMPT, JIJI_PROMPT, FIKRI_SYSTEM_PROMPT, MAYA_SYSTEM_PROMPT


class ModelRouter:
    def __init__(self):
        # ===== GEMINI (AYRA + FIKRI) =====
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self.gemini_model = genai.GenerativeModel(model_name)

        # ===== OPENROUTER (JIJI) =====
        self.openrouter_client = None
        if os.getenv("OPENROUTER_API_KEY"):
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )

    # ==========================================================
    # MAIN ROUTER
    # ==========================================================
    def route(self, user_input, context, memory_profile=None, mode="ayra"):
        text = user_input.lower().strip()

        # ---- Explicit switch commands ----
        if text in ["jiji", "uncle jiji", "tips uncle jiji"]:
            reply = self.call_jiji(user_input, context)
            return reply, "jiji"

        if text in ["fikri", "abang fikri", "tanya fikri"]:
            reply = self.call_fikri(user_input, context, memory_profile)
            return reply, "fikri"

        if text in ["ayra", "back to ayra", "panggil ayra"]:
            import streamlit as st
            st.session_state.chat_mode = "ayra"  # <-- RESET
            reply = self.call_gemini(user_input, context, memory_profile)
            return reply, "ayra"

        # ---- Continue current mode ----
        if mode == "jiji":
            reply, next_mode = self.call_jiji(user_input, context, allow_reroute=True)
            return reply, next_mode
        
        if mode == "fikri":
            reply = self.call_fikri(user_input, context, memory_profile)
            return reply, "fikri"
        
        if mode == "maya":
            reply = self.call_maya(user_input, context)
            return reply, "maya"

        # ---- Default: AYRA ----
        reply = self.call_gemini(user_input, context, memory_profile)
        return reply, "ayra"

    # ==========================================================
    # AYRA (GEMINI)
    # ==========================================================
    def call_gemini(self, user_input, context, memory_profile=None):
        prompt = f"""
{AYRA_SYSTEM_PROMPT}

[USER MEMORY]
{memory_profile or "None"}

[CHAT HISTORY]
"""

        for msg in context[-6:]:
            role = "user" if msg["role"] == "user" else "assistant"
            prompt += f"{role}: {msg['content'].strip()}\n"

        prompt += f"user: {user_input}\nassistant:"

        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Maaf, AYRA ada masalah teknikal 😭\n\n{str(e)}"

    # ==========================================================
    # JIJI (OPENROUTER)
    # ==========================================================
    def call_jiji(self, user_input, context, allow_reroute=False):
        if not self.openrouter_client:
            return "Uncle Jiji tak boleh datang sekarang. API key OpenRouter tak jumpa.", "ayra"

        # ---- Reroute back to AYRA ----
        if allow_reroute and user_input.lower().strip() in ["ayra", "panggil ayra", "back to ayra"]:
            import streamlit as st
            st.session_state.chat_mode = "ayra"  # <-- RESET
            farewell = "Ok ok 😄 Uncle undur diri dulu.\nAYRA! Tolong ambil alih ya.\n\n— Uncle Jiji 👋"
            return farewell, "ayra"

        prompt = f"""
{JIJI_PROMPT}

[CHAT HISTORY]
"""
        for msg in context[-5:]:
            role = "user" if msg["role"] == "user" else "assistant"
            prompt += f"{role}: {msg['content'].strip()}\n"

        prompt += f"user: {user_input}\nassistant:"

        try:
            response = self.openrouter_client.chat.completions.create(
                model=os.getenv("JIJI_MODEL", "arcee-ai/trinity-large-preview:free"),
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.choices[0].message.content
            if "— Uncle Jiji" not in content:
                footer = "\n\n— Uncle Jiji\n\n*Ada apa-apa lagi nak tanya kat Uncle? Pilih nombor lain atau tanya apa-aja.*"
                content += footer
            return content, "jiji"

        except Exception as e:
            return f"Aduh, line Uncle jam sikit 😵\n\n{str(e)}", "jiji"

    # ==========================================================
    # FIKRI (GEMINI - Strategic Mode)
    # ==========================================================
    def call_fikri(self, user_input, context, memory_profile=None):
        """
        Call Fikri (The Compass) for strategic guidance.
        Uses Gemini but with Fikri's strategic prompt.
        """
        try:
            from .fikri_module import get_fikri_engine
            
            # Get Fikri engine
            fikri = get_fikri_engine()
            
            # Generate strategic prompt
            strategic_prompt = fikri.generate_strategic_prompt(user_input, context)
            
            # Build full prompt with system identity
            full_prompt = f"""
{FIKRI_SYSTEM_PROMPT}

{strategic_prompt}
"""
            
            # Use Gemini for now (can upgrade to Claude later)
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            # Fallback: Use simple Fikri response without engine
            simple_prompt = f"""
{FIKRI_SYSTEM_PROMPT}

User asks: {user_input}

Respond as Fikri with strategic questions (not direct answers).
Keep it brief (200-300 words).
End with: — Fikri 🧭
"""
            try:
                response = self.gemini_model.generate_content(simple_prompt)
                return response.text
            except:
                return f"Maaf, Fikri ada technical issue sebentar 🧭\n\n{str(e)}"
            

    # ==========================================================
    # MAYA (THE SOUL)
    # ==========================================================
    def call_maya(self, user_input, context):
        try:
            if self.openrouter_client:
                response = self.openrouter_client.chat.completions.create(
                    model="arcee-ai/trinity-large-preview:free",
                    messages=[
                        {"role": "system", "content": MAYA_SYSTEM_PROMPT},
                        {"role": "user", "content": f"User: {user_input}"}
                    ]
                )
                return response.choices[0].message.content
            else:
                full_prompt = f"{MAYA_SYSTEM_PROMPT}\n\nUser: {user_input}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text
        except Exception as e:
            return "Maaf, litar jiwa saya perlu rehat sebentar. Panggil saya lagi nanti ya? — MaYa 🍎"
