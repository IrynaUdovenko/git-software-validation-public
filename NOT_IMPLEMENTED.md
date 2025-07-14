# Not Implemented Yet

This document outlines Git features and test flows that were intentionally excluded from Phase 1 and are planned for implementation in Phase 2 and beyond.

The structure follows the original [Mindmap](./Git_Software_Validation.png) and continues the modular, layered approach to test design.

---

## Authentication & SSH

SSH-based authentication is not yet implemented due to the complexity of setting up SSH daemons, managing key pairs, and ensuring secure flows within CI environments.

However, the test architecture is already prepared to support SSH-based validation.

### Planned Test Cases

#### Positive Flows
- Add a valid deploy key
- Clone with a valid SSH key
- Push with a valid SSH key
- Pull with a valid SSH key
- Support for multiple valid keys per repo
- Simulated key rotation during CI runs

#### Negative Flows
- Clone without an SSH key
- Pull using an incorrect or expired key
- Push as an unauthorized user
- Fetch using a malformed or revoked key
- Push with a read-only or restricted key

### Implementation Notes
- `ssh-server` will be embedded in the `git_bare_server` fixture (likely via OpenSSH inside test container or subprocess)
- Temporary SSH key pairs will be generated per test
- `GIT_SSH_COMMAND` will override default SSH behavior to inject test-specific logic
- SSH-related tests will be organized in `test_ssh_auth_phase2.py`

---

## Advanced Git Commands (Core Extensions)

Several Git commands were excluded in Phase 1 but are essential for broader coverage of real-world workflows.

### Planned Commands
- `git status` – check tracked/untracked/modified states
- `git diff` – show staged vs. unstaged changes
- `git reset` – unstage files, soft or hard reset of commits
- `git checkout` / `switch` – navigate between commits/branches
- `git reflog` – view local history of `HEAD` movements

These commands will be validated with different **flags, modifiers, and combinations**, including:

- `git diff --cached`
- `git reset --hard`
- `git checkout -b <branch>`
- `git reflog show --date=relative`

Future tests will be organized in `test_core_extensions_phase2.py`.

---

## Branching & Collaboration

Branching workflows are fundamental to Git but were not implemented in Phase 1.

### Planned Test Cases
- Create new branches and switch between them
- Merge feature branches into main
- Detect and resolve merge conflicts
- Rebase commits onto another branch
- Use `stash` to temporarily save work

This section introduces divergent repo histories, complex integration paths, and user-like decision flows.

Future tests will be grouped in `test_branching_phase2.py`.

---

## Remote Edge Cases

Remote operation edge cases were postponed due to lower priority for Phase 1, but they are critical for robustness.

### Planned Scenarios
- Force push (`--force`, `--force-with-lease`)
- Push to orphaned branches
- Push without upstream tracking
- Push to read-only remote
- Pull from a stale or divergent remote
- Push after remote history rewrite

These will help validate Git behavior in conflict-heavy or restricted environments.

Expected implementation in `test_remote_edge_cases_phase2.py`.

---

## Advanced Integration Scenarios

Phase 2 will include complex integration tests, simulating real-world, multi-step user workflows.

### Planned Features
- Combine multiple commands in realistic usage sequences
- Simulate multi-user workflows (two or more clones)
- Chain push-pull-rebase operations across clients
- Validate the interaction of flags (e.g., `--amend`, `--no-ff`, `--squash`)
- Use parameterized tests to cover variant combinations

These tests will not only validate command correctness but also **usability and expected developer experience**.

Expected implementation in `test_integration_flows_phase2.py`.

---

## Summary

The following areas are intentionally deferred to Phase 2 and beyond:

- SSH authentication (positive & negative cases)
- Advanced core commands with various flag combinations
- Branching, merging, rebasing, and stashing
- Edge-case remote interactions
- Sophisticated user scenarios and integration chains

All features above are covered in the [Mindmap](./Git_Software_Validation.png) and will follow the same CI-ready, fixture-driven approach used in Phase 1.

The project is designed to scale — tests will continue evolving from isolated commands to **real Git workflows**, covering both nominal paths and edge cases in reproducible environments.
