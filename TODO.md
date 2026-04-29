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

## IR-design

### Principer
- IR ska följa HIUH:s svenska språk så nära som möjligt
- Operatorer ska vara korta men läsbara svenska ord
- Tokenizern mappar svenska alias → IR operatorer
- Parse.py产出 enhetliga IR-namn, oavsett vilket keyword som användes

### Operatorer (Jämförelse)

| IR operator | Source keywords | Betydelse |
|-------------|-----------------|-----------|
| `mindre` | "är mindre än" | a < b |
| `mindreLikaMed` | "är mindre eller" | a <= b |
| `större` | "är större än" | a > b |
| `störreLikaMed` | "är större eller" | a >= b |
| `likaMed` | "är" | a == b |
| `inteLikaMed` | "är inte" | a != b |

### IR-nod dokumentation

#### Satser (Statements)

| IR nod | Språk-konstruktion | IR-exempel | X86 | WASM |
|--------|-------------------|------------|-----|------|
| `('SÄTT', name, expr)` | `sätt x till 5` | `('SÄTT', 'x', 5)` | ✅ | ❌ |
| `('FÖR', var, start, end, body)` | `för x från 0 till 10` | `('FÖR', 'x', 0, 10, [body])` | ✅ | ❌ |
| `('WHILE', var, op, val, body)` | `medan x är mindre än 5` | `('WHILE', 'x', 'mindre', '5', [body])` | ✅ | ❌ |
| `('OM', var, op, val, true_body, false_body)` | `om x är mindre än 5` | `('OM', 'x', 'mindre', '5', [...], [...])` | ❌ | ❌ |
| `('BRYT',)` | `bryt` | `('BRYT',)` | ✅ | ❌ |
| `('HEJDÅ',)` | `hej då` / `jag gå nu` | `('HEJDÅ',)` | ✅ | ❌ |
| `('SKRIV', text)` | `skriv hello` | `('SKRIV', 'hello')` | ✅ | ❌ |
| `('SKRIV_NL',)` | `skriv ny rad` | `('SKRIV_NL',)` | ✅ | ❌ |
| `('SKRIV_VAR', name)` | `skriv värdet av x` | `('SKRIV_VAR', 'x')` | ✅ | ❌ |
| `('LÄS',)` | `läs` | `('LÄS',)` | ✅ | ❌ |
| `('GREJ', name, params, body)` | `grej namn param` | `('GREJ', 'add', ['a', 'b'], [body])` | ✅ | ❌ |
| `('ANROPA', name, args)` | `anropa namn med x` | `('ANROPA', 'add', ['x', 'y'])` | ✅ | ❌ |
| `('GE', expr)` | `ge x` | `('GE', 'x')` | ✅ | ❌ |
| `('LISTA', name)` | `sätt x till lista` | `('LISTA', 'x')` | ✅ | ❌ |
| `('LÄGG_TILL', list, val)` | `lägg till x till lista` | `('LÄGG_TILL', 'lst', 'x')` | ✅ | ❌ |
| `('ELEMENT', list, idx)` | `element i ur lista` | `('ELEMENT', 'lst', 'i')` | ✅ | ❌ |
| `('ANTAL', list)` | `antal element i lista` | `('ANTAL', 'lst')` | ✅ | ❌ |

#### Uttryck (Expressions)

| IR nod | Språk-konstruktion | IR-exempel | X86 | WASM |
|--------|-------------------|------------|-----|------|
| `('PLUS', a, b)` | `a pluss b` | `('PLUS', 'x', 1)` | ✅ | ❌ |
| `('MINUS', a, b)` | `a minus b` | `('MINUS', 'x', 1)` | ❌ | ❌ |
| `('GENOM', a, b)` | `a delat b` | `('GENOM', 'x', 2)` | ❌ | ❌ |

## Nästa steg

### Hög prioritet
1. [x] **IF_ELSE** - parse.py stödjer OM med true_body och false_body
2. [ ] **Uppdatera IR** - använd svenska operatorer (mindre, likaMed, etc)
3. [ ] **Uppdatera x86 backend** - generera kod för OM (IF) med true/false body
4. [ ] **Uppdatera tokenizer** - mappar svenska keywords → IR operatorer

### Medel prioritet
5. [ ] **Fixa UT expression i x86 backend** (PLUS ok, MINUS/GENOM saknas)
6. [ ] **Implementera WHILE med OM-format** (nuvarande WHILE är annorlunda)

### Låg prioritet
7. [ ] WASM backend
8. [ ] Självkompilering

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn

## Exempel: hur IR ser ut (ny design)

```python
# Om-sats med else
('OM', 'x', 'mindre', '5',
    [('SKRIV', 'hej')],
    [('SKRIV', 'annat')])

# För-loop med body
('FÖR', 'i', '0', '10',
    [('SKRIV', 'i')])

# Sätt med uttryck
('SÄTT', 'n', ('PLUS', 'n', '1'))
```