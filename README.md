# json-parser

Simple parser for a JSON subset in Python. Warning: code is extremely spaghetti.

## but why?

I already have a compiler ([zen, btw](https://github.com/pes18fan/zen)), so why
am I making just a JSON parser?

Well, I saw [this tweet](https://x.com/TheGingerBill/status/1874621905451593738)
from Odin creator gingerbill, and just thought, "Hmm... I did write a compiler,
but I was just following a book. Do I really know how to implement lexing and
parsing?" So I spent a few hours trying to do it. And thankfully, as it turns
out, I can indeed do it. Served as some good brain exercise too.

## (rather informal) ebnf grammar

```ebnf
json ->  "{" (pair ",")* pair "}"
pair ->  key ":" value

key   -> str
value -> str | num

str   -> "\"" CHAR* "\""
num   -> DIGIT*

DIGIT -> "0" - "9"
CHAR  -> any unicode character
```
