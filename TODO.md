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

### IR-format
```python
('SET', 'x', 5)              # Sätt x till 5
('SET', 'x', ('+', 'a', 3))  # Sätt x till a pluss 3
('FOR', 'i', 0, 10, body)  # För i från 0 till 10
('IF', cmp, body)           # Om x är 0
```

## Nuvarande status (2026-04-28)

### ✅ Klart
- Tokenizer (tokenize.py)
- Parser → IR (parse.py)
- x86 Backend (backend/x86.py)
- Tester för alla delar

### ⚠️ Delvis implementerat
- SET: bara integer och plus
- FOR: grundläggande
- IF: är, är mindre, är större
- SKRIV/SKRIV_NL: grundläggande

## Uppgifter (baserat på README)

### Hög prioritet

#### 1. WHILE-loop
```python
# IR
('WHILE', cmp, body)
```
- [ ] tokenizer: 'Medan' → WHILE
- [ ] parse.py: parsa WHILE-block
- [ ] x86.py: generera loop kod
- [ ] tester

#### 2. Aritmetik (minus, gånger, delat)
```python
('SET', 'x', ('-', 'a', 'b'))  # minus
('SET', 'x', ('*', 'a', 'b'))  # gånger
('SET', 'x', ('/', 'a', 'b'))  # delat
```
- [ ] tokenizer: 'minus', 'gånger', 'delat'
- [ ] parse.py: parsa uttryck
- [ ] x86.py: generera asm för alla operatorer
- [ ] tester

#### 3. Fler jämförelseoperatorer
```python
('x', '!=', 'y')  # är inte
('x', '>=', 'y')  # är större eller
('x', '<=', 'y')  # är mindre eller
```
- [ ] tokenizer: 'är inte', 'är större eller', 'är mindre eller'
- [ ] parse.py: parsa nya operatorer
- [ ] x86.py: >=, <=, != i IF
- [ ] tester

#### 4. Läsning från användare (READ)
```python
# README: Läs - Läser text från användaren
('READ', 'buf')  # finns redan
```
- [ ] x86.py: implementera read-syscall
- [ ] testa med kompilerat program

### Medel prioritet

#### 5. Logiska operatorer (och, eller, inte)
```python
('AND', a, b)   # och
('OR', a, b)    # eller
('NOT', a)      # inte
```
- [ ] tokenizer
- [ ] parse.py
- [ ] x86.py (test/kör logiska op)
- [ ] tester

#### 6. Text/variabler (Skriv utan värde av)
```python
# README: Skriv Hej världen (ingen citationstecken!)
# Finns redan: SKRIV utan värdet av
```
- [ ] x86.py: output direkt text
- [ ] testa

#### 7. Listor
```python
('LIST_CREATE', 'x')           # Sätt x till lista
('LIST_APPEND', 'x', 'val')   # Lägg till val till x
('LIST_GET', 'list', 'idx')    # element idx ur lista
('LIST_LEN', 'list')           # Antal element i lista
```
- [ ] tokenizer: 'lista', 'lägg till', 'element', 'antal'
- [ ] parse.py
- [ ] x86.py: list-implementation (array i minnet)
- [ ] tester

#### 8. Strängmanipulation
```python
('CONCAT', 'a', 'b')     # a sammanfogat_med b
('CHAR_AT', 'text', 'idx')  # tecken idx ur text
```
- [ ] tokenizer
- [ ] parse.py
- [ ] x86.py
- [ ] tester

#### 9. Funktioner (Grej/Anropa)
```python
('FUNC_DEF', 'namn', params, body)
('CALL', 'namn', args)
```
- [ ] tokenizer: 'Grej', 'Anropa', 'med'
- [ ] parse.py: funktionsdef + anrop
- [ ] x86.py: call/ret, stack frames
- [ ] tester

### Låg prioritet (kräver mer design)

#### 10. File I/O
```python
('FILE_OPEN', 'fil', 'mode', 'buf')
('FILE_WRITE', 'fil', 'text')
```
- [ ] designa API
- [ ] implementera

#### 11. Typ-system (statisk typkontroll)
```
README: Heltal, Decimal, Text, JaNej
```
- [ ] definiera typer
- [ ] type checker i parse/compile
- [ ] typfel vid kompilering

### Bootstrapping

#### 12. Självkompilering
- [ ] HIUH-parser i HIUH (src/hiuh/parse.py → hiuh/parse.hiuh)
- [ ] HIUH-backend i HIUH (src/hiuh/backend/x86.py → hiuh/backend/x86.hiuh)
- [ ] Kompilera hiuh.exe med sig själv

## Kända buggar/problem

- `i` är keyword `IN` → kan inte användas som variabelnamn
- x86.py: SKRIV/SKRIV_NL med variabler är inte fullständigt testat
- READ syscall är inte implementerad i x86.py
