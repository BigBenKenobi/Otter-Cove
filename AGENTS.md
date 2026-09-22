# Mandatory engineering rules

## Documentation standard — non-negotiable

Every new or materially modified code file must meet the explanatory standard
established by `app.py` and `main.py`. This is a completion requirement, not an
optional cleanup task.

- Start each substantive module with an idiomatic file-level docstring or header
  that explains its responsibility, architectural boundary, principal data flow,
  and relationship to the rest of Otter Cove.
- Give every important class a docstring that identifies its owner/creator,
  lifecycle, persistent or shared state, collaborators, and side effects.
- Give every significant function, method, event handler, and Qt lifecycle hook a
  docstring that explains its purpose, inputs/outputs where useful, mutations,
  failure behavior, and its role in the surrounding control flow.
- Add layered comments before non-trivial routing, validation, persistence,
  asynchronous work, state synchronization, UI-to-service boundaries, recovery,
  or resource-lifecycle blocks. Comments must explain intent and consequences,
  not restate obvious syntax.
- Document non-obvious variables, flags, caches, identifiers, and ordering rules
  at the point where their meaning affects future maintenance.
- Preserve accurate existing documentation. If behavior is intentionally unusual
  but its rationale is not supported by the code, describe what happens without
  speculating why.

Before declaring a coding change complete, review the diff specifically for
documentation coverage and accuracy. Run relevant syntax/tests after the comments
are added. A code change that does not meet this standard is incomplete.
