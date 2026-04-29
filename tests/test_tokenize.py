#!/usr/bin/env python3
"""Tests for tokenize.py - indentation-aware tokenizer"""

import sys
sys.path.insert(0, 'src')

from hiuh.tokenize import tokenize

def test_simple_set():
    """sätt x till 5"""
    lines = list(tokenize("sätt x till 5"))
    indent, tokens = lines[0]
    assert indent == 0
    assert tokens == ['SET', 'x', 'TILL', '5']

def test_multiple_lines():
    """Multiple lines with indentation"""
    src = """sätt x till 5
sätt y till 10"""
    lines = list(tokenize(src))
    assert len(lines) == 2
    assert lines[0] == (0, ['SET', 'x', 'TILL', '5'])
    assert lines[1] == (0, ['SET', 'y', 'TILL', '10'])

def test_for_loop():
    """för x från 0 till 10"""
    src = """för x från 0 till 10
    skriv x"""
    lines = list(tokenize(src))
    assert len(lines) == 2
    assert lines[0] == (0, ['FOR', 'x', 'FRAN', '0', 'TILL', '10'])
    assert lines[1] == (1, ['SKRIV', 'x'])

def test_if_statement():
    """om x är 0"""
    src = """om x är 0
    skriv x"""
    lines = list(tokenize(src))
    assert len(lines) == 2
    assert lines[0] == (0, ['IF', 'x', 'AR', '0'])
    assert lines[1] == (1, ['SKRIV', 'x'])

def test_space_friendly_skriv_ny_rad():
    """skriv ny rad x"""
    lines = list(tokenize("skriv ny rad x"))
    indent, tokens = lines[0]
    assert tokens == ['SKRIV_NL', 'x']

def test_space_friendly_jag_ga_nu():
    """jag gå nu"""
    lines = list(tokenize("jag gå nu"))
    indent, tokens = lines[0]
    assert tokens == ['EXIT']

def test_hej_da():
    """hej då"""
    lines = list(tokenize("hej då"))
    indent, tokens = lines[0]
    assert tokens == ['EXIT']

def test_indentation_levels():
    """Nested indentation"""
    src = """för i från 0 till 10
    om i är 5
        skriv i
hej då"""
    lines = list(tokenize(src))
    assert lines[0] == (0, ['FOR', 'i', 'FRAN', '0', 'TILL', '10'])
    assert lines[1] == (1, ['IF', 'i', 'AR', '5'])
    assert lines[2] == (2, ['SKRIV', 'i'])
    assert lines[3] == (0, ['EXIT'])  # hej då at indent 0 (program exit)

def test_list_len():
    """antal element i x → LIST_LEN"""
    lines = list(tokenize("antal element i x"))
    indent, tokens = lines[0]
    assert tokens == ['LIST_LEN', 'x'], f"Got {tokens}"

def test_file_open_read():
    """öppna X för läsning → FILE_OPEN"""
    lines = list(tokenize("öppna data.txt för läsning"))
    indent, tokens = lines[0]
    assert tokens == ['FILE_OPEN', 'data.txt', 'r'], f"Got {tokens}"

def test_file_open_write():
    """öppna X för skrivning → FILE_OPEN"""
    lines = list(tokenize("öppna output.txt för skrivning"))
    indent, tokens = lines[0]
    assert tokens == ['FILE_OPEN', 'output.txt', 'w'], f"Got {tokens}"

def test_file_write():
    """skriv till fil X → FILE_WRITE"""
    lines = list(tokenize("skriv till fil resultat.txt"))
    indent, tokens = lines[0]
    assert tokens == ['FILE_WRITE', 'resultat.txt'], f"Got {tokens}"

def test_keyword_as_variable_after_set():
    """Keywords like 'tecken' should work as variable names after 'sätt'"""
    lines = list(tokenize("sätt tecken till 0"))
    indent, tokens = lines[0]
    assert tokens == ['SET', 'tecken', 'TILL', '0'], f"Got {tokens}"

def test_keyword_as_variable_case_preserved():
    """Variable names preserve case after 'sätt'"""
    lines = list(tokenize("Sätt Tecken Till 0"))
    indent, tokens = lines[0]
    assert tokens == ['SET', 'Tecken', 'TILL', '0'], f"Got {tokens}"

if __name__ == '__main__':
    test_simple_set()
    test_multiple_lines()
    test_for_loop()
    test_if_statement()
    test_space_friendly_skriv_ny_rad()
    test_space_friendly_jag_ga_nu()
    test_hej_da()
    test_indentation_levels()
    test_file_open_read()
    test_file_open_write()
    test_file_write()
    print("Alla tokenizer-tester OK!")
