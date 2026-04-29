# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Arkitektur

```
src/hiuh/
  tokenize.py   ← tokenizer (ren Python)
  parse.py      ← parser → IR
  backend/
    x86.py     ← x86 asm backend
tests/
  test_tokenize.py
  test_parse.py
  test_backend_x86.py
```

## IR-nod dokumentation

### Satser (Statements)

| IR nod | Språk-konstruktion | IR-exempel | X86 | WASM |
|--------|-------------------|------------|-----|------|
| `('SET', name, expr)` | `sätt x till 5` | `('SET', 'x', 5)` | ✅ | ❌ |
| `('FOR', var, start, end, body)` | `för x från 0 till 10` | `('FOR', 'x', 0, 10, [body])` | ✅ | ❌ |
| `('IF', cmp, body)` | `om x är 0` | `('IF', ('x', '==', '0'), [body])` | ✅ | ❌ |
| `('BREAK',)` | `bryt` | `('BREAK',)` | ✅ | ❌ |
| `('EXIT',)` | `hej då` / `jag gå nu` | `('EXIT',)` | ✅ | ❌ |
| `('SKRIV', text)` | `skriv hello` | `('SKRIV', 'hello')` | ✅ | ❌ |
| `('SKRIV_NL',)` | `skriv ny rad` | `('SKRIV_NL',)` | ✅ | ❌ |
| `('SKRIV_VAR', name)` | `skriv värdet av x` | `('SKRIV_VAR', 'x')` | ❌ | ❌ |
| `('READ',)` | `läs` | `('READ',)` | ❌ | ❌ |
| `('STORE', buf, idx, val)` | `lagra vid i i buf` | `('STORE', 'buf', 'i', 'x')` | ❌ | ❌ |
| `('LOAD', buf, idx)` | `tecken i ur buf` | `('LOAD', 'buf', 'i')` | ❌ | ❌ |
| `('FUNC_DEF', name, params, body)` | `grej namn param` | `('FUNC_DEF', 'add', ['a', 'b'], [body])` | ✅ | ❌ |
| `('CALL', name, args)` | `anropa namn med x` | `('CALL', 'add', ['x', 'y'])` | ✅ | ❌ |
| `('RETURN', expr)` | `ge x` | `('RETURN', 'x')` | ✅ | ❌ |
| `('WHILE', cmp, body)` | `medan x är 0` | `('WHILE', ('x', '==', '0'), [body])` | ✅ | ❌ |
| `('LIST_CREATE', name)` | `sätt x till lista` | `('LIST_CREATE', 'x')` | ✅ | ❌ |
| `('LIST_APPEND', list, val)` | `lägg till x till lista` | `('LIST_APPEND', 'lst', 'x')` | ✅ | ❌ |
| `('LIST_GET', list, idx)` | `element i ur lista` | `('LIST_GET', 'lst', 'i')` | ✅ | ❌ |
| `('LIST_LEN', list)` | `antal element i lista` | `('LIST_LEN', 'lst')` | ✅ | ❌ |
| `('CONCAT', a, b)` | `a sammanfogat med b` | `('CONCAT', 'a', 'b')` | ❌ | ❌ |
| `('FILE_OPEN', filename, mode, buf)` | `öppna fil för läsning` | `('FILE_OPEN', 'data.txt', 'r', 'buf')` | ❌ | ❌ |
| `('FILE_WRITE', filename, data)` | `skriv till fil` | `('FILE_WRITE', 'out.txt', 'hello')` | ❌ | ❌ |

### Uttryck (Expressions)

| IR nod | Språk-konstruktion | IR-exempel | X86 | WASM |
|--------|-------------------|------------|-----|------|
| `('LIT', n)` | `5` (literalt tal) | `('LIT', 5)` | ✅ | ❌ |
| `('VAR', name)` | `x` (variabel-referens) | `('VAR', 'x')` | ✅ | ❌ |
| `('ADD', a, b)` | `a pluss b` | `('ADD', 'a', 'b')` | ✅ | ❌ |
| `('SUB', a, b)` | `a minus b` | `('SUB', 'a', 'b')` | ❌ | ❌ |
| `('MUL', a, b)` | `a gånger b` | `('MUL', 'a', 'b')` | ❌ | ❌ |
| `('DIV', a, b)` | `a delat b` | `('DIV', 'a', 'b')` | ❌ | ❌ |

### Jämförelse (Comparisons)

| IR nod | Språk-konstruktion | IR-exempel | X86 | WASM |
|--------|-------------------|------------|-----|------|
| `('EQ', a, b)` | `är` | `('EQ', 'x', '0')` | ✅ | ❌ |
| `('NE', a, b)` | `är inte` | `('NE', 'x', '0')` | ❌ | ❌ |
| `('LT', a, b)` | `är mindre än` | `('LT', 'x', '5')` | ✅ | ❌ |
| `('GT', a, b)` | `är större än` | `('GT', 'x', '0')` | ✅ | ❌ |
| `('LE', a, b)` | `är mindre eller` | `('LE', 'x', '5')` | ❌ | ❌ |
| `('GE', a, b)` | `är större eller` | `('GE', 'x', '0')` | ❌ | ❌ |

## Indentering

- ✅ Python-style: block bestäms av indentering, inga END-nyckelord
- Indentering: 4 spaces = 1 nivå

## Nästa steg

### Hög prioritet
1. [x] **Implementera alla uttryck** - SUB, MUL, DIV ✅
2. [x] **Implementera alla jämförelser** - NE, LE, GE ✅
3. [x] **Läs input** - READ x86 syscall ✅
4. [x] **skriv värdet av x** - SKRIV_VAR ✅

### Medel prioritet
5. [x] **WHILE-loop** ✅
6. [x] **Funktioner** - grej/anropa/ge ✅
7. [x] **Listor** - lägg till, element ur, antal ✅

### Låg prioritet
8. [x] **File I/O** ✅ (FILE_OPEN, FILE_WRITE tokenizer+parser+x86)
9. [ ] WASM backend

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn