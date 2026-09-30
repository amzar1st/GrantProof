# GrantProof documentation milestone

This is a deliberately small public documentation deliverable used to verify the funding workflow. It does not claim that a production beta or 100-user onboarding milestone is complete.

## Five verdicts

- MILESTONE_COMPLETED
- PARTIALLY_COMPLETED
- MILESTONE_FAILED
- REVISION_REQUIRED
- INSUFFICIENT_EVIDENCE

## Escrow rules

The funder defines immutable milestone amounts, due dates, exact evidence hosts and criterion weights totaling 10,000 basis points. The designated builder must accept the fully funded grant. Funds remain in escrow while validators independently fetch evidence and review each criterion. After a challenge window, a complete milestone receives its allocation; a partial milestone receives the agreed weighted share with the remainder credited to the funder. Both recipients use withdraw to transfer their credit.

## Deadline refunds

Missing acceptance, missing delivery, expired revision or stalled consensus can be recovered using resolve_timeout when the applicable deadline has expired. A first unresolved verdict permits one revision; an unresolved revised round refunds the remaining grant. No retrieval failure or mismatched hash earns a builder payment.
