# GrantProof

A working GenLayer DApp for milestone-based grant funding. The funder freezes deliverables, criterion weights, evidence hosts, amounts and deadlines; the builder accepts; independent AI validators fetch public evidence and review delivery before funds can be allocated.

## Live deployment

- Website: https://grantproof.amzar1st96.chatgpt.site
- Contract: `0x54B09978AA69636073b147F1CD1FbB046524202C`
- [Contract explorer](https://explorer-studio.genlayer.com/address/0x54B09978AA69636073b147F1CD1FbB046524202C)
- [Deployment transaction](https://explorer-studio.genlayer.com/transactions/0x19ba4e91ade9bc2462b0a778e35f529b358fdb54d677e2726829ee5e3d36ba63)
- Network: Studionet, chain ID **61999**, RPC `https://studio.genlayer.com/api`.
- Constructor: response 60s; challenge 60s; revision 300s; final resolution 3600s after the current milestone due date. These short windows are for this demonstration deployment.

## Try the app

1. Open the app. It reads live finalized grant state without an account.
2. Choose **Create Studio test accounts**. The app generates funder and builder signing identities and requests 10 test GEN per account. Keys stay in the tab's session storage; closing the tab loses those identities. They are simulator accounts, not production wallets.
3. Create grant terms as the funder. Enter the designated builder, increasing delivery deadlines, allocation amounts, exact public evidence hosts and acceptance criteria. Every milestone's criterion weights must total 100%.
4. Fund the draft with the exact full grant amount, then switch to Builder and accept the fixed terms.
5. Submit a delivery summary and HTTPS evidence. Each side gets four ordinary slots. An optional SHA-256 pins the **complete raw fetched response bytes**, not rendered text.
6. After the evidence deadline, request validator review. Each validator independently fetches evidence and checks the criteria. No leader-only shortcut is used.
7. Either party can challenge once during the challenge window with additional evidence. This reopens evidence collection and requires a fresh review.
8. After the challenge deadline, finalize. A completed milestone credits its full allocation; a partial milestone credits only the agreed weights for proved criteria, with the remainder credited to the funder. Use **Withdraw** to transfer available credit.
9. An unresolved first review permits one revision. Missing acceptance or delivery, expired revision, and stalled review have contract-enforced timeout refunds accessible in the app.

All writes await **FINALIZED** and verify execution success before refreshing reads from `LATEST_FINAL`. Read errors are shown directly; no seeded fallback data is displayed.

## Evidence and payment design

- Terms cannot be edited after creation; full funding and designated-builder acceptance are required.
- Source hosts are set by the funder and accepted by the builder. Host comparison is exact: suffix matches, userinfo, unusual ports, HTTP and fragments are rejected. Criteria should identify the exact project, repository, release or analytics verifier; host approval alone does not establish ownership.
- Pages and party statements are untrusted data. README assertions, mockups and unsupported user counts alone do not prove functional deliverables.
- Fetch failures and hash mismatches are recorded and cannot support a payment. A funder's broken URL does not veto valid builder proof. A builder gains no payment through unavailable evidence. No party bonds are charged in this version.
- Decision citations must be successfully fetched URLs. Completed criteria are validated for uniqueness/range. Payouts are calculated deterministically from immutable weights, never an AI-chosen percentage.
- Comparative consensus independently recomputes the verdict, completed set and fetch outcomes. Reasoning is informational; the consensus result governs state.
- `MILESTONE_FAILED` refunds remaining grant escrow. First `REVISION_REQUIRED` or `INSUFFICIENT_EVIDENCE` preserves escrow for one revision; another unresolved result refunds. Absolute deadlines prevent indefinite locking even if review fails or consensus stalls.
- Accounting separates escrow and withdrawal credits. Finalization creates credits; `withdraw` zeroes the caller's credit before emitting a finalized native transfer. Milestone state cannot be settled twice.

## Verification

`npm test` executes 27 direct contract behavioral tests using a deliberately small GenLayer fixture. These validate authorization, funding amounts, weighted partial accounting/rounding, two-milestone settlement, early/late calls, reserved capacity, hash mismatches, fetch failures, one challenge, one revision, timeout refunds and withdrawal reuse. The fixture does not prove GenVM deployment compatibility or AI accuracy; live receipt/state verification provides separate evidence.

Nine frontend DOM tests cover finalized reads, payable signing, failed execution, role/deadline controls, dynamic terms and WebMCP readback. Cloud-browser visual QA was unavailable because the internal preview URL was blocked.

`npm run build` produces the public frontend. GitHub Actions repeats tests and build.

The live grant `grantproof-live-v1-1790762140947` reached **COMPLETED** with **MILESTONE_COMPLETED**. The builder withdrew **0.01 test GEN**; final escrow and withdrawable balances are both zero. All eight transactions finalized successfully.

See [docs/live-demo.json](docs/live-demo.json) for public transaction hashes and finalized state of the real **documentation milestone** demonstration. This demo checks public documentation delivery only; it does not claim 100-user onboarding or a production beta was verified.

## Development

```bash
npm ci
npm test
npm run dev
npm run build
```

Contract source: [contracts/grant_proof.py](contracts/grant_proof.py). Frontend: [src/main.js](src/main.js). Deployment configuration: [public/deployment.json](public/deployment.json).

Studionet is a hosted development simulator with temporary state. This deployment uses test GEN and short review windows. Private production evidence, image-based adjudication, independently authenticated analytics, multi-funder grants and token escrows are outside this version's scope. WebMCP exposes a read-only `read_grant` action in supporting browsers.
