#!/usr/bin/env python3
"""HIUH Tokenizer - pure Python, works correctly with pipelines"""

import sys

# Keywords
KEYWORDS = {
    'Sätt': 'SET', 'För': 'FOR', 'Om': 'IF', 'Hejdå': 'END',
    'Annars': 'ELSE', 'Läs': 'READ', 'SkrivNyRad': 'SKRIV_NL',
    'Skriv': 'SKRIV', 'Lagra': 'STORE', 'Jämför': 'CMP',
    'JämförBuffer': 'CMP_BUF', 'JagMåsteGåNu': 'EXIT',
    'Bryt': 'BREAK', 'till': 'TILL', 'från': 'FROM',
    'är': 'AR', 'pluss': 'PLUS', 'ur': 'UR', 'vid': 'VID',
    'med': 'MED', 'tecken': 'CHAR', 'än': 'THAN',
    'mindre': 'LESS', 'större': 'GREATER', 'värdet': 'VAL',
    'av': 'OF', 'text': 'TEXT', 'i': 'IN', 'ge': 'RET',
}

def tokenize_stream():
    """Read from stdin, output one token per line"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        for word in line.split():
            if word in KEYWORDS:
                print(KEYWORDS[word])
            else:
                # Number or identifier
                print(word)

if __name__ == '__main__':
    tokenize_stream()