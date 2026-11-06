# Break it: Module 03

1. Add `import x from "./a"; // trailing comment with "./b"` to the sample. Is `./b` reported?
2. Put an `import` inside a template literal: `` const t = `import "./c"`; ``. Does the tokenizer see a string or code?
3. Write `export const name = "./lazy";`. Is it reported as an export-from? Why not?
4. Write a regex literal containing a quote: `const r = /"/;`. What happens to the rest of the file? (This is why the real tokenizer special-cases `/`.)
5. Import `./dir` where `dir/index.ts` exists. Does your resolver find it? What about `./util.js` when only `util.ts` exists (TypeScript ESM style)?
