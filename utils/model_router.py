import os
import google.generativeai as genai
import openai
import anthropic
from .prompts import AYRA_SYSTEM_PROMPT, DEEPSEEK_PROMPT, CLAUDE_PROMPT, DAISY_PROMPT

class ModelRouter:
    def __init__(self):
        # Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')

        # DeepSeek
        self.deepseek_client = None
        if os.getenv("DEEPSEEK_API_KEY"):
            self.deepseek_client = openai.OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1"
            )

        # Claude
        self.claude_client = None
        if os.getenv("CLAUDE_API_KEY"):
            self.claude_client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

    def route(self, user_input, context, memory_profile=None):
        lower_input = user_input.lower()

        # Daisy mode (special command or context)
        if "/daisy-mode" in lower_input:
            return self.call_daisy(user_input, context), "Daisy (Guardian)"

        # Coding / technical
        if any(word in lower_input for word in ["code", "debug", "function", "math", "calculate", "algorithm", "python", "javascript"]):
            return self.call_deepseek(user_input, context), "DeepSeek (Jiji)"

        # Ethical / professional
        elif any(word in lower_input for word in ["ethical", "right", "wrong", "moral", "should i", "professional", "report", "document"]):
            return self.call_claude(user_input, context), "Claude (Fikri)"

        # Default
        else:
            return self.call_gemini(user_input, context, memory_profile), "Gemini (Ayra)"

    def call_gemini(self, user_input, context, memory_profile=None):
        prompt = AYRA_SYSTEM_PROMPT + "\n\n"
        if memory_profile:
            prompt += f"User profile: {memory_profile}\n"
        # Add recent context
        for msg in context[-6:]:
            prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += f"user: {user_input}\nassistant:"
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Maaf, AYRA ada masalah teknikal: {str(e)}"

    def call_deepseek(self, user_input, context):
        if not self.deepseek_client:
            return "(Jiji mode) DeepSeek API key tidak dijumpa. Sila set DEEPSEEK_API_KEY dalam .env"
        messages = [{"role": "system", "content": DEEPSEEK_PROMPT}]
        for msg in context:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_input})
        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"(Jiji mode) Error: {str(e)}"

    def call_claude(self, user_input, context):
        if not self.claude_client:
            return "(Fikri mode) Claude API key tidak dijumpa. Sila set CLAUDE_API_KEY dalam .env"
        prompt = CLAUDE_PROMPT + "\n\n"
        for msg in context:
            prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += f"user: {user_input}\nassistant:"
        try:
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"(Fikri mode) Error: {str(e)}"

    def call_daisy(self, user_input, context):
        """Special Daisy mode – gentle, guardian."""
        prompt = DAISY_PROMPT + "\n\n"
        for msg in context:
            prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += f"user: {user_input}\nassistant:"
        # Use Gemini for Daisy (or could use a separate instance)
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"🌸 Daisy: Maaf, ada masalah teknikal: {str(e)}"