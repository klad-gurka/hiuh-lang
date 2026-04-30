#!/usr/bin/env python3
"""HIUH Tokenizer - pure Python, works correctly with pipelines"""

import sys

# Keywords (lowercase for case-insensitive matching)
KEYWORDS = {
    # Core keywords
    'sätt': 'SET', 'för': 'FOR', 'om': 'IF', 'hejdå': 'END',
    'annars': 'ELSE', 'läs': 'READ', 'skriv': 'SKRIV', 'skrivnyrad': 'SKRIV_NL',
    'lagra': 'STORE', 'jämför': 'CMP',
    'jämförbuffer': 'CMP_BUF', 'jagmåstegånu': 'EXIT',
    'bryt': 'BREAK', 'till': 'TILL', 'från': 'FRAN',
    'är': 'AR', 'pluss': 'PLUSS', 'minus': 'MINUS',
    'gånger': 'GÅNGER', 'delat': 'DELA',
    'ur': 'UR', 'vid': 'VID', 'med': 'MED',
    'tecken': 'CHAR', 'än': 'THAN', 'mindre': 'MINDRE',
    'inte': 'INTE', 'eller': 'OR',
    'större': 'STÖRRE', 'värdet': 'VAL', 'av': 'OF',
    'text': 'TEXT', 'i': 'IN', 'ge': 'GE',
    'medan': 'WHILE',
    # Function keywords
    'grej': 'GREJ',     # function definition
    'anropa': 'CALL',   # function call
    'kalla': 'CALL',    # alias for anropa
    # List keywords
    'lista': 'LIST',    # list type
    'lägg': 'LIST_APPEND',  # append to list (handled specially)
    'antal': 'LIST_LEN',   # list length
    'element': 'LIST_GET', # get element at index
    'skapa': 'LIST_CREATE', # create list
    # File I/O keywords
    'öppna': 'FILE_OPEN',  # open file
    'fil': 'FILE',         # file keyword
    'läsning': 'READ_MODE',  # read mode
    'skrivning': 'WRITE_MODE',  # write mode
    # Space-friendly compound keywords
    'ny': 'SKRIV_NL',  # "skriv ny rad" = SKRIV + SKRIV_NL
    'rad': 'SKRIV_NL',
    'gå': 'EXIT',  # "jag gå nu" = EXIT
    'nu': 'EXIT',
}

def tokenize(src):
    """Tokenize source string, yield (indent_level, tokens) for each line"""
    prev_word = None
    last_token = None  # Track the last token added
    first_indent = None  # Track first non-empty line's indent for normalization
    for line in src.split('\n'):
        # Calculate indentation level
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if not stripped:
            continue
        words = stripped.split()
        tokens = []
        i = 0
        while i < len(words):
            word = words[i].lower()
            
            # Handle "antal element i X" → LIST_LEN X (skip if after 'sätt' where antal is a variable)
            if word == 'antal' and i + 3 <= len(words) and prev_word != 'sätt':
                if words[i+1].lower() == 'element' and words[i+2].lower() == 'i':
                    list_name = words[i+3]
                    tokens.append('LIST_LEN')
                    tokens.append(list_name)
                    last_token = 'LIST_LEN'
                    i += 4
                    continue
            
            # Handle "sätt x till lista" → LIST_CREATE
            if word == 'sätt' and i + 3 < len(words):
                var_name = words[i + 1]
                rest_words = words[i + 3:]
                rest_lower = ' '.join(rest_words).lower()
                if rest_lower == 'lista':
                    tokens.append('LIST_CREATE')
                    tokens.append(var_name)
                    last_token = 'LIST_CREATE'
                    i += 4
                    continue
                if rest_lower.startswith('lista av '):
                    # "sätt x till lista av 1, 2, 3"
                    items_str = rest_lower[9:]  # skip "lista av "
                    # Split on commas, filter empty, strip whitespace
                    items = [x.strip() for x in items_str.split(',') if x.strip()]
                    tokens.append('NY_LISTA')
                    tokens.append(var_name)
                    tokens.extend(items)
                    last_token = 'NY_LISTA'
                    i += len(rest_words) + 4
                    continue
            
            # Handle "lägg till X till Y" → LIST_APPEND Y X
            if word == 'lägg' and i + 4 < len(words):
                if words[i+1].lower() == 'till' and words[i+3].lower() == 'till':
                    item = words[i+2]
                    target = words[i+4]
                    tokens.append('LIST_APPEND')
                    tokens.append(target)
                    tokens.append(item)
                    last_token = 'LIST_APPEND'
                    i += 5
                    continue
            
            # Handle "element X ur Y" → LIST_GET Y X
            if word == 'element' and i + 3 < len(words):
                if words[i+2].lower() == 'ur':
                    idx = words[i+1]
                    list_name = words[i+3]
                    tokens.append('LIST_GET')
                    tokens.append(list_name)
                    tokens.append(idx)
                    last_token = 'LIST_GET'
                    i += 4
                    continue
            
            # Handle "ta bort element X från Y" → TA_BORT_INDEX Y X
            if word == 'ta' and i + 5 < len(words):
                if words[i+1].lower() == 'bort' and words[i+2].lower() == 'element':
                    idx = words[i+3]
                    if words[i+4].lower() == 'från':
                        list_name = words[i+5]
                        tokens.append('TA_BORT_INDEX')
                        tokens.append(list_name)
                        tokens.append(idx)
                        last_token = 'TA_BORT_INDEX'
                        i += 6
                        continue
            
            # Handle "antal element i X" → LIST_LEN X
            if word == 'antal' and i + 3 < len(words):
                if words[i+1].lower() == 'element' and words[i+2].lower() == 'i':
                    list_name = words[i+3]
                    tokens.append('LIST_LEN')
                    tokens.append(list_name)
                    last_token = 'LIST_LEN'
                    i += 4
                    continue
            
            # Handle "skriv värdet av x" → SKRIV_VAR x (print variable value)
            if word == 'skriv' and i + 3 < len(words):
                if words[i+1].lower() == 'värdet' and words[i+2].lower() == 'av':
                    tokens.append('SKRIV_VAR')
                    tokens.append(words[i+3])
                    last_token = 'SKRIV_VAR'
                    i += 4
                    continue
            
            # Handle "skriv ny rad" → SKRIV_NL (space-friendly)
            if word == 'skriv' and i + 2 < len(words):
                if words[i+1].lower() == 'ny' and words[i+2].lower() == 'rad':
                    tokens.append('SKRIV_NL')
                    last_token = 'SKRIV_NL'
                    i += 3
                    continue
            
            # After SKRIV_NL, next word is an argument (not a keyword)
            if last_token == 'SKRIV_NL':
                tokens.append(words[i])
                last_token = None
                i += 1
                continue
            
            # Handle "jag gå nu" → EXIT (space-friendly for JagMåsteGåNu)
            if word == 'jag' and i + 2 < len(words):
                if words[i+1].lower() == 'gå' and words[i+2].lower() == 'nu':
                    tokens.append('EXIT')
                    last_token = 'EXIT'
                    i += 3
                    continue
            
            # Handle "hej då" → EXIT (program exit)
            if word == 'hej' and i + 1 < len(words):
                if words[i+1].lower() == 'då':
                    tokens.append('EXIT')
                    last_token = 'EXIT'
                    i += 2
                    continue

            # Handle "öppna X för läsning" → FILE_OPEN X 'r'
            if word == 'öppna' and i + 3 < len(words):
                filename = words[i+1]
                if words[i+2].lower() == 'för' and words[i+3].lower() == 'läsning':
                    tokens.append('FILE_OPEN')
                    tokens.append(filename)
                    tokens.append('r')
                    last_token = 'FILE_OPEN'
                    i += 4
                    continue
            
            # Handle "öppna X för skrivning" → FILE_OPEN X 'w'
            if word == 'öppna' and i + 3 < len(words):
                filename = words[i+1]
                if words[i+2].lower() == 'för' and words[i+3].lower() == 'skrivning':
                    tokens.append('FILE_OPEN')
                    tokens.append(filename)
                    tokens.append('w')
                    last_token = 'FILE_OPEN'
                    i += 4
                    continue
            
            # Handle "skriv till fil X" → FILE_WRITE X
            if word == 'skriv' and i + 3 < len(words):
                if words[i+1].lower() == 'till' and words[i+2].lower() == 'fil':
                    filename = words[i+3]
                    tokens.append('FILE_WRITE')
                    tokens.append(filename)
                    last_token = 'FILE_WRITE'
                    i += 4
                    continue
            
            # 'i' after variable-taking keywords/operators is a variable name, not IN keyword
            if word == 'i' and prev_word in ('för', 'sätt', 'om', 'skriv', 'lagra', 'av', 'är', 'medan', 'WHILE', 'IF', 'FOR', 'SET', 'pluss', 'minus', 'gånger', 'delat', 'PLUSS', 'MINUS', 'GÅNGER', 'DELA'):
                tokens.append(word)  # variable name
                last_token = word
            # After SET/TILL, next word is a variable name (even if it's a keyword like 'antal')
            elif prev_word in ('sätt', 'till'):
                tokens.append(words[i])  # variable name, preserve original case
                last_token = words[i]
            elif word in KEYWORDS:
                tokens.append(KEYWORDS[word])
                last_token = KEYWORDS[word]
            else:
                tokens.append(words[i])
                last_token = words[i]
            prev_word = word
            i += 1
        if tokens:
            # Normalize indentation: compute relative indent from first line's indent
            # This handles both tabs and spaces correctly
            if first_indent is None:
                first_indent = indent
            norm_indent = indent - first_indent
            yield (norm_indent, tokens)

def tokenize_stream():
    """Read from stdin, output indent level + tokens"""
    for indent, tokens in tokenize(sys.stdin.read()):
        print(f"{indent} {' '.join(tokens)}")

if __name__ == '__main__':
    tokenize_stream()
