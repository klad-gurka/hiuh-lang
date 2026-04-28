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

### HIUH tokenizer (hiuh-tokenizer.hiuh) - FIXAD (2026-04-28)
- Status: FIXAD - tokenizer kompilerar och fungerar!
- Fix 1: Tokenizer bug - `elif 'är' in words` matched substring 'är' i compound-ord som 'Sättantal'. Fix: ny `elif first.startswith('Sätt')` gren före 'är'-checks.
- Fix 2: `Sätttecken till tecken i input_buf` använde `words[3:]` istället för `words[2:]` för rest-värde.
- Fix 3: Parse bug - sista IF (no ELSE) i FOR body konsumerade FOR's END-token via `if tokens[i][0] == 'END': i += 1`, vilket placerade post-loop statements inuti loopen. Fix: ta bort den felaktiga `i += 1`.
- Fix 4: Flag-based nested IF approach för att komma runt kompilatorns bristfälliga nästning.
- Test: `printf "ab cd\n" | ./tok` ger `ab` `cd` (var för sig)
- Commits: [Denna commit]

## SJÄLVKOMPILERING - vägen dit

### Nuvarande flöde för självkompilering
1. hiuh-native.py (Python) tokenizerar hiuh-tokenizer.hiuh
2. Ger ord_lista: 153 ord
3. För att kompilera hiuh-tokenizer.hiuh med sig själv, behöver HIUH-ord-listan
   producera samma tokenström som Python-tokenizern

### Nästa steg (prioriterad ordning)
1. [ ] Fixa tokenizer-buggen (word-end detection med "klar"-flagga)
2. [ ] Bygg HIUH-parser i HIUH (för att bygga uttryck)
3. [ ] Bygg HIUH-kodgenerator i HIUH (för att generera asm)
4. [ ] Självkompilerad hiuh.exe som kan kompilera hiuh-tokenizer.hiuh

## Kända buggar
- Output innehåller fortfarande lite garbage pga oinitierad buffer (mindre problem)

## Test-kommandon
```bash
# Bygga tokenizer
python3 native/hiuh-native.py --asm hiuh-tokenizer.hiuh > /tmp/tok.asm && as -o /tmp/tok.o /tmp/tok.asm && ld -o /tmp/tok /tmp/tok.o

# Testa tokenizer
printf "foo bar" | /tmp/tok

# Testa ord_lista för självkompilering
python3 native/hiuh-native.py --ord-lista hiuh-tokenizer.hiuh 2>/dev/null | wc -w
```
