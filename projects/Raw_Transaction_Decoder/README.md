# Bitcoin Raw Transaction Decoder

Decodes a raw Bitcoin transaction (hex) into its fields (version, inputs, outputs, witness data, and locktime) by parsing the bytes directly in Python, without relying on Bitcoin Core's decoder.

## Why this exists

I built this as part of a self-directed Bitcoin and software-development curriculum ([bitcoin-foundations](https://github.com/tide-blast/bitcoin-foundations)). The goal was to understand the transaction wire format at the byte level, not just call an API that decodes it for me. It also doubles as a small, readable reference for how a transaction is laid out.

The decoder makes no network calls and runs entirely on your machine. `decode_transaction()` takes a hex string and returns a dictionary, so it can be imported into other Python code.

## Features

- Parses legacy and SegWit (BIP141) transactions, including coinbase transactions
- Prints the version, each input (txid, vout, scriptSig, sequence), each output (value in satoshis, scriptPubKey), the witness stack for each input, and the locktime
- No third-party dependencies
- Includes a test suite checked against Bitcoin Core's own decoding

## Requirements

- Python 3 (developed and tested on 3.9.6)
- Nothing else to run the decoder: it uses only Python's standard library
- `pytest`, only if you want to run the tests
- Optional: Bitcoin Core (`bitcoin-cli`) with a running node, if you want to fetch transaction hex from your own node. The decoder works on hex from any source.

## Getting started

Nothing to install. Clone the repository (or copy `tx_decoder.py`):

```
git clone https://github.com/tide-blast/bitcoin-foundations
```

Then change into then `Raw_Transaction_Decoder` project folder:

```
cd Projects/Raw_Transaction_Decoder
```

## Usage

The decoder takes the raw transaction as a single command-line argument: a plain hex string with no `0x` prefix, as returned by `bitcoin-cli getrawtransaction <txid>` (without the verbose flag).

**Decode a hex string:**

```
python3 tx_decoder.py "<raw transaction hex>"
```

**Fetch hex from your own Bitcoin Core node and decode it in one step:**

```
python3 tx_decoder.py "$(bitcoin-cli -conf=<path to bitcoin.conf> -signet getrawtransaction <txid>)"
```

Notes on the node command:
- Remove `-signet` for mainnet, or use the flag for the network your node runs on.
- Looking up an arbitrary confirmed transaction needs `txindex=1` in `bitcoin.conf`.

**Compare against Bitcoin Core's own decoding:**

```
bitcoin-cli -conf=<path to bitcoin.conf> -signet getrawtransaction <txid> true
bitcoin-cli -conf=<path to bitcoin.conf> -signet decoderawtransaction "<raw transaction hex>"
```

The first works for transactions your node can look up. The second decodes any hex you give it.

**With no argument**, the program decodes a small built-in test transaction.

## Example

A legacy (non-SegWit) transaction from the Bitcoin developer documentation:

```
python3 tx_decoder.py "01000000017b1eabe0209b1fe794124575ef807057c77ada2138ae4fa8d6c4de0398a14f3f00000000494830450221008949f0cb400094ad2b5eb399d59d01c14d73d8fe6e96df1a7150deb388ab8935022079656090d7f6bac4c9a94e0aad311a4268e082a725f8aeae0573fb12ff866a5f01ffffffff01f0ca052a010000001976a914cbc20a7664f2f69e5355aa427045bc15e7c6c77288ac00000000"
```

Output:

```
Version: 1

Inputs:
  txid: 3f4fa19803dec4d6a84fae3821da7ac7577080ef75451294e71f9b20e0ab1e7b
  vout: 0
  scriptSig: 4830450221008949f0cb400094ad2b5eb399d59d01c14d73d8fe6e96df1a7150deb388ab8935022079656090d7f6bac4c9a94e0aad311a4268e082a725f8aeae0573fb12ff866a5f01
  sequence: 4294967295

Outputs:
  value (satoshis): 4999990000
  scriptPubKey: 76a914cbc20a7664f2f69e5355aa427045bc15e7c6c77288ac

Locktime: 0
```

For SegWit transactions, a `Witness:` section is printed between the outputs and the locktime, with one stack per input.

## How it works

A raw transaction is a flat sequence of bytes with no field names or delimiters. A parser knows where each field starts and ends only by position and length. The decoder keeps an `offset` into the hex string. Each parse function reads its field starting at `offset` and returns the value together with the new offset, which is passed to the next function.

Fields are read in this order:

1. Version (4 bytes)
2. SegWit marker and flag (2 bytes, only if present)
3. Input count
4. Inputs: previous txid, previous output index (vout), scriptSig, sequence
5. Output count
6. Outputs: value (8 bytes, in satoshis), scriptPubKey
7. Witness data: one stack of items per input (SegWit only)
8. Locktime (4 bytes)

Three details shape the code:

- **Variable-length integers.** Counts and script lengths use Bitcoin's compactSize encoding: one byte for values up to 252, or a marker byte (`fd`, `fe`, `ff`) followed by 2, 4, or 8 bytes.
- **Little-endian numbers.** Numeric fields are stored least-significant byte first, so the bytes are reversed before conversion.
- **Display conventions.** Previous txids are reversed to match how explorers and Bitcoin Core show them. Scripts and witness items are raw bytes and are printed as hex, unchanged.

For high-level details on how parsing occurs in the context of this program, read [EXPLAINER_Bitcoin_Transaction_Decoder.md](EXPLAINER_Bitcoin_Transaction_Decoder.md).

## Testing and verification

### Automated tests

`test_tx_decoder.py` contains 23 tests. Run them from the project folder:

```
python3 -m pip install pytest
python3 -m pytest -v
```

They cover:
- The helper functions and every compactSize branch (single byte, `fd`, `fe`, `ff`)
- Version and locktime parsing
- Hand-built legacy and SegWit transactions, including an empty witness stack and the error raised for an unexpected SegWit flag byte
- Five real transactions, each compared field by field with Core’s decoding: a SegWit P2WPKH spend, a two-input taproot spend, a coinbase transaction, a SegWit transaction with a P2WSH output, and a legacy P2PKH transaction. Four come from signet and one is the documentation example. A sixth, a large mainnet SegWit transaction (143 inputs, 11 outputs), is verified by recomputing its txid.

### Manual verification on mainnet

I also checked five real mainnet transactions by hand: three recent SegWit transactions (including one with 143 inputs and 11 outputs) and two legacy transactions. I fetched each transaction's raw hex from one API, decoded it with this program, and compared the result with the verbose JSON from a different API. Every field matched. These mainnet checks are not part of the automated test suite. Anyone wishing to audit these results is encouraged to use an API of his or her own choosing.

## Limitations

- **It decodes but does not validate.** It does not check signatures, scripts, or whether a transaction is valid, and it does not compute the txid.
- **Raw output.** Scripts are shown as hex, not disassembled. Amounts are in satoshis, not BTC. Locktime is shown as a raw number, without saying whether it means a block height or a timestamp.
- **Malformed input is not handled.** Truncated hex or non-hex characters crash with a Python error and no friendly message.
- **SegWit flag.** Only the standard flag byte `01` is accepted. Anything else raises a `ValueError`.
- **Hex must be supplied.** The program does not fetch a transaction by txid itself, and it reads hex only from the command line (not from stdin or a file).
- **Test coverage gaps.** No test has specifically targeted compactSize values of 253 or more on real data (the `fd`, `fe`, and `ff` branches are covered only by hand-built tests), or witness stacks with many items such as multisig and taproot script-path spends.

## License

Copyright (c) 2026 tide-blast

Released under the MIT License. See [LICENSE](../../LICENSE) for the full text.
