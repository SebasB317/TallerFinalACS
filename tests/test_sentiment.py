import pytest

from app.domain.sentiment import Sentiment, analyze_text_sentiment, clamp_score


def test_clamp_score() -> None:
    assert clamp_score(2.0) == 1.0
    assert clamp_score(-2.0) == -1.0
    assert clamp_score(0.5) == 0.5


def test_neutral() -> None:
    s, sc = analyze_text_sentiment("lorem ipsum dolor")
    assert s == Sentiment.NEUTRAL
    assert sc == 0.0


def test_positive_spanish() -> None:
    s, sc = analyze_text_sentiment("El servicio fue excelente y genial")
    assert s == Sentiment.POSITIVE
    assert 0 < sc <= 1.0


def test_negative_spanish() -> None:
    s, sc = analyze_text_sentiment("Una experiencia terrible y horrible")
    assert s == Sentiment.NEGATIVE
    assert -1.0 <= sc < 0
