# HIUH Native Compiler

Kompilerar HIUH → x86-64 maskinkod för Windows och Linux!

## Plan

- [ ] Lexer/Parser för HIUH
- [ ] AST-representation  
- [ ] x86-64 kodgenerator
- [ ] ELF/PE format output
- [ ] Windows .exe output

## Bygge

```bash
# Linux
make linux

# Windows (via mingw)
make windows
```

## Mål

Kompilera detta:
```
Skriv Hej världen
```

Till native binary utan mellansteg!
