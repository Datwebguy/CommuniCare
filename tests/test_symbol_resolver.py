"""
Unit tests for the AAC Symbol Library & Resolver.
Verifies ARASAAC catalog matching, Fitzgerald color assignment, and graceful text fallbacks.
"""

import pytest
from communicare.services.symbol_library import symbol_resolver, SymbolResolver, FITZGERALD_PALETTE
from communicare.models import GrammarCategory, SymbolSource


def test_symbol_resolver_direct_match():
    """Verify exact match returns correct category, SVG icon, and ARASAAC metadata."""
    card = symbol_resolver.resolve_concept("medicine")
    assert card.word == "MEDICINE"
    assert card.category == GrammarCategory.NOUN
    assert card.color_code == FITZGERALD_PALETTE[GrammarCategory.NOUN][0]
    assert card.bg_color == FITZGERALD_PALETTE[GrammarCategory.NOUN][1]
    assert card.svg_icon is not None
    assert card.is_fallback is False
    assert card.confidence == 1.0


def test_symbol_resolver_synonym_match():
    """Verify synonyms (e.g., 'pills') correctly resolve to dynamic ARASAAC pictograms."""
    card = symbol_resolver.resolve_concept("pills")
    assert card.word == "PILLS"
    assert card.category == GrammarCategory.NOUN
    assert (card.image_url is not None or card.svg_icon is not None)
    assert card.is_fallback is False


def test_symbol_resolver_verb_and_people():
    """Verify verb (walk, eat) and people (doctor) categories."""
    walk_card = symbol_resolver.resolve_concept("walk")
    assert walk_card.category == GrammarCategory.VERB
    assert walk_card.color_code == FITZGERALD_PALETTE[GrammarCategory.VERB][0]

    doctor_card = symbol_resolver.resolve_concept("doctor")
    assert doctor_card.category == GrammarCategory.PEOPLE
    assert doctor_card.color_code == FITZGERALD_PALETTE[GrammarCategory.PEOPLE][0]


def test_symbol_resolver_graceful_text_fallback():
    """Verify uncatalogued concept gracefully falls back to text card without error."""
    card = symbol_resolver.resolve_concept("astrophysics")
    assert card.word == "ASTROPHYSICS"
    assert card.is_fallback is True
    assert card.source == SymbolSource.TEXT_FALLBACK
    assert card.subtext == "Text Card"
    assert card.color_code is not None


def test_symbol_search():
    """Verify symbol search endpoint logic."""
    results = symbol_resolver.search_symbols("water", limit=5)
    assert len(results) >= 1
    assert any(r["id"] == "water" for r in results)
