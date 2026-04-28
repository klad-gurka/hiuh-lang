#!/usr/bin/env python3
"""Tests for tokenize.py"""

import sys
import io
sys.path.insert(0, 'src')

from hiuh.tokenize import tokenize

def test_simple_set():
    src = "Sätt x till 5"
    tokens = list(tokenize(src))
    assert tokens == ['SET', 'x', 'TILL', '5']

def test_multiple_tokens():
    src = "Sätt x till 5\nSkrivNyRad x"
    tokens = list(tokenize(src))
    assert 'SET' in tokens
    assert 'x' in tokens
    assert '5' in tokens

def test_for_loop():
    # Note: 'i' is keyword IN, should be variable name
    src = "För x från 0 till 10"
    tokens = list(tokenize(src))
    assert tokens == ['FOR', 'x', 'FROM', '0', 'TILL', '10']

def test_if_statement():
    src = "Om x är 0"
    tokens = list(tokenize(src))
    assert tokens == ['IF', 'x', 'AR', '0']

def test_empty_lines():
    src = "Sätt x till 5\n\n\nSätt y till 10"
    tokens = list(tokenize(src))
    assert tokens == ['SET', 'x', 'TILL', '5', 'SET', 'y', 'TILL', '10']

if __name__ == '__main__':
    test_simple_set()
    test_multiple_tokens()
    test_for_loop()
    test_if_statement()
    test_empty_lines()
    print("Alla tester OK!")
