# Module 03: Scanning JavaScript

**Goal:** find imports in JS/TS without a JavaScript parser and without Node.

## Tokenize first

A regex for `import ... from "x"` also matches that text inside comments and strings, and misses
statements spread across lines. So we tokenize: one master regex with alternatives for whitespace,
comments (both kinds), string literals (single, double, backtick) and everything else. Comments are
dropped. A string becomes one `("str", value)` token with its quotes removed. Now "find the string
after `from`" is a walk over a short token list.

The real server's tokenizer also handles template literals with nested `${}` and regex literals
(a `/` can start a regex or be division; it decides by the previous token). This tutorial keeps the
idea and drops those edge cases.

## The patterns

- `import ... from "x"`, `import "x"` (side effect), `export ... from "x"`, `export * from "x"`: scan from the keyword to the next string.
- `import type {T} from "x"`: same, flagged `type_only`.
- `import("x")` with a string: a dynamic import we *can* resolve. `import(variable)`: counted, not guessed.
- `require("x")`: same two cases.
- `obj.import("x")` is a method call, not the keyword: skip when the previous token is `.`.

## Resolving a specifier

A specifier is a *string*, not a module name. Relative ones (`./util`) resolve by Node's rules:

1. exact file
2. try each extension: `.ts`, `.tsx`, `.js`, ...
3. try `<path>/index.<ext>`

Bare specifiers (`react`) are packages from `node_modules`: external. (The real server also resolves
tsconfig `paths`/`baseUrl` aliases and monorepo workspace packages, and treats an alias-looking
specifier that matches nothing as *unresolved*, not external.)

## The honest limits

A tokenizer is not a parser. JSX text containing an apostrophe can start a bogus string, and
`require(x)` cannot be resolved. Both are stated in the real README rather than hidden.

Run it: `python 03-scanning-js/main.py`
