# HIUH Självkompilering - TODO

## Mål
- [ ] HIUH kompilator skriven i HIUH som kan kompilera sig själv

## Överblick Architecture
1. **Tokenizer** - dela input i ord (ord-gränser vid mellanslag)
2. **Parser** - bygg tokens till statements
3. **Kodgenerator** - generera x86_64 assembly

## TODO - Fixa buggar

### Hög prioritet
- [ ] IF-ELSE i FOR fungerar inte - FOR konsumerar ELSEE token
- [ ] cmp $0, %al efter CMP_LT genererar ingen CMP_LT-instruktion
- [ ] 'tecken' variabeln inte tillgänglig som väntat

### Medium prioritet  
- [ ] Tokenizer: bygg ord genom att jämföra med mellanslag (32)
- [ ] Lagra tokens i en lista

### Lower prioritet
- [ ] Självkompilering: HIUH kompilerar HIUH

## Känd bugg - IF i FOR
```
För i från 0 till 10
    Om tecken_kod är mindre än 32
        Skriv Sp
    Hejdå
Hejdå
```
FOR-loopen konsumerar tokens tills END, inklusive IF/ELSE. IF-handlern hinner inte processa ELSE.

## Test-kommandon
```bash
# Testa tokenizer
echo "Hej världen" | python3 native/hiuh-native.py --stdin /tmp/test && /tmp/test

# Kompilera tokenizer.hiuh
python3 native/hiuh-native.py hiuh-tokenizer.hiuh /tmp/test && echo "ABC" | /tmp/test
```

## Commit
- senaste: 97fb922 "WIP: tokenizer with char comparison"
