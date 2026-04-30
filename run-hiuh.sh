#!/bin/bash
# HIUH Runner - Kör HIUH-källkod med timeout
# Användning: ./run-hiuh.sh <hiuh-fil> [timeout-sekunder]
# Default timeout: 5 sekunder

set -e

TIMEOUT_SECONDS="${2:-5}"
HIUH_FILE="$1"

if [ -z "$HIUH_FILE" ]; then
    echo "Användning: $0 <hiuh-fil> [timeout-sekunder]"
    echo "Example: $0 program.hiuh 10"
    exit 1
fi

if [ ! -f "$HIUH_FILE" ]; then
    echo "Fel: Filen '$HIUH_FILE' finns inte"
    exit 1
fi

WORKDIR="$(mktemp -d)"
trap "rm -rf $WORKDIR" EXIT

# Kompilera HIUH → x86 assembly
python3 -c "
import sys
sys.path.insert(0, 'src')
from hiuh.tokenize import tokenize
from hiuh.parse import parse_tokens
from hiuh.backend.x86 import compile_ir

with open('$HIUH_FILE') as f:
    src = f.read()

lines = list(tokenize(src))
ir = parse_tokens(lines)
compile_ir(ir, target='gcc')
" > "$WORKDIR/program.s"

# Assemblera till binär
gcc -no-pie -m64 -o "$WORKDIR/a.out" "$WORKDIR/program.s" 2>&1

# Kör med timeout
timeout "$TIMEOUT_SECONDS" "$WORKDIR/a.out"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
    echo "TIMEOUT: Programmet tog mer än ${TIMEOUT_SECONDS}s (möjlig loop eller infinite rekursion)"
    exit 1
fi

exit $EXIT_CODE
