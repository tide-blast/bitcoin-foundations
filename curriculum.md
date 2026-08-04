# Curriculum — Bitcoin Foundations

This document is the canonical plan for this learning project. It exists so that
progress and priorities don't depend on any single chat conversation — anyone
(including a future version of me, or an AI assistant helping me) can read this
file and understand exactly what's been done and what's next.

## Purpose

Build genuine, demonstrable technical literacy — Bitcoin protocol knowledge,
Linux/command-line fluency, Python basics, and disciplined Git/GitHub practice —
with the goal of supporting a technical job search (project management, solutions
engineering, or general tech roles) within roughly 2-3 months.

Bitcoin is the subject matter that motivates and structures the learning, but the
underlying skills (reading and explaining technical systems, using APIs, version
control discipline) are meant to generalize beyond Bitcoin-specific roles.

## Modules

### Module 0 — Repo hygiene
- Clean/confirm `.gitignore` behavior
- Fix folder naming issues
- Establish curriculum.md and progress-log.md as sources of truth

### Module 1 — Git deepening
- [x] Branching
- [x] Merge conflicts (created and resolved one deliberately)
- [ ] Reading `git log` fluently
- [ ] `.gitignore` patterns
- [ ] `git revert` vs `git reset`
- [ ] Writing clear commit messages as a habit

### Module 2 — Linux / terminal fundamentals (in progress)
- [ ] Filesystem navigation (pwd, ls, cd, mkdir, mv, cp, rm)
- [ ] Permissions (chmod, ownership)
- [ ] Processes (ps, top, kill)
- [ ] Piping and redirection (|, >, grep)
- [ ] Reading man pages / documentation

### Module 3 — Python fundamentals
- [ ] Variables, strings, numbers
- [ ] Control flow (if/while/for)
- [ ] Functions
- [ ] Lists and dictionaries
- [ ] Reading/writing files
- [ ] Calling an API, working with JSON

### Module 4 — Bitcoin protocol theory
- [ ] Hashing (SHA-256), Merkle trees
- [ ] Public-key cryptography, addresses
- [ ] UTXOs vs. account models
- [ ] Transaction structure
- [ ] Block structure, proof-of-work
- [ ] The P2P network (conceptual)

### Module 5 — Bitcoin Core + RPC (hands-on)
- [ ] Install Bitcoin Core
- [ ] Run on testnet/signet
- [ ] Use bitcoin-cli / JSON-RPC
- [ ] Explore real blocks and transactions

### Module 6 — Build
- [ ] Project 1: raw transaction decoder (Python)
- [ ] Project 2: RPC-based node info tool (Python)

### Module 7 — Polish + write-up
- [ ] Clean READMEs across all projects
- [ ] 2-3 short technical explainer articles in notes/
- [ ] Final portfolio review

## Working style notes

- Explanations should cover *why*, not just *what* — especially for terminal commands.
- Concepts should be predicted/reasoned through before being confirmed, where practical.
- Sessions may happen in separate chats; this file plus progress-log.md are the
  source of truth for continuity, not chat history.