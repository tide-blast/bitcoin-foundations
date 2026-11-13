# Asking a Bitcoin Node Questions: How the Node Info Tool Works

A beginner-friendly introduction to talking to Bitcoin Core over RPC and turning its answers into a readable status report.

---

## 1. What This Program Does

A Bitcoin node is a program that keeps a copy of the blockchain, checks every new block and transaction against the rules, and talks to other nodes. It does a great deal, but it does not show much by default. To find out whether it is caught up, how many peers it has, or how busy the mempool is, you have to ask it.

This program queries a running node for its status. It connects to a Bitcoin Core node running on your own computer, makes three requests, and prints one report: the state of the chain, the state of the network connections, and the state of the mempool. If something goes wrong, such as the node not running or the login failing, it says so in one plain line instead of crashing.

The program was written as part of a self-directed Bitcoin and software-development curriculum ([bitcoin-foundations](https://github.com/tide-blast/bitcoin-foundations)). Its companion project, the Raw Transaction Decoder, reads Bitcoin's byte format by hand. This one works at a higher level: it uses an existing interface, combines several of its answers, and presents them for a person to read.

---

## 2. Talking to a Node: RPC over HTTP

Bitcoin Core can run a small web server that accepts commands. This is called its **RPC interface** (RPC stands for *remote procedure call*: asking another program to run a function and send back the result). The tool sends a message, the node runs the named command, and the node sends back a reply.

The message is a small piece of structured text (JSON) sent over HTTP, the same protocol browsers use. For example, to ask for the number of blocks the node has:

```json
{"jsonrpc": "1.0", "id": "node_info", "method": "getblockcount", "params": []}
```

Parts:<br>
`method`: The command to run<br>
`params`: The command's arguments, as a list (empty here, because this command takes none)<br>
`id`: A label chosen by the sender, which the node copies into its reply so the two can be matched<br>
`jsonrpc`: The protocol version the message uses<br>

The reply has three parts, whatever the command:

```json
{"result": 329509, "error": null, "id": "node_info"}
```

`result` holds the answer. `error` is `null` when all went well, and holds a code and a message when it did not. `id` is the label coming back.

**Where the message goes.** The address is `http://127.0.0.1:38332/`. `127.0.0.1` always means "this computer", and `38332` is the port a signet node listens on for RPC. The address is the default value of `url` in the tool's `rpc_call()` function. The same idea would work for a node on another machine, with only the address changed.

**What the program does *not* do.** It never opens the node's data files or reads the blockchain from disk. It asks the running node, and the node does all the work. That is why the tool needs only a login and an address, and not the path to the node's data directory.

---

## 3. Logging In: The Cookie File

A node's RPC interface can control a wallet and shut the node down, so it does not answer anyone who asks. Each request has to carry a username and password.

Bitcoin Core has a convenient way to provide them. When the node starts without an RPC password configured, it generates a random one, writes it to a file called `.cookie` in its data folder, and deletes the file when it shuts down. The file holds one line:

```
__cookie__:<a long random string>
```

The part before the first colon is the username. The part after it is the password. The tool's `read_cookie()` function opens the file, strips the trailing newline, and splits the line at the first colon (only the first, in case the password ever contained one). It returns the pair, which `requests` attaches to each message as an HTTP login.

Why this is better than a password written in the code:

- Nothing secret is in the program or in the repository.
- The password changes every time the node restarts, so an old one is useless.
- Only someone who can read files on the machine can get it.

The cookie's path is the one thing the user supplies on the command line:

```
python3 node_info.py <path to .cookie>
```

So the command line answers "how do I log in?" and the default address in the code answers "where is the node?".

---

## 4. Reading the Three Replies

Each command returns a large dictionary. Most of the fields describe things a status report does not need, so the program picks the few that answer a question a person would ask.

### Chain: `getblockchaininfo`

*Is my node on the right network, and is it caught up?*

| Field | What it is | How the report shows it |
|---|---|---|
| `chain` | The network (`signet` here) | Printed as-is |
| `blocks` | Blocks the node has fully validated | "Validated blocks" |
| `headers` | Block headers the node knows about | Used to compute "Blocks remaining" (`headers - blocks`) |
| `difficulty` | A measure of how hard it is to produce a valid block | Printed to four decimals |
| `time` | The timestamp inside the newest block | Shown as an age in whole minutes |
| `verificationprogress` | The node's own estimate of how much of the chain it has verified, from 0 to 1 | Multiplied by 100 and shown as a percentage |

Two details matter when reading these numbers:

- **"Blocks remaining" is the exact signal, and the percentage is not.** The percentage is rounded to two decimals, so a node a few blocks behind can still show 100.00%. The subtraction cannot hide anything. On a small network like signet this rarely matters. On a larger one it would.
- **"Latest block" is an approximation.** The timestamp in a block is set by the miner who produced it, not by your node, and the age is measured against your computer's own clock. It is a useful sign that blocks are arriving, not a precise measurement.

### Network: `getnetworkinfo`

*Is the node connected, and to how many peers?*

- `subversion` is the software the node reports itself as (for example `/Satoshi:31.1.0/`).
- `networkactive` says whether peer-to-peer networking is switched on, shown as Yes or No.
- `connections`, `connections_in` and `connections_out` are the total number of peers, and how many started the connection to you (in) versus how many you started (out). A home node often has zero inbound connections, because other nodes usually cannot reach it, and that does not mean anything is wrong.
- `timeoffset` is the node's reported time offset in seconds. Bitcoin Core's documentation describes it only as "the time offset", so the report shows the number and does not interpret it. A value near zero is normal.

### Mempool: `getmempoolinfo`

*How much is waiting to be confirmed?*

The **mempool** is the set of valid transactions a node has received that are not yet in a block.

- `size` is the number of transactions waiting.
- `bytes` is their combined **virtual size**, a measure that takes SegWit's discount for witness data into account. The report shows it in kilobytes.
- `total_fee` is the sum of the fees those transactions offer, in BTC. It is printed with eight decimal places (the smallest unit is one hundred-millionth of a bitcoin). Without that, Python prints very small numbers in scientific notation, such as `4e-05`, which is hard to read in a report.

A quiet network like signet has a small mempool, sometimes only a few transactions.

---

## 5. When Things Go Wrong

Four things can fail in a predictable way, and each gets a plain message:

| What happened | How the program notices | What the user sees |
|---|---|---|
| The cookie file is not where the user said. | Python raises `FileNotFoundError` when opening it. | `Cookie file not found: <path>` |
| The node is not running, or the port is wrong. | `requests` raises a `ConnectionError`. | `Could not connect to the node at 127.0.0.1:38332. Is bitcoind running?` |
| The login is wrong or out of date. | The node replies with HTTP status 401. | `Authentication failed` |
| The node understood the request but refused it. | The reply's `error` field is not `null`. | `Node returned an error: <message> (code <number>)` |

The last two need explicit checks. An HTTP status code is a number attached to every web reply: "200" means "success" and "401" means "unauthorized". The program checks the number before reading the body, because a failed login does not come with a normal reply. A refused command seems more unusual because it arrives as a perfectly valid reply with the `error` field filled in. No Python exception happens, so a program that forgot to look would carry on with an empty result and fail later, somewhere confusing.

**Who prints the message?** `rpc_call()` does not print anything. When it detects a problem, it *raises* an error, and the error travels up to `main()`, which decides what to show and then exits. Keeping the printing in one place means the rest of the code can stay focused on its own job.

**All three requests are made before anything is printed.** If the node stopped between the first and third request, the user would otherwise see half a report followed by an error. Fetching everything first means the output is either a full report or a single error line.

---

## 6. Keeping Fetching and Formatting Apart

The program has two kinds of functions:

- **Functions that talk to the world:** `read_cookie()` reads a file, and `rpc_call()` sends a request.
- **Functions that only transform data:** `format_chain_section()`, `format_network_section()` and `format_mempool_section()` each take a dictionary and return text. They make no network calls, read no files, and print nothing.

The second kind is much easier to check because you can pass it a hand-written dictionary and compare the result with the expected text.

One formatter needed a small extra step. The "latest block" line depends on the current time, so its output changes every second. The function therefore takes an optional `now` argument. It defaults to the real time, and a test can pass a fixed value, such as exactly ten minutes after the block's timestamp, and get the same answer every time.

---

## 7. Testing Without a Node

The tests need Python, `requests` and `pytest`, but no running node. The formatters are checked as described above, and `read_cookie()` is checked against a temporary file the test creates.

Testing `rpc_call()` and `main()` needs a different technique, because they normally contact a node. The tests replace the real network call with a **fake** that returns a reply the test chooses: a 401, an error message, or a normal answer. The real code then runs against the fake reply, so the error paths can be checked without breaking a real login or stopping a real node. The fake only exists for the length of one test.

---

## 8. Putting It Together

1. The user runs `python3 node_info.py <path to .cookie>`.
2. `read_cookie()` reads the file and returns the username and password.
3. `rpc_call()` is called three times (`getblockchaininfo`, `getnetworkinfo`, `getmempoolinfo`), each sending a request to `127.0.0.1:38332` with the login attached.
4. If any step fails, a single error line is printed and the program exits.
5. Otherwise each reply goes to its formatting function, and the three sections are printed.

**What this version does not do.** It works against a signet node at a fixed address, and it logs in with a cookie only. Supporting another network, or a node that uses a configured password, would mean making the address and the login settable by the user. That change would be small, but the current version leaves it out on purpose.
