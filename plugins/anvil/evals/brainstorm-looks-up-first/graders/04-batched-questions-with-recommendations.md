---
type: llm
weight: 1
---

PASS if the final message's questions to Saad come as one numbered batch (Q1, Q2, ... or 1., 2., ...), each with a recommended answer, and the message ends with a line inviting a single reply such as "Reply yes to take every recommendation, or yes except Q2: ...". An open "why do you want this" question with no recommendation is allowed as the first question. Questions listed under a spec's "Waiting on you" heading count if they follow the same rules.
FAIL if questions are scattered through the text, any closed question lacks a recommended answer, or the message asks a single question and promises more later.
