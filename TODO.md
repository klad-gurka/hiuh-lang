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
tools/
  hiuh-native.py    ← kompilator (Python)
```

## IR-nod dokumentation

| IR nod                               | Språk-konstruktion       | IR-exempel                                | X86 | WASM |
|--------------------------------------|--------------------------|-------------------------------------------|-----|------|
| `('SET', name, val)`                 | `sätt x till 5`          | `('SET', 'x', 5)`                         | ✅   | ❌    |
| `('SET', name, ('+', a, b))`         | `sätt x till a pluss b`  | `('SET', 'x', ('+', 'a', 3))`             | ✅   | ❌    |
| `('SET', name, ('-', a, b))`         | `sätt x till a minus b`  | `('SET', 'x', ('-', 'a', 'b'))`           | ❌   | ❌    |
| `('SET', name, ('*', a, b))`         | `sätt x till a gånger b` | `('SET', 'x', ('*', 'a', 'b'))`           | ❌   | ❌    |
| `('SET', name, ('/', a, b))`         | `sätt x till a delat b`  | `('SET', 'x', ('/', 'a', 'b'))`           | ❌   | ❌    |
| `('FOR', var, start, end, body)`     | `för x från 0 till 10`   | `('FOR', 'x', 0, 10, [body])`             | ✅   | ❌    |
| `('IF', (var, op, val), body)`       | `om x är 0`              | `('IF', ('x', '==', '0'), [body])`        | ✅   | ❌    |
| `('BREAK',)`                         | `bryt`                   | `('BREAK',)`                              | ✅   | ❌    |
| `('EXIT', code)`                     | `hej då` / `jag gå nu`   | `('EXIT', 0)`                             | ✅   | ❌    |
| `('SKRIV', expr)`                    | `skriv hello`            | `('SKRIV', 'hello')`                      | ✅   | ❌    |
| `('SKRIV_NL', expr)`                 | `skriv ny rad x`         | `('SKRIV_NL', 'x')`                       | ✅   | ❌    |
| `('SKRIV_VAR', name)`                | `skriv värdet av x`      | `('SKRIV_VAR', 'x')`                      | ❌   | ❌    |
| `('READ', buf)`                      | `läs`                    | `('READ', 'input_buf')`                   | ❌   | ❌    |
| `('STORE', buf, idx, val)`           | `lagra vid i i buf`      | `('STORE', 'buf', 'i', 'x')`              | ❌   | ❌    |
| `('LOAD', buf, idx)`                 | `tecken i ur buf`        | `('LOAD', 'buf', 'i')`                    | ❌   | ❌    |
| `('FUNC_DEF', name, params, body)`   | `grej namn param`        | `('FUNC_DEF', 'add', ['a', 'b'], [body])` | ❌   | ❌    |
| `('CALL', name, args)`               | `anropa namn med x`      | `('CALL', 'add', ['x', 'y'])`             | ❌   | ❌    |
| `('RETURN', val)`                    | `ge x`                   | `('RETURN', 'x')`                         | ❌   | ❌    |
| `('WHILE', (var, op, val), body)`    | `medan x är 0`           | `('WHILE', ('x', '==', '0'), [body])`     | ❌   | ❌    |
| `('LIST_CREATE', name)`              | `sätt x till lista`      | `('LIST_CREATE', 'x')`                    | ❌   | ❌    |
| `('LIST_APPEND', list, val)`         | `lägg till x till lista` | `('LIST_APPEND', 'lst', 'x')`             | ❌   | ❌    |
| `('LIST_GET', list, idx)`            | `element i ur lista`     | `('LIST_GET', 'lst', 'i')`                | ❌   | ❌    |
| `('LIST_LEN', list)`                 | `antal element i lista`  | `('LIST_LEN', 'lst')`                     | ❌   | ❌    |
| `('CONCAT', a, b)`                   | `a sammanfogat med b`    | `('CONCAT', 'a', 'b')`                    | ❌   | ❌    |
| `('FILE_OPEN', filename, mode, buf)` | `öppna fil för läsning`  | `('FILE_OPEN', 'data.txt', 'r', 'buf')`   | ❌   | ❌    |
| `('FILE_WRITE', filename, data)`     | `skriv till fil`         | `('FILE_WRITE', 'out.txt', 'hello')`      | ❌   | ❌    |

## Jämförelseoperatorer (används i IF/WHILE)

| Operator | Språk             | IR | X86 | WASM |
|----------|-------------------|----|-----|------|
| `==`     | `är`              | ✅  | ✅   | ❌    |
| `!=`     | `är inte`         | ❌  | ❌   | ❌    |
| `<`      | `är mindre än`    | ✅  | ✅   | ❌    |
| `>`      | `är större än`    | ✅  | ✅   | ❌    |
| `<=`     | `är mindre eller` | ❌  | ❌   | ❌    |
| `>=`     | `är större eller` | ❌  | ❌   | ❌    |

## Indentering

- ✅ Python-style: block bestäms av indentering, inga END-nyckelord
- Indentering: 4 spaces = 1 nivå

## Nästa steg

### Hög prioritet
1. [ ] **minus, gånger, delat** - aritmetik
2. [ ] **Läs input** - READ x86 syscall
3. [ ] **!=, >=, <=** - jämförelseoperatorer
4. [ ] **skriv värdet av x** - variabel-output

### Medel prioritet
5. [ ] **WHILE-loop** - medan x är 0
6. [ ] **Funktioner** - grej/anropa/ge
7. [ ] **Listor** - lägg till, element ur, antal

### Låg prioritet
8. [ ] File I/O
9. [ ] WASM backend

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn
- READ syscall är inte implementerad i x86.py
