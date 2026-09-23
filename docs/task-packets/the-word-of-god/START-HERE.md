# Start Terra here

Select Terra with Medium reasoning in your coding environment. Open a checkout
containing these documents (initial publication branch:
`docs/the-word-of-god-pilot`; use main once these documents are merged). The
implementation must use a separate branch, as described in packet 00-A.

Paste this prompt:

```text
Implement Pilot 1 of “The word of God” in the Otter-Cove repository.

Read AGENTS.md and docs/task-packets/the-word-of-god/README.md, then
OPERATING-GUIDE.md in the same directory. Follow its packet order exactly,
starting at 00-A, and read the corresponding PLAN.md task before each task.

You may inspect the repository, create an isolated implementation branch or
worktree, incorporate the reviewed R2 candidate as instructed, edit scoped code,
add meaningful regression tests, run checks with disposable data, and make local
commits. Make routine implementation decisions autonomously within the packets.
Do not modify my personal database/settings or discard existing working changes.

Complete the current task and its gate before beginning the next task. A gate
requires recorded evidence, not a promise. Diagnose and repair in-scope failures;
stop with a precise blocker when the required evidence cannot be obtained.
Do not weaken tests, change acceptance criteria, or skip a failed gate.

Keep a resumable run record using the supplied template. Continue automatically
after a passing gate. End with FINAL-pilot-handoff.md and then stop. Do not start
OC-05 or later work. Do not merge, publish a release, or change the open PR #6.
Leave a review-ready local branch and report its commits and evidence paths.
Do not push or open a PR unless I separately ask you to publish the implementation.

Native Fedora/reference acceptance may remain explicitly pending as the guide
allows; never describe offscreen checks as native acceptance.
```

## Resume after a context reset

Give Terra the checkout/branch and the run directory. Ask it to read the operating
guide and run index, inspect actual git status, and resume the first incomplete
packet. It must recheck evidence affected by intervening code changes. Do not
restart from an old branch or trust an unchecked completion label.
