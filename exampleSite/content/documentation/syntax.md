+++
title = "Syntax"
weight = 10
+++

## A struct with a function

```c
struct Point {
    int x;
    int y;
    fn norm2(self) -> int { return self.x * self.x + self.y * self.y; }
}
```
