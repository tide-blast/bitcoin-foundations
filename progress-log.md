# Progress Log — Bitcoin Foundations

Running log of study sessions. Newest entries at the top. Used both as a personal
journal and as a handoff reference when starting a new chat session with an AI
assistant — paste the most recent entry (or last few) at the start of a new chat
for continuity.

---

## 2026-08-04

**Covered:**

- File permissions: read/write/execute, owner/group/others breakdown of
  `ls -l` output (e.g., `rwx------`).
- Debugged a real issue: `chmod u-x` ran successfully (exit code 0) but
  never changed permissions. Root cause: the repo lives on an exFAT-formatted
  external drive, which doesn't support Unix permission bits at all — `ls -l`
  was just simulating a display, not showing real stored data.
- `grep` basics: searching file contents, `-n` (line numbers), `-i`
  (case-insensitive), `-v` (invert match / exclude).
- `find` basics: searching the filesystem by name (`find . -name "*.md"`),
  and that it recurses into subdirectories by default.
- Regex basics: `.` as wildcard vs `\.` as literal period (escaping).
- Combined `find` + `grep -v` to filter out `._` AppleDouble files from
  results — same underlying pattern as the Module 0 `git ls-files | grep`
  check, now with the "why" behind the escaping.

**Open items / next session:**

- Module 2 continues: processes (`ps`, `kill`, background jobs) still to cover.
- curriculum.md still shows "Module 0 — Repo hygiene (in progress)" —
  needs updating to reflect Module 0 and Module 1 are both complete.

**Confused / needs reinforcement:**

- (none flagged — exFAT/chmod debugging was worked through successfully)

## 2026-08-03

**Covered:**
- Fixed folder typo: `projects/bitcoin-dashborad` → `bitcoin-dashboard` (using `mv`)
- Learned that Git does not track empty directories at all — a rename of an
  empty folder produces no `git status` change.
- Read `git log` in full detail: commit hash, HEAD/branch pointers, author,
  date, and merge commits (which have two parents, one per branch merged).
- Practiced `git log --oneline --graph --all` to visually read branch
  splits and merges.
- `git revert`: creates a new commit that undoes an earlier one; original
  mistake stays visible in history. Safe on shared/pushed commits.
- `git reset --hard`: moves the branch pointer backward, makes commits
  after that point unreachable, and discards uncommitted working directory
  changes. Only safe on commits that haven't been pushed/shared yet.
- Confirmed practically: unpushed commits are safe to reset; pushed commits
  should be reverted instead, since others may have already built on them.

**Open items / next session:**
- Module 1 (Git) is now complete.
- Move into Module 2: Linux/terminal fundamentals (permissions, processes,
  grep/find, piping in more depth).
- Optional cleanup: delete the now-unused `conflict-demo` branch label
  (commits already merged, label just needs tidying).

**Confused / needs reinforcement:**
- (none flagged — reasoning checks throughout the session were solid)


## 2026-07-29

**Covered:**
- Reworked overall plan: shifted from "learn subjects broadly" to a hybrid —
  genuine protocol/technical understanding *and* a portfolio, since target roles
  may not be Bitcoin-specific (could be PM/marketing/solutions engineering in
  general tech).
- Decided on session structure: new chat per session, continuity maintained via
  curriculum.md + this log, not chat history.
- Terminal fundamentals: what a shell/prompt is, pipes (`|`), exit codes (`$?`),
  and the distinction between "no output" (success, nothing to report) vs an
  actual error.
- Confirmed via `git ls-files | grep '\._'` that macOS `._` AppleDouble files
  were never tracked by Git (harmless disk clutter, not a real issue).
- Set up `code .` shell command for launching VS Code from the terminal.
- Created curriculum.md and progress-log.md.

**Open items / next session:**
- Fix folder name typo: `projects/bitcoin-dashborad` → `bitcoin-dashboard`
- Commit and push curriculum.md + progress-log.md
- Continue Module 1 (Git): git log reading, revert vs reset
- Then move into Module 2 (Linux fundamentals)

**Confused / needs reinforcement:**
- (none flagged yet — will fill in as they come up)