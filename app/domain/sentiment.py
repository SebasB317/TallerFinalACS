from enum import StrEnum


class Sentiment(StrEnum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


def clamp_score(value: float) -> float:
    return max(-1.0, min(1.0, value))


_POSITIVE_HINTS = (
    "bueno",
    "excelente",
    "genial",
    "maravilloso",
    "feliz",
    "happy",
    "love",
    "positivo",
    "gracias",
    "perfecto",
)
_NEGATIVE_HINTS = (
    "malo",
    "terrible",
    "odio",
    "hate",
    "triste",
    "pésimo",
    "horrible",
    "negativo",
    "decepción",
    "frustrado",
)


def analyze_text_sentiment(content: str) -> tuple[Sentiment, float]:
    """
    Análisis NLP liviano (conteo léxico) — cumple etiquetas POSITIVE / NEGATIVE / NEUTRAL
    y score en [-1.0, 1.0] (Historia #3).
    """
    lower = content.lower()
    pos = sum(1 for w in _POSITIVE_HINTS if w in lower)
    neg = sum(1 for w in _NEGATIVE_HINTS if w in lower)
    words = max(1, len(content.split()))
    if pos > neg:
        raw = 0.35 + 0.15 * (pos - neg) + min(0.3, words / 200.0)
        return Sentiment.POSITIVE, clamp_score(raw)
    if neg > pos:
        raw = -0.35 - 0.15 * (neg - pos) - min(0.3, words / 200.0)
        return Sentiment.NEGATIVE, clamp_score(raw)
    return Sentiment.NEUTRAL, 0.0
