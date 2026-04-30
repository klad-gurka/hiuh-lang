# IR-noddokumentation

Detta dokument beskriver varje IR-nod i HIUH-kompilatorn.

## Satser (Statements)

### SÄTT
Tilldelning av variabel.

**Signatur:** `('SÄTT', name: str, expr: int|str|tuple)`

**Exempel:**
```python
('SÄTT', 'x', 5)                    # Sätt x till 5
('SÄTT', 'x', ('PLUSS', 'x', 1))    # Sätt x till x pluss 1
```

---

### FÖR
Räknarloop.

**Signatur:** `('FÖR', var: str, start: int, end: int, body: list[stmt])`

**Exempel:**
```python
('FÖR', 'i', 0, 10, [('SKRIV', ('VARIABEL', 'i'))])
```

---

### MEDAN
While-loop.

**Signatur:** `('MEDAN', condition: tuple, body: list[stmt])`

**Exempel:**
```python
('MEDAN', ('MINDRE', ('VARIABEL', 'x'), ('HELTAL', 5)),
    [('SÄTT', 'x', ('PLUSS', 'x', 1))])
```

---

### OM
If/else-villkor.

**Signatur:** `('OM', condition: tuple, true_body: list[stmt], false_body: list[stmt])`

**Exempel:**
```python
('OM', ('LIKA MED', ('VARIABEL', 'x'), ('HELTAL', 5)),
    [('SKRIV', 'ja')],
    [('SKRIV', 'nej')])
```

---

### BRYT
Avbryt pågående loop.

**Signatur:** `('BRYT',)`

**Exempel:**
```python
('BRYT',)
```

---

### HEJDÅ
Avsluta programmet.

**Signatur:** `('HEJDÅ',)`

**Exempel:**
```python
('HEJDÅ',)
```

---

### SKRIV
Skriv text eller uttryck.

**Signatur:** `('SKRIV', expr: str|int|tuple)`

**Exempel:**
```python
('SKRIV', 'hej världen')
('SKRIV', ('PLUSS', 'x', 1))
```

---

### SKRIV_VÄRDE
Skriv variabels värde.

**Signatur:** `('SKRIV_VÄRDE', name: str)`

**Exempel:**
```python
('SKRIV_VÄRDE', 'x')
```

---

### LÄS_RAD
Läs rad från stdin till variabel.

**Signatur:** `('LÄS_RAD', name: str)`

**Exempel:**
```python
('LÄS_RAD', 'namn')
```

---

### GREJ
Funktionsdefinition.

**Signatur:** `('GREJ', params: list[str], body: list[stmt])`

**Exempel:**
```python
('GREJ', ['x'], [('GE', ('GÅNGER', 'x', 2))])
```

---

### ANROPA
Funktionsanrop.

**Signatur:** `('ANROPA', func_name: str, args: list[expr])`

**Exempel:**
```python
('ANROPA', 'dubbla', [('VARIABEL', 'x')])
('SÄTT', 'y', ('ANROPA', 'dubbla', [('VARIABEL', 'x')]))
```

---

### GE
Returnera värde från funktion.

**Signatur:** `('GE', expr: int|str|tuple)`

**Exempel:**
```python
('GE', ('VARIABEL', 'x'))
('GE', ('PLUSS', 'x', 1))
```

---

### NY_LISTA
Skapa lista.

**Signatur:** `('NY_LISTA', name: str, items: list[expr])`

**Exempel:**
```python
('NY_LISTA', 'lst', [])                        # Sätt lst till ny lista
('NY_LISTA', 'lst', [1, 2, 3])                 # Sätt lst till lista av 1, 2, 3
```

---

### LÄGG_TILL
Lägg till element i lista.

**Signatur:** `('LÄGG_TILL', item: expr, list_name: str)`

**Exempel:**
```python
('LÄGG_TILL', 42, 'lst')
('LÄGG_TILL', ('VARIABEL', 'x'), 'lst')
```

---

### TA_BORT
Ta bort element efter värde.

**Signatur:** `('TA_BORT', value: expr, list_name: str)`

**Exempel:**
```python
('TA_BORT', 'apa', 'frukt')
```

---

### TA_BORT_INDEX
Ta bort element vid index.

**Signatur:** `('TA_BORT_INDEX', list_name: str, index: int)`

**Exempel:**
```python
('TA_BORT_INDEX', 'lst', 0)   # Ta bort första elementet
```

---

### HÄMTA_INDEX
Hämta element vid index.

**Signatur:** `('HÄMTA_INDEX', list_name: str, index: int)`

**Exempel:**
```python
('HÄMTA_INDEX', 'lst', 0)
```

---

### BYT_UT
Byt ut element vid index.

**Signatur:** `('BYT_UT', list_name: str, index: int, expr: expr)`

**Exempel:**
```python
('BYT_UT', 'lst', 0, 99)
```

---

### ANTAL
Antal element i lista.

**Signatur:** `('ANTAL', list_name: str)`

**Exempel:**
```python
('ANTAL', 'lst')
```

---

### SKRIV_FIL
Skriv till fil.

**Signatur:** `('SKRIV_FIL', path: str, data: str)`

**Exempel:**
```python
('SKRIV_FIL', 'hej.txt', 'innehåll')
```

---

### LÄS_FIL
Läs från fil.

**Signatur:** `('LÄS_FIL', path: str, var_name: str)`

**Exempel:**
```python
('LÄS_FIL', 'hej.txt', 'buf')
```

---

## Uttryck (Expressions)

### PLUSS
Addition.

**Signatur:** `('PLUSS', a: expr, b: expr)`

**Exempel:**
```python
('PLUSS', 'x', 1)
('PLUSS', ('VARIABEL', 'x'), ('HELTAL', 5))
```

---

### MINUS
Subtraktion.

**Signatur:** `('MINUS', a: expr, b: expr)`

**Exempel:**
```python
('MINUS', 'x', 1)
```

---

### GÅNGER
Multiplikation.

**Signatur:** `('GÅNGER', a: expr, b: expr)`

**Exempel:**
```python
('GÅNGER', 'x', 2)
```

---

### DELA
Division.

**Signatur:** `('DELA', a: expr, b: expr)`

**Exempel:**
```python
('DELA', 'x', 2)
```

---

### Jämförelseoperatorer

| Operator | Betydelse | Exempel |
|----------|-----------|---------|
| `mindre` | a < b | `('MINDRE', 'x', 5)` |
| `mindreLikaMed` | a <= b | `('MINDRE_LIKA_MED', 'x', 5)` |
| `större` | a > b | `('STÖRRE', 'x', 5)` |
| `störreLikaMed` | a >= b | `('STÖRRE_LIKA_MED', 'x', 5)` |
| `likaMed` | a == b | `('LIKA_MED', 'x', 5)` |
| `inteLikaMed` | a != b | `('INTE_LIKA_MED', 'x', 5)` |

---

### Variabler

**VARIABEL:** Referens till variabel.

**Signatur:** `('VARIABEL', name: str)`

**Exempel:**
```python
('VARIABEL', 'x')
```

---

### HELTAL
Heltalsliteral.

**Signatur:** `('HELTAL', value: int)`

**Exempel:**
```python
('HELTAL', 42)
```
