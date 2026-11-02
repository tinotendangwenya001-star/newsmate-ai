"""Newsroom tasks: translate, summarise, draft, headline, social posts."""
from .llm import ask, ask_json

LANGUAGES = {"English": "English", "Shona": "Shona (chiShona)", "Ndebele": "isiNdebele (Zimbabwean)"}

EDITORIAL_RULES = (
    "You assist a Zimbabwean newsroom. Use ONLY facts present in the material provided. "
    "Never invent names, numbers, quotes, places or dates. If something is unclear, say so. "
    "Keep quotes exactly as spoken. Use a neutral, accurate news tone."
)


def translate(text: str, target: str) -> str:
    system = (
        EDITORIAL_RULES
        + f" Translate into {LANGUAGES[target]}. Keep names, numbers and [mm:ss] timestamps unchanged. "
        "If you are unsure about a word or phrase, keep the original in square brackets. "
        "Output the translation only."
    )
    return ask(system, text, max_tokens=4000)


def summarise(text: str) -> str:
    system = EDITORIAL_RULES + " Summarise in 5 concise bullet points covering the key facts and quotes."
    return ask(system, text, max_tokens=800)


def build_package(transcript: str, notes: str = "", beat: str = "general news") -> dict:
    """One call that returns everything the journalist needs to review."""
    system = (
        EDITORIAL_RULES
        + " Return JSON with keys: "
        '"headlines" (list of 3 options), "article" (150-300 words, inverted pyramid, '
        "put a [mm:ss] timestamp after every fact or quote taken from the transcript), "
        '"facebook" (post with 1-2 hashtags), "x_post" (under 270 characters), '
        '"whatsapp" (short message with emoji, plain text), '
        '"open_questions" (list of facts the editor should verify or details missing).'
    )
    user = f"Beat: {beat}\n\nJournalist notes:\n{notes or '(none)'}\n\nTranscript:\n{transcript}"
    return ask_json(system, user, max_tokens=3500)
