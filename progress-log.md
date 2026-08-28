# Progress Log — Bitcoin Foundations

Running log of study sessions. Newest entries at the top. Used both as a personal
journal and as a handoff reference when starting a new chat session with an AI
assistant — paste the most recent entry (or last few) at the start of a new chat
for continuity.

---


2026-08-28
Covered:

* Module 5 — Bitcoin Core + RPC hands-on, continued. Confirmed signet
  node fully synced (319,701+ blocks, verificationprogress: 1). Noted
  infrastructure change: datadir relocated from external SSD to internal
  drive due to repeated external-drive disconnects during sync;
  bitcoin.conf itself remains on the external drive, with datadir
  pointing inward — correctly reasoned that config location and data
  location don't need to match.
* Walked the getblockhash -> getblock -> getrawtransaction chain by hand
  via bitcoin-cli. Correctly predicted header contents (nonce, prev
  hash, Merkle root, difficulty) before running commands. Initial
  reasoning on the getblockhash/getblock split proposed height as
  something getblock independently derives; corrected — height isn't
  stored in the header at all, it's a locally-maintained index
  (hash -> height) separate from the hash-addressed block data itself.
* Asked a strong clarifying question on chainwork ("compute cycles?"),
  correctly redirected — chainwork tallies *expected* hash attempts
  derived from each block's difficulty target, not actual work
  performed. Follow-up question (whether mainnet's chainwork would
  overflow 256 bits soon) reasoned through with order-of-magnitude
  math — confirmed no realistic overflow risk (~47 orders of magnitude
  of headroom remaining).
* Pulled block 1 (single-tx block) and correctly predicted the
  Merkle-root duplication rule would apply; self-corrected on follow-up
  when the actual result (root == sole txid, no duplication) didn't
  match — recognized that duplication only applies when reducing a
  multi-element odd-length level, not a single-leaf case.
* Pulled block 319,700 (212 transactions) and a real non-coinbase
  transaction. Encountered a Taproot script-path spend (complex witness
  stack) — flagged as a future topic and deliberately not pursued in
  depth. Re-pulled a second, simpler transaction to isolate a clean
  P2WPKH key-path spend: mapped scriptSig (empty, SegWit) vs.
  txinwitness (sig + pubkey), an OP_RETURN data-carrier output (correctly
  asked whether this is spender-set and how — confirmed: spender's
  choice at construction time, zero value, not added to the UTXO set),
  and a real payment output.
* Initially assumed transactions were self-contained and that a
  referenced prior transaction must belong to the same wallet —
  corrected: every non-coinbase transaction must reference a prior
  UTXO as input, and that prior output was near-certainly created by
  an unrelated sender; only ability to unlock it (via signature) matters,
  not who created it.
* Enabled txindex=1 and ran a full reindex (same-session completion) to
  resolve a "No such mempool transaction" error, after correctly
  identifying that a plain txid lookup requires either an indexed node
  or an explicit block hash. Used the new index to trace a transaction's
  input back to its parent transaction and complete a real fee
  calculation by hand (fee = input value - total output value),
  discovering a 2-input, 3-output UTXO consolidation transaction in the
  process.
* Correctly pushed back on an unclear question (vin's vout index vs.
  this transaction's own vout list) — flagged confusion rather than
  guessing, leading to a needed clarification that these are two
  unrelated numbering systems sharing a field name.
* Bridged into Module 5's Python/RPC component. Asked a foundational
  question on why a local-only call needs an IP address at all —
  correctly reasoned toward the idea that ports serve as network
  input/output interfaces, refined into the full model: single unified
  networking stack regardless of destination, with 127.0.0.1 as a
  reserved loopback address using identical IP-based machinery to
  internet traffic, just short-circuited before leaving the machine.
  Verified rpcport/rpcbind/rpcallowip were all unset in bitcoin.conf,
  confirming signet's default (127.0.0.1:38332) by elimination rather
  than assumption.
* Wrote and successfully ran first raw JSON-RPC call from Python via
  requests.post() (getblockchaininfo), with HTTP Basic Auth. Correctly
  predicted the response would contain recognizable blockchain fields;
  refined to the precise structural point — JSON-RPC wraps responses in
  a result/error/id envelope, distinct from bitcoin-cli's flattened
  display of the same underlying data. Requested and received a full
  line-by-line explanation of the request script before running it.

** Module 5 (Bitcoin Core + RPC) — IN PROGRESS. bitcoin-cli exploration
solid; Python/JSON-RPC layer just begun. **

Open items / next session:

* Resume by sketching a rpc_call(method, params) function signature
  before seeing the implementation (question intentionally left open
  at session end).
* Generalize the raw JSON-RPC pattern into a reusable Python function.
* Reimplement getblockhash / getblock / getrawtransaction in Python
  instead of bitcoin-cli.
* Eventually feeds into Module 6 Project 2 (RPC-based node info tool).

Confused / needs reinforcement:

* None of real substance. A few initial mismatches this session
  (Merkle-root duplication on a single-leaf block, assuming referenced
  transactions share a wallet, conflating vin's vout index with the
  transaction's own vout list) were self-caught or quickly corrected
  through discussion — pattern of strong first-principles reasoning
  from Module 4 continues to hold under more complex, real-world data.


2026-08-26
Covered:

* Session 5 — The P2P network (conceptual): defined a node's three core
  jobs (store, validate, relay) and established that trust is placed
  entirely in shared validation rules, not in any node's identity or
  authority — no central coordinator.
* Correctly reasoned that invalid data (bad signature, bad proof-of-
  work) fails to propagate through the network. Initial answer proposed
  a shared "blacklist" mechanism — corrected: rejected data is simply
  dropped silently and never relayed; every node re-validates
  independently using the same rules, so there's no need for a
  coordinated blacklist. Noted the one real (but local, non-shared)
  exception: individual nodes may disconnect from consistently
  misbehaving peers.
* Worked through a double-spend scenario in detail: correctly
  identified that both conflicting transactions could be individually
  valid (signature-wise), and correctly predicted eventual resolution
  via block inclusion. Refined with the precise mechanism: mempool-
  level detection (a node rejects a second transaction referencing an
  already-seen UTXO), with final resolution occurring once one version
  is actually mined into a block — the losing version is then dropped
  network-wide since its UTXO is now provably already spent.
* Worked through a temporary-fork scenario (two valid blocks found
  near-simultaneously): correctly predicted that whichever side extends
  first "wins" and that the network converges onto the longer/more
  current chain at an accelerating rate. Refined terminology to the
  precise rule (most cumulative proof-of-work, not simply "longest"),
  and added the economic mechanism driving the acceleration: miners are
  incentivized to abandon a losing chain immediately, since continuing
  to mine on it risks an unspendable reward once abandoned (orphaned/
  stale block) — this is what drives the winning chain's lead to
  compound quickly.
* Correctly distinguished orphaned blocks' fate: coinbase reward
  evaporates entirely for that miner, while ordinary (non-coinbase)
  transactions from the orphaned block return to the mempool and are
  eligible for inclusion in a future block.

** Module 4, Session 5 complete. MODULE 4 (Bitcoin Protocol Theory) — FULLY COMPLETE. **

Open items / next session:

* Scope Module 5 (Bitcoin Core + RPC, hands-on) — install Bitcoin Core,
  choose signet as the target network (recommended over testnet3/4 for
  size and predictability, per earlier discussion), run via bitcoin-cli
  / JSON-RPC, explore real blocks and transactions via Python.

Confused / needs reinforcement:

* None of real substance. Initial answers throughout this session
  (blacklist mechanism, "consensus conflict" phrasing for double-spend,
  "longest chain" phrasing for forks) were directionally correct on
  first attempt and refined to precise mechanisms through discussion —
  strong conceptual grasp of P2P consensus by the end of the session.


2026-08-20
Covered:

* Session 4 — Block structure, proof-of-work: block anatomy (header +
  transaction list) — header contains previous block hash, Merkle root,
  timestamp, difficulty target, and nonce, and stays small/fixed size
  regardless of transaction count. Correctly reasoned why including only
  the previous block's hash is sufficient to "lock in" that entire prior
  block's contents (ties directly to Session 1 hashing properties).
* Correctly reasoned through the chain-tampering ripple effect: initially
  answered "50 blocks" for a tampered block 100 in a chain at height 150,
  self-corrected to the precise answer (51 — the tampered block itself
  plus the 50 that follow) once walked through carefully.
* Built a full sample block in Python: transactions list + header,
  computing a real Merkle root from 3 transactions using the Session 1
  method (including odd-count duplication, since 3 is odd).
* Proof-of-work mechanics: difficulty target as a numeric ceiling a
  header hash must fall below; nonce as the only "free variable" miners
  can change per attempt. Correctly reasoned that no pattern or shortcut
  exists between nonce attempts (avalanche effect implication) — floated
  "rainbow tables" as a possible shortcut, which was corrected: rainbow
  tables reverse a specific known hash, which doesn't apply to mining's
  "find any hash below a threshold" search.
* Ran a real mining simulation in Python (4-leading-zero target, easy
  difficulty for demo purposes) — found a valid nonce after 66,951 brute-
  force attempts, confirming no shortcuts exist in practice.
* Correctly reasoned through why tampering with an old block is
  infeasible beyond "expensive": framed it as a race against a
  continuously-growing honest chain, and correctly invoked the 51%/
  cumulative-hashpower consensus rule connecting back to proof-of-work.
* Difficulty defined precisely as a ratio against the difficulty-1
  baseline target (not a literal "count the zeros" metric) — clarified
  that leading zeros are a rough visual proxy for a shrinking numeric
  target, not the actual mechanism the protocol tracks.
* Pulled and examined two real blocks via Blockstream's public API:
  the Genesis Block (block 0 — 1 transaction, null previous_block_hash,
  nonce 2083236893, embedded newspaper headline) and Block 100,000
  (Dec 2010 — 4 transactions, difficulty 14,484, 0 BTC in fees).
* Coinbase transaction deep dive: examined the real coinbase tx from
  Block 100,000 — no real "vin" (just an arbitrary "coinbase" data
  field, no signature needed), single output creating 50 BTC from
  nothing. Noted real output used a raw public key (P2PK), not a hashed
  address — a live historical artifact of the pre-P2PKH era, directly
  reinforcing Session 2/3 material on address hashing. Also examined a
  normal (non-coinbase) transaction from the same block, mapping
  prev_tx_id/output_index/signature/public_key onto real vin/vout/
  scriptSig/scriptPubKey fields.
* Coinbase field size limit: confirmed via search — 100 bytes max
  (4-byte minimum, holding block height per BIP34). Discussed real use
  of remaining space as "extra nonce" for mining (since the header's own
  4-byte nonce field is exhausted almost instantly by modern ASICs),
  directly extending the Session 4 mining-search discussion.
* OP_RETURN outputs: explained as a script opcode marking an output
  provably unspendable, existing specifically so nodes don't have to
  carry fake "spendable" outputs in the UTXO set forever just to store
  arbitrary data. Covered current, real controversy: Bitcoin Core v30
  (Oct 2025) raised the default relay limit from ~80 bytes to 100,000
  bytes (policy-level, not consensus) — discussed the active Core vs.
  Knots debate and the real concern (illicit material permanently
  embedded on-chain) at a high level, without specifics.
* Asked a sharp follow-up on why "cumulative work" rather than "block
  count" is the consensus tie-breaker (hypothesizing a mid-fork
  difficulty drop scenario) — corrected: both forks share the same
  difficulty at the fork point (recalculated network-wide only every
  2,016 blocks), so the real reason for "cumulative work" is precision
  across long forks spanning a difficulty adjustment boundary, not a
  live short-fork threat. Distinguished this from real, separate
  difficulty-timing manipulation attacks (largely theoretical for
  Bitcoin given capped ±25%-ish adjustment size).
* Follow-up research: confirmed real historical multi-adjustment
  downward difficulty streaks (2011; and 2021's 4-in-a-row streak
  during the China mining ban, including the largest single drop ever
  at ~28%) and current 2026 data (10 downward vs. 7 upward adjustments
  YTD) — good real-world grounding for difficulty adjustment limits and
  behavior around halvings.

** Module 4, Session 4 complete. **

Open items / next session:

* Session 5: The P2P network (conceptual) — completed in the same
  session as Session 4 (see below).

Confused / needs reinforcement:

* Minor initial miscount on the block-tampering ripple effect (50 vs.
  51) — self-corrected immediately once walked through step by step.
  No other gaps; strong session with several sharp tangents pursued
  and resolved (rainbow tables, coinbase size limit, OP_RETURN,
  cumulative-work vs. block-count reasoning).


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