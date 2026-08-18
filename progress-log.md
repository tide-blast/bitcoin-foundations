# Progress Log — Bitcoin Foundations

Running log of study sessions. Newest entries at the top. Used both as a personal
journal and as a handoff reference when starting a new chat session with an AI
assistant — paste the most recent entry (or last few) at the start of a new chat
for continuity.

---

2026-08-18
Covered:

* Session 2 — Public-key cryptography, addresses: private/public key
  relationship (private key easy to derive public key from, practically
  impossible in reverse), generated a real secp256k1 key pair via `ecdsa`
  library. Confirmed structurally why public key (128 hex chars) is
  ~2x the length of private key (64 hex chars) — public key is a curve
  point (X + Y coordinates), private key is a single number.
* Signing and verification: signed a message with the private key,
  verified using only the public key + signature + message (no private
  key needed for verification — confirmed by reasoning before testing).
  Manually sliced a signature into its r/s components (64 hex chars
  each), tying back to a supplementary ECDSA math session covered
  separately.
* Verification failure case: verifying against an altered message
  correctly raises `BadSignatureError` rather than returning `False` —
  confirmed hands-on.
* Important distinction surfaced and corrected: signing is NOT
  encryption. Transaction data broadcasts fully public/unencrypted;
  the signature proves authorization, not secrecy. Clarified that
  verification (hash message, check against signature using public key)
  is performed broadly by all full nodes, not just miners — miners
  do the same check, just with an added incentive to get a valid block
  accepted.
* Supplementary session (separate chat): worked through a general
  sign+encrypt message exchange between two parties (Party A/B) to
  build intuition for how a message, signature, and public key all
  verify against a private key without ever exposing it. Then
  compared that general model against Bitcoin's actual approach —
  confirmed Bitcoin skips encryption entirely (no secrecy step, since
  the transaction is meant to be publicly readable) and that
  verification is performed by every node on the network, not a
  single recipient. This directly reinforced and predated the
  signing-vs-encryption distinction raised and corrected in the main
  Module 4 session.
* Addresses: built a simplified address by hashing the public key with
  SHA-256 (`pubkey_bytes = public_key.to_string()` — noted `.to_string()`
  actually returns bytes despite the name, a library-naming quirk, not
  something reasoned toward). Discussed why hashing matters: public key
  stays hidden until spend time, giving a security margin even if
  elliptic curve math were ever broken. Noted real addresses add
  RIPEMD-160 + Base58Check/Bech32 encoding on top (not built, discussed
  only).
* Session shell state was lost partway through (browser/session issue)
  — session was cleanly restarted from the top; no material lost,
  concepts re-covered quickly on second pass.
* Minor troubleshooting: hit `NameError: name 'hashlib' is not defined`
  after the restart (import carried over from Session 1's now-closed
  shell, not the new one) — self-diagnosed and correctly re-ran
  `import hashlib` without prompting.

* Session 3 — UTXOs vs. account models, transaction structure: UTXO
  model explained via cash/denominations analogy (discrete unspent
  "bills," no partial spending, change becomes a new UTXO). Correctly
  reasoned through a worked example (2 BTC + 0.5 BTC UTXOs spent to
  pay 2.3 BTC, yielding 0.2 BTC change) before being shown structure.
* Transaction defined precisely: a signed, self-contained record that
  consumes specific existing UTXOs as inputs and produces new UTXOs as
  outputs — no balance tracking anywhere in the system.
* Confirmed each input is signed separately (not one blanket signature
  per transaction), since different UTXOs may be locked to different
  addresses/keys.
* Address reuse and privacy: discussed why wallets generate a new
  address per incoming payment (avoids trivially linking all of a
  person's transaction history via one address), and the real limits
  of this — address clustering when UTXOs are spent together, and
  potential identity links via KYC exchanges. Correctly identified this
  as obfuscation, not full anonymity.
* Corrected an imprecise explanation from Claude: an output's address
  (hash) is a locking condition/label, not something that itself
  requires a private key to create or that "unlocks" anything on its
  own — the actual unlocking proof happens later, at spend time, via
  public key + signature.
* Built a full simplified transaction as a Python dict: two inputs
  (each with `prev_tx_id`, `output_index`, `signature`, `public_key`)
  and two outputs (`amount`, `address`) — mapped directly onto the
  worked UTXO example above.
* Fees: corrected an initial guess that fees involve an explicit extra
  input/output. Clarified fee = total inputs − total outputs, with the
  gap implicitly claimed by whichever miner includes the transaction,
  via their own coinbase transaction (not encoded in the spender's
  transaction at all). Modified the example transaction to include a
  real 0.0005 BTC fee and confirmed the arithmetic.
* Correctly separated block subsidy (new bitcoin, Session 4 topic) from
  transaction fees (this session's topic) unprompted.

** Module 4, Sessions 2 and 3 complete. **

Open items / next session:

* Session 4: Block structure, proof-of-work.

Confused / needs reinforcement:

* None of real substance — several initially-imprecise phrasings from
  Claude were caught and corrected in discussion (e.g. "obscured but
  deterministic layer" reasoning on addresses, "unlocking via hash"
  wording, fee-as-extra-input assumption). No repeated errors; strong
  session overall, particularly on transaction/fee mechanics.


---

2026-08-17
Covered:

* Session 1 — Hashing (SHA-256) and Merkle trees. Covered hash function
  properties hands-on: deterministic, one-way, avalanche effect —
  confirmed by comparing `hashlib.sha256("hello")` vs `"Hello"` outputs
  (same length, no resemblance) and re-running the same input to confirm
  identical output. Correctly reasoned that determinism is what allows
  independent nodes to reach consensus without coordination.
* Merkle trees: defined structure (pairwise hashing up to a single
  root). Correctly predicted the 4-leaf/3-level structure before being
  shown code. Built a 4-transaction Merkle tree from scratch in the
  Python shell (Level 0 leaf hashes → Level 1 pair hashes → Level 2
  root), computing each level manually.
* Demonstrated the avalanche effect at the Merkle tree level: edited
  one transaction, rebuilt the tree, and correctly traced which
  branches changed (the modified leaf's path up to the root) vs. which
  stayed identical (the untouched sibling branch) — correctly
  articulated that the root always changes even when only one leaf out
  of several is modified, since the root transitively depends on
  everything below it.
* Covered the odd-transaction-count edge case: Bitcoin's rule of
  duplicating the last hash at a given level when the count is odd,
  walked through a 5-transaction example across multiple levels.
* Briefly discussed why Bitcoin uses double SHA-256 (defense against
  length-extension attacks) — noted at Darrell's request as background
  context only, not required for deep understanding.

** Module 4, Session 1 complete. **

Open items / next session:

* Session 2: Public-key cryptography, addresses.

Confused / needs reinforcement:

* None — reasoning throughout (avalanche effect prediction, Merkle
  tree level count, ripple-effect tracing) was correct on first attempt
  each time.



2026-08-13 (cont'd)
Covered:

* Session 5 — File I/O: `open()` and file modes — `"w"` (write, truncates
  existing contents — same risk as terminal `>` from Module 2), `"a"`
  (append), `"r"` (read). `.write()` requires strings and does NOT auto-add
  newlines (`\n` must be included manually, unlike `print()`).
* `with open(...) as file:` pattern — automatically closes the file on
  exit from the block, safer than manual `open()`/`.close()` since it
  still closes properly even if an error occurs mid-block. Confirmed
  understanding that writing to a file after its `with` block ends throws
  a `ValueError` (file object still exists as a variable, but is closed).
* `.read()` (whole file as one string, `\n` characters included literally)
  vs `.readlines()` (a list of strings, one per line). Practiced writing
  a two-line file, reading it back with `.readlines()`, looping through
  with `for i in lines:`, and using `.strip()` to clean trailing `\n`
  before printing — full write/read round trip completed successfully.
* API calls: conceptual link established between RPC (Module 5 preview)
  and general web API calls — both are request/response, just RPC is
  local (to `bitcoind`) and this was a remote HTTP call.
* JSON — recognized as structurally identical to Python dicts/lists,
  explaining why Session 4 directly prepares for this material.
* Installed `requests` via `pip3 install requests` (handled two benign
  warnings: PATH warning for helper scripts, pip version warning) and an
  `import requests` LibreSSL/OpenSSL compatibility warning from urllib3 —
  confirmed harmless for basic use.
* Distinguished one-time `pip3 install` (installs on the machine) from
  per-script `import` (loads into that specific running program) —
  articulated correctly and precisely on first attempt.
* Made a live GET request to GitHub's public API (`requests.get(...)`),
  checked `response.status_code` (200), and converted the response to a
  Python dictionary with `response.json()`.
* Looped through the response with `.items()` to inspect all keys/values;
  clarified the distinction between fixed dictionary methods (`.keys()`,
  `.values()`, `.items()` — fixed names, not renameable) vs. loop variable
  names (arbitrary, matched by position, not by name).
* Final independent exercise: pulled a specific field (`data["repository_url"]`)
  from the live API response and formatted it into a sentence with an
  f-string — combining dict access + f-strings + real API data correctly
  on the first attempt.

** Module 3 (Python fundamentals) — COMPLETE. All 5 sessions finished:
variables/strings/numbers, control flow, functions, lists/dictionaries,
file I/O + API/JSON. **

Open items / next session:

* Module 4 — to be scoped (see curriculum.md for original outline; may
  be reviewed/adjusted before starting given how Module 3 went).

Confused / needs reinforcement:

* One extra comma in `for a, b, in data.items():` — ran without error but
  flagged as non-standard syntax; corrected.




2026-08-13
Covered:

* Session 4 — Lists: creation (`[ ]`), indexing (positive and negative,
  e.g. `[-1]` for last item), `len()` and the `len()-1` last-index
  relationship, `.append()` vs index assignment (`list[i] = x`), and
  looping with `for item in list:`.
* Session 4 — Dictionaries: creation (`{ }` with `key: value` pairs),
  accessing values by key (`dict["key"]`), case-sensitivity of keys,
  `KeyError` vs a list's `IndexError`. Adding a new key vs overwriting
  an existing one via assignment — noted the key difference from lists
  (dict assignment to a new key never errors; list assignment to an
  out-of-range index does).
* Looping through a dictionary: keys-only (`for key in dict:`) vs
  keys+values together (`for key, value in dict.items():`).
* Combined structure: list of dictionaries (e.g. a list of transaction
  objects) — identified as the direct real-world shape of RPC/JSON data.
  Chained indexing + key access (`transactions[1]["confirmations"]`) to
  pull one field from one item in a list of dicts.
* Wrote a full realistic pattern independently: loop through a list of
  dicts, filter with an `if` on one field, print another field for
  matches only (`for tx in transactions: if tx["confirmations"] == 0:
  print(tx["txid"])`) — traced through manually pass-by-pass and
  predicted output correctly.
* Cleared up a wording mix-up: `return` is specific to function bodies,
  not a general term for "produce a value" — flagged and corrected when
  raised.

Module 3 (Python fundamentals) — Session 4 complete.

Open items / next session:

* Session 5: Reading/writing files, calling an API, working with JSON
  (final session of Module 3).

Confused / needs reinforcement:

* Minor syntax miss chaining list index + dict key
  (tried `transactions[1, "confirmations"]` instead of
  `transactions[1]["confirmations"]`) — corrected immediately once the
  two-step lookup was explained; no repeat of the mistake afterward.
* Requested a slower, more explicit pace for this session (defining each
  new concept before showing code, rather than introducing via example) —
  worked well and should carry forward into Session 5.


2026-08-12
Covered:

* Session 3 — Functions: `def`, parameters, calling a function, and the
  distinction between `print()` (display only) vs `return` (hands a value
  back to be used elsewhere).
* Wrote `classify_confirmations()` from scratch — refactored the earlier
  if/elif/else confirmation logic into a function returning a string.
  Self-corrected an indentation error under `elif` (unindented `return`)
  after being shown where to look.
* Calling a function and branching on its result: `status = my_func(...)`
  then `if status == "value":` — identified as the pattern that will map
  directly onto Module 5 (call RPC method → store JSON response → branch
  on its contents).
* Multiple parameters and default parameter values
  (`def f(x, y=0):`) — omitting an argument falls back to the default;
  supplying one overrides it.
* Positional argument matching — arguments are matched to parameters by
  order, not by inferred meaning. Discussed the silent-bug risk of
  swapped positional args (no error, just wrong values), and keyword
  arguments (`f(y=6, x="abc")`) as the fix, especially relevant once
  RPC calls have several parameters.

Module 3 (Python fundamentals) — Session 3 complete.

Open items / next session:

* Session 4: Lists and dictionaries.

Confused / needs reinforcement:

* None — one indentation slip under `elif`, self-corrected immediately
  once pointed out. No conceptual gaps; reasoning through return values
  and positional args was solid throughout.



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