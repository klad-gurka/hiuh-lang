#!/usr/bin/env python3
"""
HIUH Parser - converts tokens to IR using indentation-based blocks

Python-style: blocks are determined by indentation level, not END keywords.
"""

import sys

def parse_tokens(tokenized_lines):
    """
    Parse tokenized lines (indent, tokens) to IR
    
    Args:
        tokenized_lines: list of (indent_level, tokens) tuples
    
    Returns:
        IR as list of tuples
    """
    ir = []
    parse_block(tokenized_lines, 0, ir)
    return ir

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
        elif tok == 'EXIT':
            out.append(('EXIT', 0))
            i += 1
        elif tok == 'BREAK':
            out.append(('BREAK',))
            i += 1
        elif tok == 'SKRIV':
            expr = tokens[1] if len(tokens) > 1 else ''
            out.append(('SKRIV', expr))
            i += 1
        elif tok == 'SKRIV_NL':
            expr = tokens[1] if len(tokens) > 1 else ''
            out.append(('SKRIV_NL', expr))
            i += 1
        elif tok == 'SKRIV_VAR':
            name = tokens[1] if len(tokens) > 1 else ''
            out.append(('SKRIV_VAR', name))
            i += 1
        elif tok == 'READ':
            out.append(('READ', 'input_buf'))
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
    # Check for binary expressions: a PLUS/MINUS/TIMES/DIV b
    if len(tokens) >= 3 and tokens[1] in ('PLUS', 'MINUS', 'TIMES', 'DIV'):
        op_sym = {'PLUS': '+', 'MINUS': '-', 'TIMES': '*', 'DIV': '/'}[tokens[1]]
        second = tokens[2]
        second_val = int(second) if second.isdigit() else second
        first_val = int(tok) if tok.isdigit() else tok
        return (op_sym, first_val, second_val)
    # Plain number or identifier
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
    if next_indent <= base_indent:
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
    Returns (ir_statement, lines_consumed)
    """
    indent, tokens = lines[0]
    
    # Parse the IF condition
    cmp_result = parse_cmp(tokens[1:])
    var, op, val = cmp_result
    
    # Check if there's a body (next line at higher indent)
    if len(lines) < 2:
        return ('IF', (var, op, val), []), 1
    
    next_indent, next_tokens = lines[1]
    if next_indent <= base_indent:
        # No body (dedent after IF line)
        return ('IF', (var, op, val), []), 1
    
    # Multi-line IF with body at next_indent
    body = []
    i = 1  # Start after IF line
    while i < len(lines):
        child_indent, child_tokens = lines[i]
        if child_indent <= base_indent:
            # Dedent - body is done
            break
        consumed, body_len = parse_single_line(lines[i:], base_indent + 1, body)
        i += body_len
    
    ir = ('IF', (var, op, val), body)
    return ir, i

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
        return parse_set(tokens), 1
    elif tok == 'EXIT':
        body.append(('EXIT', 0))
        return None, 1
    elif tok == 'BREAK':
        body.append(('BREAK',))
        return None, 1
    elif tok == 'SKRIV':
        expr = tokens[1] if len(tokens) > 1 else ''
        body.append(('SKRIV', expr))
        return None, 1
    elif tok == 'SKRIV_NL':
        expr = tokens[1] if len(tokens) > 1 else ''
        body.append(('SKRIV_NL', expr))
        return None, 1
    elif tok == 'SKRIV_VAR':
        name = tokens[1] if len(tokens) > 1 else ''
        body.append(('SKRIV_VAR', name))
        return None, 1
    elif tok == 'FOR':
        consumed = parse_for_single(tokens)
        body.append(consumed)
        return None, 1
    elif tok == 'IF':
        cmp_result = parse_cmp(tokens[1:])
        var, op, val = cmp_result
        body.append(('IF', (var, op, val), []))
        return None, 1
    
    return None, 1

def parse_cmp(tokens):
    """Parse comparison: VAR [är [inte]] [mindre/större [eller]] än VALUE"""
    var = tokens[0]
    if len(tokens) >= 3:
        # är mindre än 5 OR mindre än 5 (but NOT är mindre eller → <=)
        if tokens[1] == 'LESS' or (tokens[1] == 'AR' and tokens[2] == 'LESS' and tokens[3] != 'OR'):
            val = tokens[4] if tokens[1] == 'AR' else tokens[3]
            return (var, '<', val)
        # är mindre eller (än) → <= (check BEFORE plain LESS)
        if tokens[1] == 'AR' and tokens[2] == 'LESS' and tokens[3] == 'OR':
            val = tokens[5] if len(tokens) > 5 else tokens[4]
            return (var, '<=', val)
        # är större än 5 OR större än 5 (but NOT är större eller → >=)
        elif tokens[1] == 'GREATER' or (tokens[1] == 'AR' and tokens[2] == 'GREATER' and tokens[3] != 'OR'):
            val = tokens[4] if tokens[1] == 'AR' else tokens[3]
            return (var, '>', val)
        # är större eller (än) → >= (check BEFORE plain GREATER)
        if tokens[1] == 'AR' and tokens[2] == 'GREATER' and tokens[3] == 'OR':
            val = tokens[5] if len(tokens) > 5 else tokens[4]
            return (var, '>=', val)
        # är X (equality)
        elif tokens[1] == 'AR':
            # är inte X → !=
            if tokens[2] == 'INTE':
                return (var, '!=', tokens[3])
            return (var, '==', tokens[2])
    return (var, '!=', 0)

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
