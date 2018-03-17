# Misc commands

## Convert simplified chinese to chinese traditional
```bash
cconv -f UTF8-CN -t UTF8-HK in.file -o out.file
```

## Convert dos line break to unix (Using vim)
```bash
nvim --noplugin --headless -c "set ff=unix" -c wq file.md
```

For batch convertion, wrap the file name variable in double quotation.
