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

### HIUH tokenizer (hiuh-tokenizer.hiuh) - BRUTET
- Status: BRUTET - behöver mer arbete
- Problem: Binären outputtar bara `\x00` oavsett input (`printf "ab cd" | ./hiuh-tokenizer` ger tom output)
- Även git HEAD-versionen är trasig (den är 9768 bytes vs commit:ade 9768 bytes samma md5, men output är tom)
- Tidigare förväntat beteende: "ab\n001" för "ab cd" (första ordet + count)

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
- Inga kritiska buggar kvar i tokenizer eller kompilator

## Test-kommandon
```bash
# Bygga tokenizer
python3 native/hiuh-native.py --asm hiuh-tokenizer.hiuh > /tmp/tok.asm && as -o /tmp/tok.o /tmp/tok.asm && ld -o /tmp/tok /tmp/tok.o

# Testa tokenizer
printf "foo bar" | /tmp/tok

# Testa ord_lista för självkompilering
python3 native/hiuh-native.py --ord-lista hiuh-tokenizer.hiuh 2>/dev/null | wc -w
```
