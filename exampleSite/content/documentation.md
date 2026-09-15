+++
title = "Documentation"
+++

## Language reference

- Syntax — C-compatible, plus `struct { fn ... }` method blocks
- Types — value semantics by default, explicit pointers
- Modules — single-file compilation units, `import` for cross-file references

### A struct with a function

```c
struct Point {
    int x;
    int y;
    fn norm2(self) -> int { return self.x * self.x + self.y * self.y; }
}
```

> anti keeps C's syntax and semantics where they already work.

## Compiler (antic)

| Command | Does |
|---|---|
| `antic build main.an -o main` | compile to a native binary |
| `antic run main.an` | compile, then run |

```
antic build main.an -o main
antic run main.an
```
