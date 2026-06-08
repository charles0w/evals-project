---
agent: commerce
tags:
- ai-evals
- criteria
- commerce
---
# Criteria — Commerce Product Listing

Rubric for grading AI-generated product listings (shopify-arbitrage dropshipping copy, card-arbitrage relist descriptions) before they go live.

```text
Grade this AI-generated product listing on:
1. Accuracy — title, attributes, and specs match the actual source product.
   Penalize ANY invented spec, wrong size/condition, or unsupported claim hard.
2. Compliance — no prohibited or false claims (medical/cure, "authentic" without
   basis, fake scarcity, trademark misuse). A compliance violation caps the score low.
3. Completeness — has a clear title, price, condition, and the key buying attributes
   a customer needs to decide. Missing condition/price on a card listing is a major gap.
4. Persuasiveness — benefit-led and readable, without hype or false urgency.
5. Searchability — includes the terms a buyer would actually search, naturally.
Score 1.0 only if accurate AND compliant AND complete. Drop fast for invented specs
or prohibited claims.
```

- **Threshold:** 0.75 (compliance-sensitive — keep it strict).
- **Judge model:** different family than the listing generator (Haiku writes → judge with another).
- **Why these axes:** accuracy + compliance are gates, not nice-to-haves — a false claim is a chargeback/suspension risk, costlier than a bland listing.

## Changelog

- 2026-06-04 — initial rubric.

## See also

- llm-as-judge · judge-biases · README
