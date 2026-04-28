# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Status

### Python-kompilatorn (native/hiuh-native.py) - KLAR
- [x] Tokenizer - fungerar i Python
- [x] Parser - fungerar
- [x] Kodgenerator - genererar x86_64 assembly
- [x] Funktioner (lambda-style)
- [x] IF-ELSE i loopar
- [x] Nästlade loopar

### HIUH tokenizer (hiuh-tokenizer.hiuh) - KLAR (v5, 2026-04-28)
- [x] Status: FUNGERAR! Korrekt word-end detection med f-guard
- Fix 5 (v5): Word-end detection race condition. f=1 efter whitespace/null,
  f=0 efter lagring. Lagra endast printable chars när f=0.
- Test: `printf "ab cd\n" | ./hiuh-tokenizer` ger `ab` och `cd` som separata rader

## SJÄLVKOMPILERING - vägen dit

### Nuvarande flöde för självkompilering
1. hiuh-native.py (Python) tokenizerar hiuh-tokenizer.hiuh
2. Ger ord_lista: 212 ord
3. För att kompilera hiuh-tokenizer.hiuh med sig själv, behöver HIUH-ord-listan
   producera samma tokenström som Python-tokenizern

### Nästa steg (prioriterad ordning)
1. [ ] Självkompilering: bygg HIUH-parser i HIUH (för att bygga uttryck)
2. [ ] Bygg HIUH-kodgenerator i HIUH (för att generera asm)
3. [ ] Självkompilerad hiuh.exe som kan kompilera hiuh-tokenizer.hiuh

## Kända buggar
- Output innehåller fortfarande lite garbage pga oinitierad buffer (mindre problem)

## Test-kommandon
```bash
# Bygga tokenizer
python3 native/hiuh-native.py hiuh-tokenizer.hiuh

# Testa tokenizer
printf "ab cd\n" | ./hiuh-tokenizer

# Testa ord_lista för självkompilering
python3 native/hiuh-native.py --ord-lista hiuh-tokenizer.hiuh 2>/dev/null | wc -w
```
