#!/usr/bin/env python3
"""HIUH Tokenizer - pure Python, works correctly with pipelines"""

import sys

# Keywords
KEYWORDS = {
    'Sätt': 'SET', 'För': 'FOR', 'Om': 'IF', 'Hejdå': 'END',
    'Annars': 'ELSE', 'Läs': 'READ', 
    'SkrivNyRad': 'SKRIV_NL', 'Skriv': 'SKRIV', 
    'Lagra': 'STORE', 'Jämför': 'CMP',
    'JämförBuffer': 'CMP_BUF', 'JagMåsteGåNu': 'EXIT',
    'Bryt': 'BREAK', 'till': 'TILL', 'från': 'FRAN',
    'är': 'AR', 'pluss': 'PLUS', 'ur': 'UR', 'vid': 'VID',
    'med': 'MED', 'tecken': 'CHAR', 'än': 'THAN',
    'mindre': 'LESS', 'större': 'GREATER', 'värdet': 'VAL',
    'av': 'OF', 'text': 'TEXT', 'i': 'IN', 'ge': 'RET',
    # Space-friendly aliases (for mobile typing)
    'NyRad': 'SKRIV_NL',  # "Skriv NyRad" instead of "SkrivNyRad"
    'Gå': 'EXIT',  # "Jag Gå Nu" instead of "JagMåsteGåNu"
    'Nu': 'EXIT',
}

def tokenize(src):
    """Tokenize source string, yield tokens"""
    for line in src.split('\n'):
        line = line.strip()
        if not line:
            continue
        words = line.split()
        i = 0
        while i < len(words):
            word = words[i]
            # Handle "Jag Gå Nu" → EXIT (space-friendly for JagMåsteGåNu)
            if word == 'Jag' and i + 2 < len(words) and KEYWORDS.get(words[i+1]) == 'EXIT' and KEYWORDS.get(words[i+2]) == 'EXIT':
                yield 'EXIT'
                i += 3
                continue
            if word in KEYWORDS:
                token = KEYWORDS[word]
                # Handle "Skriv NyRad" → SKRIV_NL (space-friendly)
                if token == 'SKRIV' and i + 1 < len(words) and KEYWORDS.get(words[i+1]) == 'SKRIV_NL':
                    yield 'SKRIV_NL'
                    i += 2
                    continue
                yield token
            else:
                yield word
            i += 1

def tokenize_stream():
    """Read from stdin, output one token per line"""
    for tok in tokenize(sys.stdin.read()):
        print(tok)

if __name__ == '__main__':
    tokenize_stream()
