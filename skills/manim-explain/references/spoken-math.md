# Spoken math for TTS

**Rule:** On-screen = LaTeX. Narration = natural spoken English. Never paste `MathTex` source into TTS.

When unsure how to speak a symbol or expression, look it up (e.g. MathSpeak / ClearSpeak / Wikipedia “mathematical pronunciation”) and record the choice in `script.yaml` comments if non-obvious.

## Project-specific glossary (top-k on-mass demo)

| On screen | Speak as |
|-----------|----------|
| top-$k$ | "top k" |
| on-mass / \(\mathrm{on\text{-}mass}(c)\) | "on-mass" or "on-mass of class c" |
| class-response distribution | "class-c response distribution" (prefer over "profile") |
| \(\mu_{c,j}\) | "mu sub c j" or "the class mean for unit j" |
| \(\|\mu_{c,j}\|\) | "the absolute value of mu" / "absolute class mean" |
| \(S_c\) | "S sub c" or "the top set for class c" |
| \(f\) | "f" or "the set fraction f" |
| \(fF\) | "f times F" / "f F units" |
| \(\sum_{j\in S_c}\) | "the sum over j in S sub c" |
| fraction bar | "divided by" / "over" |
| \(\sig\) / \(\sigma\) | "sigma" (bias scale) |
| \(10\%\) | "ten percent" |

## General patterns

| LaTeX-ish | Speak |
|-----------|--------|
| \(a/b\), \(\frac{a}{b}\) | "a over b" |
| \(a_b\) | "a sub b" |
| \(a^b\) | "a to the b" / "a to the power b" |
| \(\sum\) | "the sum of" |
| \(\prod\) | "the product of" |
| \(\approx\) | "approximately" |
| \(\gg\) | "much greater than" |
| \(\in\) | "in" |
| \(\|\cdot\|\) | "the absolute value of" / "the norm of" (context) |

## Script hygiene

- Put display math only under beat field `latex` / `show`, never inside `say`.
- Prefer teaching words over symbol soup in VO: *"sum the gold heights, divide by the total"* while the formula is on screen.
- Keep numbers speakable: "zero point four eight" or "about one half."