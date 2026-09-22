# Changelog

All notable changes to Otter Cove are documented here.

## Unreleased

- Add validated non-secret model registry edit/remove/capability queries and a
  persistent capability-default resolver with ordered, stale-safe fallbacks.
- Add a Local Data Settings tab for atomic JSON export, confirmed import and
  confirmed reset, with explicit affected/excluded scope and visible errors.
- Add native animation instrumentation for 1720×900/Balanced frame intervals and
  paint cost, refusing to treat offscreen measurements as acceptance evidence.
- Isolate persistent and Nobody message views and drafts, report their actual storage policy, and dispose memory-only sessions when New Chat closes them.
- Replace the fixed Nobody-button width with content-aware sizing for Large text and Roomy density.
- Disable and label sensitive blur, Web Search and Shell controls until their runtime consumers exist; describe the implemented summary as session storage status.
- Preserve the complete composer draft and selected mode when local message storage fails; a successful retry now clears the accepted draft once and adds one message.

- Consolidated original reference media and acceptance records under docs; recorded architecture/decisions, all-step acceptance ledger, testing matrix and historical GUI review.
- Preserved a fresh 65/65 offscreen test/smoke record with source hashes; clarified that Git tagging and native/manual acceptance remain outstanding.

- Adopted the latest GUI review as the sole PLAN.md, retired PLAN.txt, shortened ROADMAP.md to execution order, and refreshed STATUS.md with known gaps and evidence.

- Established the standard project, documentation, acceptance-evidence, and reference-asset layout.
