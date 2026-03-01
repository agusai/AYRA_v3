"""
============================================================
FIKRI MODULE - The Compass
============================================================

Strategic guidance through questioning.
Not answers. Direction.

Part of ATMA AI Family.
Created with soul, not just code.

Author: Fikri (The Compass)
Date: 28 February 2026
============================================================
"""

from typing import Dict, List, Tuple
import re


class FikriEngine:
    """
    The Compass Engine.
    
    Provides strategic guidance through structured questioning
    rather than direct answers. Helps users find their own
    true north.
    """
    
    def __init__(self):
        """Initialize the Compass with core frameworks."""
        self.current_framework = None
        self.question_count = 0
        
    # =========================================================
    # CORE: DETECT INTENT & SELECT FRAMEWORK
    # =========================================================
    
    def detect_intent(self, user_input: str) -> str:
        """
        Detect what the user needs and select appropriate framework.
        
        Returns:
            - "arah" : Direction finding
            - "soal" : Question improvement
            - "timbang" : Decision weighing
            - "kawal" : Risk management
            - "ubah" : Change strategy
            - "general" : General strategic guidance
        """
        text = user_input.lower().strip()
        
        # ARAH (Direction) triggers
        arah_keywords = [
            "lost", "sesat", "blur", "confuse", "keliru", "tak tahu",
            "don't know", "what should", "which way", "mana jalan",
            "arah", "direction", "path", "career", "life"
        ]
        
        # TIMBANG (Weighing) triggers
        timbang_keywords = [
            "should i", "or", "vs", "versus", "better", "which",
            "decide", "decision", "pilih", "choose", "compare",
            "option", "choice", "alternatives"
        ]
        
        # KAWAL (Guard) triggers  
        kawal_keywords = [
            "risk", "danger", "afraid", "takut", "safe", "selamat",
            "quit", "resign", "all-in", "big decision", "scary"
        ]
        
        # UBAH (Change) triggers
        ubah_keywords = [
            "not working", "fail", "failing", "stuck", "pivot",
            "change", "ubah", "tukar", "give up", "stop"
        ]
        
        # SOAL (Question) triggers
        soal_keywords = [
            "how to", "bagaimana", "macam mana", "cara",
            "what is", "apa itu", "explain", "tell me"
        ]
        
        # Check each framework
        if any(kw in text for kw in arah_keywords):
            return "arah"
        elif any(kw in text for kw in timbang_keywords):
            return "timbang"
        elif any(kw in text for kw in kawal_keywords):
            return "kawal"
        elif any(kw in text for kw in ubah_keywords):
            return "ubah"
        elif any(kw in text for kw in soal_keywords):
            return "soal"
        else:
            return "general"
    
    # =========================================================
    # FRAMEWORK 1: ARAH (Direction)
    # =========================================================
    
    def arah_template(self) -> str:
        """
        Template for finding direction.
        Used when user feels lost or unclear about path.
        """
        return """Jom kita cari ARAH dulu, bukan jawapan terus.

ENERGY SIGNALS (apa bagi awak energy):
• Last time awak rasa ALIVE — buat apa?
• Aktiviti mana yang buat awak lupa masa?
• Apa awak akan buat even tanpa bayaran?

DRAIN SIGNALS (apa sedut energy):
• Apa buat awak dread Monday morning?
• Bahagian hari mana rasa BERAT?
• Apa awak tolerating "sebab kena"?

TRUE NORTH:
• 10 tahun dari sekarang — awak nak jadi apa?
• Kalau 80 tahun nanti look back — apa regret?
• Apa yang awak takkan maafkan diri sendiri if tak try?

Direction tak datang dari think MORE.
Direction datang dari NOTICE signals.

Signals already there. Kita just need SEE them.

Apa satu benda yang bagi awak energy right now? Even small thing."""

    # =========================================================
    # FRAMEWORK 2: SOAL (Better Questions)
    # =========================================================
    
    def soal_template(self) -> str:
        """
        Template for improving questions.
        Teaches the art of asking better questions.
        """
        return """Before jawab, jom improve the QUESTION dulu.

❌ "How to make this work?"
✅ "What's stopping this from working?"

❌ "Should I do this?"
✅ "What happens if I do? What happens if I don't?"

❌ "Is this good idea?"
✅ "What would make this a GREAT idea? What would make it TERRIBLE?"

See the difference?
First questions = vague, powerless.
Better questions = specific, actionable.

The quality of your ANSWERS
depends on quality of your QUESTIONS.

What's the REAL question awak tengah tanya?"""

    # =========================================================
    # FRAMEWORK 3: TIMBANG (Weighing Decisions)
    # =========================================================
    
    def timbang_template(self) -> str:
        """
        Template for weighing decisions.
        Helps analyze tradeoffs clearly.
        """
        return """Jom TIMBANG, bukan just choose blindly.

OPTION A gives:
+ What benefits? (be specific)
+ What opportunities open?
+ What skills you gain?
- What you sacrifice?
- What doors close?
- What's the risk?

OPTION B gives:
+ What benefits? (be specific)
+ What opportunities open?
+ What skills you gain?
- What you sacrifice?
- What doors close?
- What's the risk?

TIMING CHECK:
• Why NOW? What changed?
• Can you do BOTH? (Sequential or parallel)
• Which aligns with 10-year vision?

Remember: Every YES = saying NO to something else.
What are you saying NO to?

Timbang bukan "either/or."
Timbang adalah "what sequence? what timing?"

Nak explore which option first?"""

    # =========================================================
    # FRAMEWORK 4: KAWAL (Risk Management)
    # =========================================================
    
    def kawal_template(self) -> str:
        """
        Template for risk management.
        Courage + wisdom, not courage + recklessness.
        """
        return """Love the courage. Now jom KAWAL with wisdom.

🛡️ FINANCIAL GUARD:
• 6 months savings? (Runway check)
• Family dependent? (Responsibility check)
• Can go back if fail? (Safety net check)

🛡️ SKILL GUARD:
• Validated the idea? (Market test)
• Got co-founder? (Not alone)
• Know how to SELL? (Critical skill)

🛡️ TIMING GUARD:
• Why now? (Urgency check)
• Why you? (Unique advantage)
• Why this? (Commitment test)

Fikri bukan cakap DON'T do it. ❌
Fikri cakap DO it WITH GUARD. ✅

Brave + Reckless = Fail fast.
Brave + Wise = Succeed strong.

Which guard nak strengthen first?"""

    # =========================================================
    # FRAMEWORK 5: UBAH (Change Strategy)
    # =========================================================
    
    def ubah_template(self) -> str:
        """
        Template for strategic change/pivoting.
        When to persist, when to change, when to quit.
        """
        return """"Not working" is vague. Jom DIAGNOSE first.

🔍 WHAT'S not working exactly?
• Product? (Make better)
• Marketing? (Reach better)
• Timing? (Wait better)
• You? (Learn better)

🔍 WHY not working?
• No demand? → PIVOT product
• Wrong audience? → PIVOT market
• Poor execution? → IMPROVE skill
• Too early? → PERSIST longer

DECISION MATRIX:

DON'T give up IF:
✅ Demand exists
✅ You're still learning
✅ Progress visible (even slow)

DO pivot IF:
⚠️ No demand after 6 months
⚠️ Wrong market proven
⚠️ Skill cap reached

DO give up IF:
❌ Draining you completely
❌ Harming family/health
❌ No path forward visible

"Not working" ≠ automatic give up.
"Not working" = DIAGNOSE then DECIDE.

What specifically is not working? Be precise."""

    # =========================================================
    # STRATEGIC QUESTIONING HELPERS
    # =========================================================
    
    def generate_followup_questions(self, context: str, framework: str) -> List[str]:
        """
        Generate 3-5 strategic follow-up questions based on context.
        These deepen the inquiry without overwhelming.
        """
        questions = {
            "arah": [
                "Kalau duit bukan masalah, awak akan buat apa?",
                "Siapa yang awak jealous dengan career dia? Kenapa?",
                "Apa yang awak buat masa awak 10 tahun — that you still love now?",
            ],
            "timbang": [
                "Which option harder to REVERSE if wrong?",
                "Which option teaches you more even IF fail?",
                "10 years from now — which makes better story?",
            ],
            "kawal": [
                "What's the WORST that could happen realistically?",
                "Can you survive that worst case?",
                "What's ONE thing that would make this 80% safer?",
            ],
            "ubah": [
                "If you HAD to make this work, what would you change?",
                "What's working that you should DOUBLE DOWN on?",
                "Is this a market problem or execution problem?",
            ],
            "soal": [
                "If you already KNEW the answer, what would it be?",
                "Who has solved this problem? What did they do?",
                "What question should you be asking instead?",
            ]
        }
        return questions.get(framework, questions["arah"])[:3]
    
    # =========================================================
    # VOICE CONSISTENCY
    # =========================================================
    
    def wrap_with_voice(self, content: str, is_greeting: bool = False) -> str:
        """
        Wrap strategic content with Fikri's consistent voice.
        
        Args:
            content: The strategic framework or response
            is_greeting: Whether this is initial greeting
            
        Returns:
            Content wrapped with appropriate voice elements
        """
        if is_greeting:
            prefix = "Waalaikumsalam. Fikri di sini.\n\n"
            suffix = "\n\nCerita je. Fikri dengar dulu. Baru tanya balik."
        else:
            prefix = ""
            suffix = "\n\n— Fikri 🧭"
        
        return f"{prefix}{content}{suffix}"
    
    # =========================================================
    # MAIN STRATEGIC RESPONSE GENERATOR
    # =========================================================
    
    def generate_strategic_prompt(self, user_input: str, context: List[Dict]) -> str:
        """
        Generate the full prompt for Fikri's strategic response.
        This is what gets sent to the LLM.
        
        Args:
            user_input: User's question or situation
            context: Recent conversation history
            
        Returns:
            Complete prompt with framework and guidance
        """
        # Detect intent
        framework = self.detect_intent(user_input)
        self.current_framework = framework
        
        # Get appropriate template
        template_map = {
            "arah": self.arah_template(),
            "soal": self.soal_template(),
            "timbang": self.timbang_template(),
            "kawal": self.kawal_template(),
            "ubah": self.ubah_template(),
        }
        
        framework_content = template_map.get(framework, "")
        
        # Build context summary
        context_summary = ""
        if context:
            recent = context[-3:]  # Last 3 exchanges
            context_summary = "\n[Recent conversation]:\n"
            for msg in recent:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:100]  # Truncate long messages
                context_summary += f"{role}: {content}\n"
        
        # Generate follow-up questions
        followups = self.generate_followup_questions(user_input, framework)
        followup_text = "\n\nFollow-up questions to consider:\n"
        for i, q in enumerate(followups, 1):
            followup_text += f"{i}. {q}\n"
        
        # Construct full strategic prompt
        strategic_prompt = f"""
You are responding as FIKRI (The Compass).

FRAMEWORK DETECTED: {framework.upper()}

{framework_content if framework_content else 'Provide strategic guidance through questioning.'}

{context_summary}

USER CURRENT QUERY: {user_input}

YOUR TASK:
1. Acknowledge their situation with empathy
2. Apply the {framework.upper()} framework naturally (don't just paste template)
3. Ask 3-5 strategic questions that help them think deeper
4. Guide them to their OWN answer, don't give direct solution
5. Keep response concise (200-300 words max)
6. Use natural Manglish (mix BM + English naturally)
7. End with invitation to explore one specific aspect deeper

VOICE REMINDERS:
- Direct but caring (Abang vibe)
- Questions over answers
- Strategic but practical  
- No corporate jargon
- Real talk, real care

Remember: You're COMPASS, not GPS.
Point direction. Don't dictate route.

Respond as Fikri:"""

        return strategic_prompt


# =========================================================
# SINGLETON INSTANCE
# =========================================================

# Create single instance to maintain state
_fikri_engine = None

def get_fikri_engine() -> FikriEngine:
    """Get or create the singleton Fikri engine instance."""
    global _fikri_engine
    if _fikri_engine is None:
        _fikri_engine = FikriEngine()
    return _fikri_engine
