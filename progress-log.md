# Progress Log — Bitcoin Foundations

Running log of study sessions. Newest entries at the top. Used both as a personal
journal and as a handoff reference when starting a new chat session with an AI
assistant — paste the most recent entry (or last few) at the start of a new chat
for continuity.

---
## 2026-08-06
Covered:

* Session 1 — Variables, strings, numbers: `int` vs `float` distinction (and its
  real relevance to satoshis-as-ints vs BTC-as-floats), f-strings for embedding
  variables in text, `type()` to inspect a variable's type.
* String concatenation (`+`) vs f-strings — concatenation requires both sides to
  already be strings (`str()` needed to convert), f-strings auto-convert inside `{}`.
  Real gotcha hit directly: `"text" + int_variable` throws a TypeError.
* Type conversion: `int()`, `float()`, `str()` — including that `int("917234.5")`
  errors (won't silently drop the decimal; needs `int(float(...))` to do both steps).
* String methods: `.strip()`, `.upper()`, `.startswith()` — and why `.strip()`
  matters for real data (invisible whitespace breaks equality checks).
* Modulo (`%`) — remainder division, and its use for "every Nth item" checks
  (tied to real Bitcoin relevance: difficulty adjustment every 2016 blocks).
* Session 2 — Control flow: `if` / `elif` / `else`, comparison operators,
  `and` / `or` (built an `and` condition from scratch, including the mistake of
  writing `>= 1 and <= 5` instead of repeating the variable on both sides).
* `while` loops, including the infinite-loop trap (forgetting to increment the
  loop variable) and `Ctrl+C` as the escape hatch.
* `for` loops with `range()` — inclusive start, exclusive stop. Nesting `if`
  inside `for` — identified as the core recurring shape for processing lists
  of transactions/blocks later on.
* `break` (exit loop entirely) vs `continue` (skip current iteration only) —
  worked through a combined example correctly, including that `break`'s
  position in the loop body determines what gets checked before the exit.
* Interactive shell mechanic: blank line required to close and execute a
  multi-line block (`if`/`while`/`for`) typed directly into the shell —
  not needed when running from a `.py` file.

Module 3 (Python fundamentals) — Sessions 1 and 2 complete.

Open items / next session:

* Session 3: Functions.

Confused / needs reinforcement:

* None — syntax mistakes (capitalization, `=` vs `==`, smart quotes, missing
  colons) were self-corrected within 1-2 attempts each. No conceptual gaps.


## 2026-08-05

**Covered:**

- Processes: `ps` (default shows only current terminal's processes), `ps -A`
  (all system processes), reading PID/TTY/TIME/CMD columns.
- PID 1 (`launchd` on macOS) as the root of the process tree — everything
  else traces back to it.
- Combined `ps -A | grep -i <name>` to search for a process — hit a real
  gotcha: searching "chrome" matched Brave, Proton Mail, Adobe Acrobat, and
  VS Code, none of which are Google Chrome, because they're all built on the
  Chromium engine and share `chrome_crashpad_handler` / version strings.
  Good lesson that grep matches substrings, not app identity.
- `kill` basics: it's not "destroy," it's "send a signal." Plain `kill`
  (SIGTERM) = polite request, catchable, allows cleanup. `kill -9`
  (SIGKILL) = immediate, uncatchable, no cleanup — last resort only.
- Discussed real-world relevance ahead: `bitcoind` in Module 5 will need
  graceful shutdown (`bitcoin-cli stop`) rather than `kill -9`.
- Redirection: `>` (overwrite) vs `>>` (append). Confirmed the shell creates/
  truncates the destination file *before* the command even runs.
- Lived through a real `>` overwrite accident: ran `ls >` instead of `ps -A >`
  into the same file, silently wiping the prior contents — direct hands-on
  example of why `>` needs caution vs `>>`.
- `man` pages: `man <command>` opens documentation via the `less` pager;
  `q` to quit, spacebar to page forward, `/` to search within the page.

**Module 2 (Linux/terminal fundamentals) is now complete.**

**Open items / next session:**

- Starting Module 3: Python fundamentals (new chat).

**Confused / needs reinforcement:**

- Minor mix-up between `man`'s pager prompt (`:`) and the actual quit key
  (`q`) — resolved immediately, not a real sticking point.



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