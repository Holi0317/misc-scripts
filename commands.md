# Misc commands

## Convert simplified chinese to chinese traditional
```bash
cconv -f UTF8-CN -t UTF8-HK in.file -o out.file
```

## Convert dos line break to unix (Using vim)
```bash
nvim -N -c "set ff=unix" -c wq file.md
```

Wrap the script in a for loop for multiple files
