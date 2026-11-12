# Bitcoin Node Info Tool

A command-line script that makes several RPC calls to a local Bitcoin Core node and prints one readable status report: chain and sync state, network connections, and mempool size.

## Why this exists

Built as part of a self-directed Bitcoin and software-development curriculum ([bitcoin-foundations](https://github.com/tide-blast/bitcoin-foundations)). Its companion project, the [Raw Transaction Decoder](../Raw_Transaction_Decoder), parses the wire format by hand. This one does the opposite: it builds something useful out of an existing API by chaining node RPC calls, handling the JSON they return, and formatting live data for a person to read.

It also covers mundane parts of working with an API: authenticating without hardcoding secrets, and turning failures (node down, wrong credentials, rejected command) into short, plain messages instead of tracebacks.

The test suite was written by an LLM and reviewed by me.

## Features

- Reports on a running node with three RPC calls: `getblockchaininfo`, `getnetworkinfo`, `getmempoolinfo`
- **Chain:** network name, validated blocks, blocks remaining to validate, difficulty, age of the latest block, sync progress
- **Network:** node software version, whether networking is active, connection count with the inbound/outbound split, clock offset
- **Mempool:** number of waiting transactions, their total virtual size, and total fees
- Authenticates with Bitcoin Core's cookie file, so no password is stored in the code or in the repository
- Fetches all three results before printing anything, so a failure never produces a half report
- Clear one-line messages for a missing cookie file, an unreachable node, bad credentials, and a node-side error
- Tests that run without a node

## Requirements

- Python (developed on 3.9.6)
- The `requests` library (`pip install requests`)
- `pytest`, only if you want to run the tests
- Bitcoin Core running on **signet**, with RPC reachable at `127.0.0.1:38332` (developed against v31.1)
- Cookie authentication (see [Node setup](#node-setup))

## Getting started

Clone the repository and change into the project folder:

```
git clone https://github.com/tide-blast/bitcoin-foundations
cd bitcoin-foundations/projects/Node_Info_Tool
```

Install the one dependency, the `requests` library:

```
python3 -m pip install requests
```

If `pip` is available directly on your system, `pip install requests` does the same thing.

### Node setup

The tool logs in with the `.cookie` file that Bitcoin Core writes while it is running, so it never needs a password you chose.

- - Core generates the cookie when no `rpcpassword` is set. If your `bitcoin.conf` sets `rpcuser` and `rpcpassword`, comment out those lines and restart the node. In the author's setup the cookie file appeared after those lines were commented out. Behavior with `rpcauth` may depend on the Core version; if no `.cookie` appears, check `bitcoin.conf` for it.
- The file is in the network's subfolder of the node's data directory. For signet that is `<data directory>/signet/.cookie`.
- Core deletes the cookie when it shuts down and writes a new one on the next start. The tool reads it fresh on every run, so this does not matter.
- Never commit a cookie file or a `bitcoin.conf` containing credentials.

## Usage

Pass the path to the cookie file as the only argument:

```
python3 node_info.py <path to .cookie>
```

For example:

```
python3 node_info.py /path/to/data-directory/signet/.cookie
```

With no argument, the tool prints a usage line and exits.

The node address is fixed at `http://127.0.0.1:38332/`, the default signet RPC address. It is the default value of `url` in `rpc_call()` in `node_info.py` if you need to change it.

## Example

Output from the author's signet node:

```
CHAIN INFO:
Chain:              signet
Validated blocks:   330349
Blocks remaining:   0
Difficulty:         0.0481
Latest block:       0 minutes ago
Sync progress:      100.00%

NETWORK INFO:
Node software:      /Satoshi:31.1.0/
Network active:     Yes
Connections:        10 (0 in, 10 out)
Clock offset:       0 s

MEMPOOL INFO:
Transactions:       3
Virtual size:       0.9 kB
Total fees:         0.00003718 BTC
```

## How it works

1. `main()` reads the cookie path from the command line and calls `read_cookie()`, which returns the `(username, password)` pair stored in the file (`__cookie__` and a random token).
2. `rpc_call()` sends each request to the node as a JSON-RPC message over HTTP, using those credentials. It returns the parsed reply, and raises an error if the node answers with HTTP 401 (bad credentials) or with an error in the reply.
3. Three calls are made: `getblockchaininfo`, `getnetworkinfo` and `getmempoolinfo`.
4. Each reply goes to a formatting function (`format_chain_section`, `format_network_section`, `format_mempool_section`). These make no network calls: each takes a dictionary and returns text, which is what makes them easy to test.

Two details worth knowing:

- **Blocks remaining** is the number of known block headers minus the number of validated blocks. It is 0 when the node is caught up.
- **Latest block** is the age of the newest block's timestamp compared with your computer's clock. The timestamp is set by the miner, so it is approximate, and a wrong local clock makes the age wrong.

For a longer walkthrough of the concepts behind the tool, read [EXPLAINER_Bitcoin_Node_Info_Tool.md](EXPLAINER_Bitcoin_Node_Info_Tool.md).

## Testing

The tests need no running node:

```
pip install pytest
python3 -m pytest -v
```

They cover the three formatting functions, `read_cookie()` (using a temporary file), `rpc_call()` (with a faked HTTP call) and `main()` (with a faked command line and node). Between them they check the exact report text, the edge cases found while building (whole-minute ages, 8-decimal fees instead of scientific notation) and every error path.

## Known limitations

- Signet only. The address and port are fixed in the code. Formatting was spot-checked against mainnet-sized values, but the tool has not been run against a mainnet node.
- Cookie authentication only. There is no option for `rpcuser`/`rpcpassword`.
- The report is fixed. There are no options to choose sections or output formats.
- A reply from the node that is not valid JSON is not handled specially.
- Per-peer details (`getpeerinfo`) are deliberately not included.

## Troubleshooting

| Message or symptom | Likely cause |
|---|---|
| `Usage: python3 node_info.py <cookie file path>` | No path was given |
| `Cookie file not found: <path>` | Wrong path, or the node is not running (Core deletes the cookie on shutdown). Also check that no RPC password is set in `bitcoin.conf`. |
| `Could not connect to the node at 127.0.0.1:38332. Is bitcoind running?` | The node is stopped, still starting up, or listening on a different port |
| `Authentication failed` | The cookie file is out of date (for example, from before a node restart) or belongs to another node |
| `Node returned an error: ... (code ...)` | The node rejected the request. The message and code come straight from Bitcoin Core. |
| A `NotOpenSSLWarning` from `urllib3` on start-up | Harmless here. macOS's bundled Python uses LibreSSL, and this tool talks to `127.0.0.1` over plain HTTP, so no SSL is involved. |

## License

Copyright (c) 2026 [tide-blast](https://github.com/tide-blast)

Released under the MIT License. See [LICENSE](../../LICENSE) for the full text.