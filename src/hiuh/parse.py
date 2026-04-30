#!/usr/bin/env python3
"""
HIUH Parser - converts tokens to IR using indentation-based blocks

Python-style: blocks are determined by indentation level, not END keywords.
"""

import sys

# Track defined function names (filled in during first pass in parse_tokens)
FUNC_NAMES = set()

def parse_tokens(tokenized_lines):
    """
    Parse tokenized lines (indent, tokens) to IR

    Args:
        tokenized_lines: list of (indent_level, tokens) tuples

    Returns:
        IR as list of tuples
    """
    ir = []
    # First pass: collect function definitions
    FUNC_NAMES.clear()
    for indent, tokens in tokenized_lines:
        if tokens and tokens[0] == 'GREJ':
            func_name = tokens[1]
            FUNC_NAMES.add(func_name)
    # Second pass: parse everything
    parse_block(tokenized_lines, 0, ir)
    return ir


def parse_skriv_expr(tokens):
    """
    Parse SKRIV expression from tokens.
    
    Rules (in order):
    - RADBRYT → ('RADBRYT',)
    - Number → ('HELTAL', int value)
    - Otherwise → ('TEXT', text)
    - Expression (pluss/mindre/etc) → parse_value()
    """
    if not tokens:
        return ''
    
    token = tokens[0]
    
    # RADBRYT keyword
    if token == 'RADBRYT':
        return ('RADBRYT',)
    
    # Check if it's an arithmetic expression
    if len(tokens) >= 3 and tokens[1].lower() in ('pluss', 'minus', 'gånger', 'dela'):
        return parse_value(tokens)
    
    # Single token
    if len(tokens) == 1:
        # Number?
        if token.isdigit():
            return ('HELTAL', int(token))
        # Otherwise text (bare string - backend interprets as variable name if used as such)
        return token
    
    # For multi-token, fall back to parse_value for expressions
    return parse_value(tokens)

def parse_block(lines, base_indent, out):
    """
    Parse a block of lines up to the next dedent.

    Args:
        lines: list of (indent, tokens) remaining
        base_indent: indentation level of parent block
        out: list to append IR statements to
    """
    i = 0
    while i < len(lines):
        indent, tokens = lines[i]

        # If dedent (less indentation than parent), we're done
        if indent < base_indent:
            return i

        # Skip empty lines
        if not tokens:
            i += 1
            continue

        tok = tokens[0]

        if tok == 'SET':
            consumed = parse_set(tokens)
            out.extend(consumed)
            i += 1
        elif tok == 'FOR':
            consumed, body_len = parse_for(lines[i:], base_indent)
            out.append(consumed)
            i += body_len
        elif tok == 'IF':
            consumed, body_len = parse_if(lines[i:], base_indent)
            out.append(consumed)
            i += body_len
        elif tok == 'WHILE':
            consumed, body_len = parse_while(lines[i:], base_indent)
            out.append(consumed)
            i += body_len
        elif tok == 'EXIT':
            out.append(('EXIT', 0))
            i += 1
        elif tok == 'BREAK':
            out.append(('BREAK',))
            i += 1
        elif tok == 'SKRIV':
            # Parse SKRIV expression
            val_tokens = tokens[1:]
            val = parse_skriv_expr(val_tokens)
            out.append(('SKRIV', val))
            i += 1
        elif tok == 'SKRIV_NL':
            # skriv ny rad → SKRIV ('RADBRYT',)
            out.append(('SKRIV', ('RADBRYT',)))
            i += 1
        elif tok == 'SKRIV_VAR':
            # skriv värdet av x → SKRIV ('VARIABEL', x)
            name = tokens[1] if len(tokens) > 1 else ''
            out.append(('SKRIV', ('VARIABEL', name)))
            i += 1
        elif tok == 'READ':
            out.append(('READ', 'input_buf'))
            i += 1
        elif tok == 'GREJ':
            consumed, body_len = parse_grej(lines[i:], base_indent)
            out.append(consumed)
            i += body_len
        elif tok == 'CALL':
            consumed = parse_call(tokens)
            out.append(consumed)
            i += 1
        elif tok == 'GE':
            consumed = parse_ret(tokens)
            out.append(consumed)
            i += 1
        elif tok == 'LIST_CREATE':
            # sätt x till lista → LIST_CREATE x
            name = tokens[1] if len(tokens) > 1 else ''
            out.append(('LIST_CREATE', name))
            i += 1
        elif tok == 'NY_LISTA':
            # sätt x till lista av 1, 2, 3 → NY_LISTA x 1 2 3
            name = tokens[1] if len(tokens) > 1 else ''
            items = tokens[2:] if len(tokens) > 2 else []
            out.append(('NY_LISTA', name, items))
            i += 1
        elif tok == 'LIST_APPEND':
            # lägg till x till y → LIST_APPEND y x
            list_name = tokens[1] if len(tokens) > 1 else ''
            item = tokens[2] if len(tokens) > 2 else ''
            out.append(('LIST_APPEND', list_name, item))
            i += 1
        elif tok == 'LIST_GET':
            # element i ur lst → LIST_GET lst i
            list_name = tokens[1] if len(tokens) > 1 else ''
            idx_str = tokens[2] if len(tokens) > 2 else ''
            idx = int(idx_str) if idx_str.isdigit() else idx_str
            out.append(('LIST_GET', list_name, idx))
            i += 1
        elif tok == 'LIST_LEN':
            # antal element i lst → LIST_LEN lst
            list_name = tokens[1] if len(tokens) > 1 else ''
            out.append(('LIST_LEN', list_name))
            i += 1
        elif tok == 'TA_BORT_INDEX':
            # ta bort element X från lst → TA_BORT_INDEX lst X
            list_name = tokens[1] if len(tokens) > 1 else ''
            idx_str = tokens[2] if len(tokens) > 2 else ''
            idx = int(idx_str) if idx_str.isdigit() else idx_str
            out.append(('TA_BORT_INDEX', list_name, idx))
            i += 1
        elif tok == 'BYT_UT':
            # byt ut element X i lst mot Z → BYT_UT lst X Z
            list_name = tokens[1] if len(tokens) > 1 else ''
            idx_str = tokens[2] if len(tokens) > 2 else ''
            idx = int(idx_str) if idx_str.isdigit() else idx_str
            new_val = tokens[3] if len(tokens) > 3 else ''
            out.append(('BYT_UT', list_name, idx, new_val))
            i += 1
        elif tok == 'FILE_OPEN':
            # öppna X för läsning → FILE_OPEN X mode
            filename = tokens[1] if len(tokens) > 1 else ''
            mode = tokens[2] if len(tokens) > 2 else 'r'
            out.append(('FILE_OPEN', filename, mode))
            i += 1
        elif tok == 'FILE_WRITE':
            # skriv till fil X → FILE_WRITE X data
            filename = tokens[1] if len(tokens) > 1 else ''
            data = tokens[2] if len(tokens) > 2 else ''
            out.append(('FILE_WRITE', filename, data))
            i += 1
        else:
            # Unknown token, skip
            i += 1

    return i

def parse_set(tokens):
    """Parse SET statement, returns list of IR statements"""
    ir = []
    name = tokens[1]
    # Skip TILL, collect value tokens
    val_tokens = []
    j = 2
    while j < len(tokens):
        val_tokens.append(tokens[j])
        j += 1
    val = parse_value(val_tokens)
    ir.append(('SET', name, val))
    return ir

def parse_value(tokens):
    """Parse a value: number, identifier, or expression"""
    if not tokens:
        return 0
    # Skip TILL keyword
    if tokens[0] == 'TILL':
        tokens = tokens[1:]
    if not tokens:
        return 0
    tok = tokens[0]
    # Check for function call: CALL func_name [MED arg1 [MED arg2 ...]]
    # Also handle 'anropa'/'kalla' keywords passed through as variable names
    # (tokenizer passes them through after SET/TILL, but we need to recognize them)
    if tok in ('CALL', 'ANROPA', 'KALLA', 'anropa', 'kalla') and len(tokens) >= 2:
        func_name = tokens[1]
        # Normalize func_name token too (might be lowercased)
        if func_name in ('anropa', 'kalla'):
            func_name = tokens[2] if len(tokens) > 2 else func_name
        # Strip commas from args (e.g. '1,' -> '1')
        args = [t.rstrip(',') for t in tokens[2:] if t not in ('MED',)]
        return ('CALL', func_name, args)
    # Check for LIST_LEN: LIST_LEN list_name
    if tok == 'LIST_LEN' and len(tokens) >= 2:
        list_name = tokens[1]
        return ('LIST_LEN', list_name)
    # Check for LIST_GET: LIST_GET list_name idx (bare LIST_GET tokens from tokenizer)
    if tok == 'LIST_GET' and len(tokens) >= 3:
        list_name = tokens[1]
        idx_str = tokens[2]
        idx = int(idx_str) if idx_str.isdigit() else idx_str
        return ('LIST_GET', list_name, idx)
    # Check for LIST_GET: CHAR IN UR list [idx] → ('LIST_GET', list, idx)
    if tok == 'CHAR' and len(tokens) >= 4 and tokens[1] == 'IN' and tokens[2] == 'UR':
        list_name = tokens[3]
        idx = tokens[4] if len(tokens) >= 5 else '0'
        return ('LIST_GET', list_name, idx)
    # Check for VAR IN UR list [idx] → ('LIST_GET', list, idx) - variable as source
    if len(tokens) >= 4 and tokens[1] == 'IN' and tokens[2] == 'UR':
        list_name = tokens[3]
        idx = tokens[4] if len(tokens) >= 5 else '0'
        return ('LIST_GET', list_name, idx)
    # Check for binary expressions: a PLUSS/MINUS/GÅNGER/DELA b
    if len(tokens) >= 3 and tokens[1] in ('PLUSS', 'MINUS', 'GÅNGER', 'DELA'):
        op_sym = {'PLUSS': 'PLUSS', 'MINUS': 'MINUS', 'GÅNGER': 'GÅNGER', 'DELA': 'DELA'}[tokens[1]]
        second = tokens[2]
        second_val = int(second) if second.isdigit() else second
        first_val = int(tok) if tok.isdigit() else tok
        return (op_sym, first_val, second_val)
    # Check for function call via known function name (after SET/TILL, anropa/kalla passed as VAR)
    # e.g. "sätt b till dubbla a" where 'dubbla' is a known function
    if tok not in ('SET', 'TILL', 'GREJ', 'FOR', 'IF', 'WHILE', 'BREAK', 'SKRIV',
                  'GE', 'FUNC_DEF') and tok in FUNC_NAMES and len(tokens) >= 2:
        func_name = tok
        args = [t.rstrip(',') for t in tokens[1:] if t not in ('MED',)]
        return ('CALL', func_name, args)
    # Plain number or identifier (including CHAR, LIST_LEN, etc.)
    if tok.isdigit():
        return int(tok)
    return tok

def parse_for(lines, base_indent):
    """
    Parse FOR loop including its indented body.
    Returns (ir_statement, lines_consumed)
    """
    indent, tokens = lines[0]

    # Parse FOR header
    var = tokens[1]
    start, end = 0, 0
    j = 2
    # Skip FROM
    if tokens[j] == 'FRAN':
        j += 1
    start = int(tokens[j])
    j += 1
    # Skip TILL
    if tokens[j] == 'TILL':
        j += 1
    end = int(tokens[j])

    # Check if there's a body (next line at higher indent)
    if len(lines) < 2:
        # No body
        return ('FOR', var, start, end, []), 1

    next_indent, next_tokens = lines[1]
    if next_indent < base_indent:
        # No body (dedent after FOR line)
        return ('FOR', var, start, end, []), 1

    # Multi-line FOR with body at next_indent
    body = []
    i = 1  # Start after FOR line
    while i < len(lines):
        child_indent, child_tokens = lines[i]
        if child_indent <= base_indent:
            # Dedent - body is done
            break
        # Parse the body line
        consumed, body_len = parse_single_line(lines[i:], base_indent + 1, body)
        if body_len == 0:
            # parse_single_line couldn't handle this line - recurse into parse_block
            consumed = parse_block(lines[i:], base_indent + 1, body)
            i += consumed
        else:
            i += body_len

    ir = ('FOR', var, start, end, body)
    return ir, i

def parse_for_single(tokens):
    """Parse single-line FOR loop"""
    var = tokens[1]
    start, end = 0, 0
    j = 2
    if tokens[j] == 'FRAN':
        j += 1
    start = int(tokens[j])
    j += 1
    if tokens[j] == 'TILL':
        j += 1
    end = int(tokens[j])
    return ('FOR', var, start, end, [])

def parse_if(lines, base_indent):
    """
    Parse IF statement including its indented body.
    If ELSE is found, parse false_body as well.
    Returns (ir_statement, lines_consumed)
    """
    indent, tokens = lines[0]

    # Parse the IF condition
    cmp_result = parse_cmp(tokens[1:])
    var, op, val = cmp_result

    # Check if there's a body (next line at higher indent)
    if len(lines) < 2:
        return ('IF', (var, op, val), [], []), 1

    next_indent, next_tokens = lines[1]
    if next_indent < base_indent:
        # No body (dedent after IF line)
        return ('IF', (var, op, val), [], []), 1

    # Multi-line IF with body at next_indent
    true_body = []
    false_body = []
    in_false_body = False
    i = 1  # Start after IF line
    while i < len(lines):
        child_indent, child_tokens = lines[i]

        # Check for ELSE at same indent level (base_indent)
        if child_indent == base_indent and child_tokens and child_tokens[0] == 'ELSE':
            in_false_body = True
            i += 1
            continue

        if child_indent <= base_indent and not in_false_body:
            # Dedent - we're done with the IF statement
            break

        # For false_body (after ELSE), use parse_block to handle arbitrary nesting
        if in_false_body:
            consumed = parse_block(lines[i:], base_indent + 1, false_body)
            i += consumed
            break  # parse_block handles dedent detection
        else:
            consumed, body_len = parse_single_line(lines[i:], base_indent + 1, true_body)
            if body_len == 0:
                # Indentation deeper than base_indent+1 - recurse into parse_block
                consumed = parse_block(lines[i:], base_indent + 1, true_body)
                i += consumed
            else:
                i += body_len

    ir = ('IF', (var, op, val), true_body, false_body)
    return ir, i

def parse_while(lines, base_indent):
    """
    Parse WHILE statement including its indented body.
    Returns (ir_statement, lines_consumed)
    """
    indent, tokens = lines[0]

    # Parse the WHILE condition
    cmp_result = parse_cmp(tokens[1:])
    var, op, val = cmp_result

    # Check if there's a body (next line at higher indent)
    if len(lines) < 2:
        return ('WHILE', (var, op, val), []), 1

    next_indent, next_tokens = lines[1]
    if next_indent < base_indent:
        # No body (dedent after WHILE line)
        return ('WHILE', (var, op, val), []), 1

    # Multi-line WHILE with body at next_indent
    body = []
    i = 1  # Start after WHILE line
    while i < len(lines):
        child_indent, child_tokens = lines[i]
        if child_indent <= base_indent:
            # Dedent - body is done
            break
        consumed, body_len = parse_single_line(lines[i:], base_indent + 1, body)
        if body_len == 0:
            # parse_single_line couldn't handle this line - recurse into parse_block
            # Use base_indent + 2 to match body indentation level
            consumed = parse_block(lines[i:], base_indent + 2, body)
            i += consumed
        else:
            i += body_len

    ir = ('WHILE', (var, op, val), body)
    return ir, i

def parse_grej(lines, base_indent):
    """
    Parse GREJ (function definition) including its indented body.
    Returns (ir_statement, lines_consumed)
    """
    indent, tokens = lines[0]

    # Parse GREJ header: grej func_name param1 [param2 ...]
    func_name = tokens[1]
    params = tokens[2:]
    # Remove MED keywords from params if any
    params = [p for p in params if p != 'MED']

    # Check if there's a body (next line at higher indent)
    if len(lines) < 2:
        return ('FUNC_DEF', func_name, params, []), 1

    next_indent, next_tokens = lines[1]
    if next_indent < base_indent:
        # No body (dedent after GREJ line)
        return ('FUNC_DEF', func_name, params, []), 1

    # Multi-line GREJ with body at next_indent
    body = []
    i = 1  # Start after GREJ line
    while i < len(lines):
        child_indent, child_tokens = lines[i]
        if child_indent <= base_indent:
            # Dedent - body is done
            break
        consumed, body_len = parse_single_line(lines[i:], base_indent + 1, body)
        i += body_len

    ir = ('FUNC_DEF', func_name, params, body)
    return ir, i

def parse_call(tokens):
    """Parse CALL statement: anropa func_name [med arg1 [med arg2 ...]]"""
    func_name = tokens[1]
    args = []
    j = 2
    # Skip MED keywords and collect args
    while j < len(tokens):
        if tokens[j] != 'MED':
            args.append(tokens[j])
        j += 1
    return ('CALL', func_name, args)

def parse_ret(tokens):
    """Parse RETURN statement: ge expr"""
    if len(tokens) >= 2:
        val = tokens[1]
        # Try to parse as expression
        val_expr = parse_value([val])
        return ('RETURN', val_expr)
    return ('RETURN', 0)

def parse_single_line(lines, base_indent, body):
    """Parse a single line into body list, returns (ir, lines_consumed)"""
    if not lines:
        return None, 0

    indent, tokens = lines[0]
    if indent < base_indent:
        return None, 0

    if not tokens:
        return None, 1

    tok = tokens[0]

    if tok == 'SET':
        consumed = parse_set(tokens)
        body.extend(consumed)
        return None, 1
    elif tok == 'EXIT':
        body.append(('EXIT', 0))
        return None, 1
    elif tok == 'BREAK':
        body.append(('BREAK',))
        return None, 1
    elif tok == 'SKRIV':
        # Parse SKRIV expression
        val_tokens = tokens[1:]
        val = parse_skriv_expr(val_tokens)
        body.append(('SKRIV', val))
        return None, 1
    elif tok == 'SKRIV_NL':
        # skriv ny rad → SKRIV ('RADBRYT',)
        body.append(('SKRIV', ('RADBRYT',)))
        return None, 1
    elif tok == 'SKRIV_VAR':
        # skriv värdet av x → SKRIV ('VARIABEL', x)
        name = tokens[1] if len(tokens) > 1 else ''
        body.append(('SKRIV', ('VARIABEL', name)))
        return None, 1
    elif tok == 'FOR':
        consumed = parse_for_single(tokens)
        body.append(consumed)
        return None, 1
    elif tok == 'IF':
        consumed, body_len = parse_if(lines, base_indent)
        body.append(consumed)
        return None, body_len
    elif tok == 'WHILE':
        consumed, body_len = parse_while(lines, base_indent)
        body.append(consumed)
        return None, body_len
    elif tok == 'GREJ':
        consumed, body_len = parse_grej(lines, base_indent)
        body.append(consumed)
        return None, body_len
    elif tok == 'CALL':
        consumed = parse_call(tokens)
        body.append(consumed)
        return None, 1
    elif tok == 'GE':
        consumed = parse_ret(tokens)
        body.append(consumed)
        return None, 1
    elif tok == 'LIST_CREATE':
        name = tokens[1] if len(tokens) > 1 else ''
        body.append(('LIST_CREATE', name))
        return None, 1
    elif tok == 'NY_LISTA':
        name = tokens[1] if len(tokens) > 1 else ''
        items = tokens[2:] if len(tokens) > 2 else []
        body.append(('NY_LISTA', name, items))
        return None, 1
    elif tok == 'LIST_APPEND':
        list_name = tokens[1] if len(tokens) > 1 else ''
        item = tokens[2] if len(tokens) > 2 else ''
        body.append(('LIST_APPEND', list_name, item))
        return None, 1
    elif tok == 'LIST_GET':
        list_name = tokens[1] if len(tokens) > 1 else ''
        idx_str = tokens[2] if len(tokens) > 2 else ''
        idx = int(idx_str) if idx_str.isdigit() else idx_str
        body.append(('LIST_GET', list_name, idx))
        return None, 1
    elif tok == 'LIST_LEN':
        list_name = tokens[1] if len(tokens) > 1 else ''
        body.append(('LIST_LEN', list_name))
        return None, 1
    elif tok == 'TA_BORT_INDEX':
        list_name = tokens[1] if len(tokens) > 1 else ''
        idx_str = tokens[2] if len(tokens) > 2 else ''
        idx = int(idx_str) if idx_str.isdigit() else idx_str
        body.append(('TA_BORT_INDEX', list_name, idx))
        return None, 1
    elif tok == 'BYT_UT':
        list_name = tokens[1] if len(tokens) > 1 else ''
        idx_str = tokens[2] if len(tokens) > 2 else ''
        idx = int(idx_str) if idx_str.isdigit() else idx_str
        new_val = tokens[3] if len(tokens) > 3 else ''
        body.append(('BYT_UT', list_name, idx, new_val))
        return None, 1
    elif tok == 'FILE_OPEN':
        filename = tokens[1] if len(tokens) > 1 else ''
        mode = tokens[2] if len(tokens) > 2 else 'r'
        body.append(('FILE_OPEN', filename, mode))
        return None, 1
    elif tok == 'FILE_WRITE':
        filename = tokens[1] if len(tokens) > 1 else ''
        data = tokens[2] if len(tokens) > 2 else ''
        body.append(('FILE_WRITE', filename, data))
        return None, 1

    return None, 1

def parse_cmp(tokens):
    """Parse comparison: VAR [är [inte]] [mindre/större [eller]] än VALUE
    Returns IR with Swedish operator names: mindre, mindreLikaMed, större, störreLikaMed, likaMed, inteLikaMed
    """
    var = tokens[0]
    if len(tokens) >= 3:
        # är mindre än 5 OR mindre än 5 → mindre
        if tokens[1] == 'MINDRE' or (tokens[1] == 'AR' and tokens[2] == 'MINDRE' and tokens[3] != 'OR'):
            val = tokens[4] if tokens[1] == 'AR' else tokens[3]
            return (var, 'mindre', val)
        # är mindre eller (än) → mindreLikaMed
        if tokens[1] == 'AR' and tokens[2] == 'MINDRE' and tokens[3] == 'OR':
            val = tokens[5] if len(tokens) > 5 else tokens[4]
            return (var, 'mindreLikaMed', val)
        # är större än 5 OR större än 5 → större
        elif tokens[1] == 'STÖRRE' or (tokens[1] == 'AR' and tokens[2] == 'STÖRRE' and tokens[3] != 'OR'):
            val = tokens[4] if tokens[1] == 'AR' else tokens[3]
            return (var, 'större', val)
        # är större eller (än) → störreLikaMed
        if tokens[1] == 'AR' and tokens[2] == 'STÖRRE' and tokens[3] == 'OR':
            val = tokens[5] if len(tokens) > 5 else tokens[4]
            return (var, 'störreLikaMed', val)
        # är X (equality) → likaMed
        elif tokens[1] == 'AR':
            # är inte lika med X → inteLikaMed
            if tokens[2] == 'INTE':
                val = tokens[5] if len(tokens) > 5 and tokens[4] == 'MED' else tokens[3]
                return (var, 'inteLikaMed', val)
            # är lika med X → likaMed X
            val = tokens[4] if len(tokens) > 4 and tokens[3] == 'MED' else tokens[2]
            return (var, 'likaMed', val)
    return (var, 'inteLikaMed', 0)

def parse_stream():
    """Read tokenized lines from stdin, output IR as text"""
    lines = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            indent = int(parts[0])
            tokens = parts[1].split()
            lines.append((indent, tokens))
        else:
            lines.append((0, line.split()))

    ir = parse_tokens(lines)
    for stmt in ir:
        print(stmt)

if __name__ == '__main__':
    parse_stream()
