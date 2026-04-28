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
- Självkompilering: tokenizer tokenizes sig själv → 57 ord (varje ord på egen rad)
- [x] Rebuilt binary (2026-04-28) och commitater

## SJÄLVKOMPILERING - vägen dit

### Nuvarande flöde för självkompilering
1. hiuh-native.py (Python) tokenizerar hiuh-tokenizer.hiuh
2. Ger ord_lista: 152 ord
3. För att kompilera hiuh-tokenizer.hiuh med sig själv, behöver HIUH-ord-listan
   producera samma tokenström som Python-tokenizern

### Nästa steg (prioriterad ordning)
1. [ ] Självkompilering: bygg HIUH-parser i HIUH (för att bygga uttryck)
   - Ett HIUH-program som kan pars-a HIUH-kod och bygga ett AST
   - Behöver läsa ord-lista (från tokenizer) och producera strukturerad output
2. [ ] Bygg HIUH-kodgenerator i HIUH (för att generera asm)
   - Tar AST och genererar x86_64 assembly
3. [ ] Självkompilerad hiuh.exe som kan kompilera hiuh-tokenizer.hiuh

## Språkdesign — beslutade riktningar

### Typsystem (statisk typning, beslutad)
- [ ] Lägg till `var_type` dict parallellt med `var_reg` i kompilatorn
- [ ] Typer: `Heltal` (64-bit int), `Text` (sträng), `Sant/Falskt` (bool)
- [ ] Typinferens från första tilldelning — ingen explicit deklaration krävs
- [ ] Kompileringsfel vid typkonflikt (t.ex. tilldela Text till Heltal)
- [ ] Funktionssignaturer med returtyp: `ge Heltal` / `ge Text`
- Beslut: statisk typning, inferred från tilldelning, ingen pekare exponerad

### Funktionsanrop (verkliga call/ret, se parser.plan.md §4)
- [ ] Riktig prologue/epilogue per funktion
- [ ] Windows x64 ABI: argument i rcx/rdx/r8/r9, returvärde i rax
- [ ] `Anropa` / `Sätt x till Anropa` syntax
- [ ] Per-funktion variabelallokering (nollställ var_reg vid FUNC_DEF)

### Minnesmodell (beslutad — se DESIGN.md)
- Värdesemantik: tilldelning kopierar alltid, inga delade buffertar
- Text är 256 byte internt, kompilator-genererat namn (_text_0 etc)
- Overflow → runtime abort med tydligt felmeddelande, aldrig tyst trunkering

#### Implementera typsystem
- [ ] Lägg till `var_type` dict i `compile_to_asm` (parallellt med `var_reg`)
- [ ] Vid `SET`: härled typ från värdet (heltal-literal → Heltal, buf → Text)
- [ ] Vid `SET`: kontrollera att ny typ matchar befintlig, annars kompileringsfel
- [ ] `READ_RES` → typ Heltal (returvärde 0/1)
- [ ] `Läs` utan till → tilldelar till implicit Text-variabel `_las_buf`

#### Implementera Text-typ
- [ ] `alloc_text(var)` — genererar `_text_N`-buffert, registrerar i `text_bufs`
- [ ] Tilldelning Text→Text kompileras till `KopieraBuffer`
- [ ] Tilldelning strängliteral→Text kompileras till inline byte-copy
- [ ] `SkrivNyRad`/`Skriv` på Text-variabel → använder rätt buffert automatiskt
- [ ] `Jämför`/`JämförBuffer` på Text-variabler → slår upp buffertnamn automatiskt

#### Implementera overflow-skydd
- [ ] Efter varje `KopieraBuffer` / strängtilldelning: kontrollera att källan ≤ 256 byte
- [ ] Runtime-check: lägg till längdkoll i genererad assembly
- [ ] Felmeddelande: `FEL: Text overflow i variabel 'X'` + exit 1

## Kända buggar
- Inga kritiska buggar i tokenizer (2026-04-28)
- TODO: Hur läser ett HIUH-program ord-listan från tokenizer? Behöver FIOLÄS.

## Test-kommandon
```bash
# Bygga tokenizer
python3 native/hiuh-native.py hiuh-tokenizer.hiuh

# Testa tokenizer
printf "ab cd\n" | ./hiuh-tokenizer

# Testa ord_lista för självkompilering
python3 native/hiuh-native.py --ord-lista hiuh-tokenizer.hiuh 2>/dev/null | wc -w
```
