import re
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from chucklepy.fun import (
    generate_pun,
    comedic_insult,
    amuseify_text,
    random_fortune
)


def test_generate_pun1():
    assert generate_pun()

def test_generate_pun2():
    assert generate_pun(category="tech", length="medium") != generate_pun(category="tech", length="short")

def test_generate_pun3():
    assert isinstance(generate_pun(), str)


def test_comedic_insult_optimistic():
    assert "optimistic" in comedic_insult("Alice", severity=1)

def test_comedic_insult_maze():
    assert "maze" in comedic_insult("Bob", severity=2)

def test_comedic_insult_time_travelers():
    assert "time travelers" in comedic_insult("Charlie", severity=3)

def test_amuseify_text():
    assert isinstance(amuseify_text("Hello world", style="emoji"), str)

def test_amuseify_text_emoji():
    assert re.search(r"[😂🤣😜🤪🙃😊😎😫🤯😈👾]", amuseify_text("Hello world", style="emoji"))

def test_amuseify_text_leet():
    assert re.search(r"[413705]", amuseify_text("Hello world", style="leet"))

def test_random_fortune():
    assert random_fortune(topic="life", mood="positive") != random_fortune(topic="career", mood="sarcastic")

def test_random_fortune2():
    assert random_fortune(topic="career", mood="sarcastic")

def test_random_fortune3():
    assert isinstance(random_fortune("love", "positive"), str)

def test_generate_pun_valid_category():
    result = generate_pun(category="general", length="short")
    assert isinstance(result, str)
    assert len(result) > 0

def test_generate_pun_invalid_length():
    result = generate_pun(category="tech", length="long")
    assert isinstance(result, str)
    assert len(result) > 0

def test_generate_pun_random_category():
    result = generate_pun(category="random", length="short")
    assert isinstance(result, str)
    assert len(result) > 0

def test_generate_pun_edge_case():
    result = generate_pun(category="", length="medium")
    assert isinstance(result, str)
    assert len(result) > 0

def test_comedic_insult_valid_severity():
    result = comedic_insult("Alice", severity=2)
    assert isinstance(result, str)
    assert "Alice" in result

def test_comedic_insult_invalid_severity():
    """Test comedic_insult with an out-of-range severity."""
    result = comedic_insult("Bob", severity=9)
    assert isinstance(result, str)
    assert "Bob" in result

def test_comedic_insult_blank_name():
    result = comedic_insult("", severity=1)
    assert isinstance(result, str)

def test_comedic_insult_special_characters():
    result = comedic_insult("@L!ce_2024", severity=3)
    assert isinstance(result, str)
    assert "@L!ce_2024" in result

def test_amuseify_text_leet():
    result = amuseify_text("Testing Leet", style="leet")
    assert isinstance(result, str)
    assert any(char in result for char in ["7", "3", "1", "0"])

def test_amuseify_text_empty():
    result = amuseify_text("", style="emoji")
    assert result == ""

def test_random_fortune_valid():
    result = random_fortune(topic="life", mood="positive")
    assert isinstance(result, str)
    assert len(result) > 0

def test_random_fortune_invalid_topic():
    result = random_fortune(topic="unknown", mood="positive")
    assert isinstance(result, str)
    assert len(result) > 0

def test_random_fortune_invalid_mood():
    result = random_fortune(topic="career", mood="unknown")
    assert isinstance(result, str)
    assert len(result) > 0

def test_random_fortune_edge_case():
    result = random_fortune(topic="", mood="sarcastic")
    assert isinstance(result, str)
    assert len(result) > 0