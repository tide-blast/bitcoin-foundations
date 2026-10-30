# Decoding Bitcoin Transactions from Raw Bytes

A beginner-friendly introduction to how Bitcoin transaction decoders work.

---

## 1. What This Program Does

Bitcoin transactions travel across the network as raw bytes and shown by tools such as explorers and this decoder as strings of hexadecimal characters. To a human reader, this hex looks like meaningless noise. This program takes that raw hex and extracts human-readable information: how many bitcoins changed hands, where they went, and who authorized the transfer. The decoder does not validate whether the transaction is legal or properly signed — it simply translates bytes into fields that software can reason about.

The program was written as part of a self-directed Bitcoin and software-development curriculum ([bitcoin-foundations](https://github.com/tide-blast/bitcoin-foundations)). The goal was to understand the transaction wire format at the byte level, not just call an API that decodes it for me. It also doubles as a small, readable reference for how a transaction is laid out.

---

## 2. Bytes Without Labels

At the protocol level, Bitcoin does not transmit structured data with field names like `{"version": 2, "inputs": [...]}`. Instead, everything is serialized as a contiguous byte stream. A decoder must know the precise order and size of each field to interpret the bytes correctly.

Consider this 259-byte legacy transaction from the Bitcoin mainnet:

```
0100000001032e38e9c0a84c6046d687d10556dcacc41d275ec55fc00779ac88fdf357a187000000008c493046022100c352d3dd993a981beba4a63ad15c209275ca9470abfcd57da93b58e4eb5dce82022100840792bc1f456062819f15d33ee7055cf7b5ee1af1ebcc6028d9cdb1c3af7748014104f46db5e9d61a9dc27b8d64ad23e7383a4e6ca164593c2527c038c0857eb67ee8e825dca65046b82c9331586c82e0fd1f633f25f87c161bc6f8a630121df2b3d3ffffffff0200e32321000000001976a914c398efa9c392ba6013c5e04ee729755ef7f58b3288ac000fe208010000001976a914948c765a6914d43f2a7ac177da2c2f6b52de3d7c88ac00000000
```

Without a specification, there is no way to know which bytes represent the transaction version, which represent the sender, or which represent the amount. The decoder encodes the specification as code: it knows that bytes 0–3 are the version, byte 4 is the input count, bytes 5–36 are the first input's previous transaction ID, and so on.

Think of it like reading a book in an unknown alphabet. The letters themselves are meaningless until you learn the grammar and word boundaries.

---

## 3. The Layout Blueprint

Every Bitcoin transaction follows the same structural template:

| Field | Size | Purpose |
|---|---|---|
| Version | 4 bytes | Protocol rules the transaction follows |
| Input count | Variable | How many previous outputs are being spent |
| Inputs | Variable | References to funds being transferred |
| Output count | Variable | How many addresses receive funds |
| Outputs | Variable | Destination addresses and amounts |
| Locktime | 4 bytes | Earliest time the transaction can be confirmed |

For legacy transactions without SegWit data, these fields appear consecutively with no padding or separators. Our 259-byte example breaks down like this:

```
Position   Hex                  Meaning
─────────────────────────────────────────────
0–3        01000000             Version 1
4          01                   One input
5–36       032e38e9...57a187    Previous txid (stored in this order but displayed byte-reversed)
37–40      00000000             Previous output index (vout = 0)
41         8c                   ScriptSig length (140 bytes)
42–181     493046...b3d3        ScriptSig (signature + public key)
182–185    ffffffff             Sequence (final, no locktime)
186        02                   Two outputs
187–194    00e3232100000000     Output 1 value (556,000,000 satoshis)
195        19                   Output 1 scriptPubKey length (25 bytes)
196–220    76a914...88ac        Output 1 scriptPubKey (P2PKH)
221–228    000fe20801000000     Output 2 value (4,444,000,000 satoshis)
229        19                   Output 2 scriptPubKey length (25 bytes)
230–254    76a914...88ac        Output 2 scriptPubKey (P2PKH)
255–258    00000000             Locktime (0 = immediate)
```

This blueprint explains the majority of transaction structure. Two complications arise: variable-length integers and byte ordering.

---

## 4. CompactSize Encoding

Most integer fields in Bitcoin are fixed-size: versions are always 4 bytes, locktime is always 4 bytes. But counts — number of inputs, number of outputs, script lengths — vary wildly. A transaction might have 1 input or 1,000 inputs. Storing a 4-byte integer for every count wastes space for small values.

Bitcoin uses **CompactSize** encoding to solve this. The rules are:

- If the count is **0 to 252**, encode it as a single byte.
- If the count is **253 to 65,535**, prefix with `0xfd` followed by 2 bytes (little-endian).
- If the count is **65,536 to 4,294,967,295**, prefix with `0xfe` followed by 4 bytes.
- Larger counts use `0xff` followed by 8 bytes.

In our example transaction:
- The input count at position 4 is `01` — a single byte representing the value 1.
- The scriptSig length at position 41 is `8c`, which is decimal 140 bytes.
- The output count at position 186 is `02` — a single byte representing two outputs.

All three fall in the single-byte range. Contrast this with the massive transaction used for testing in this project: tx 84a907af has 143 inputs. That's `0x8f` in hex, still fitting in one byte. Only when counts exceed 252 does CompactSize expand.

Why does this matter? The decoder must examine the first byte of any count field before deciding how many additional bytes to read. A single misplaced CompactSize interpretation shifts every subsequent field, corrupting the entire parse.

---

## 5. Little-Endian Byte Order

Computers store multi-byte integers in memory using a chosen byte order. Intel/AMD CPUs use **little-endian**, meaning the least-significant byte comes first. Bitcoin adopts this convention for all multi-byte numeric fields.

Human convention reads numbers with the most-significant digit on the left: "926" is nine hundred twenty-six instead of six hundred twenty-nine. Computers don't share this intuition when using little-endian and will reverse the byte order. The byte sequence `00 e3 23 21 00 00 00 00` represents a 64-bit integer. Reading left-to-right gives a huge number using human conventions. Computers will store and read it right-to-left for the correct value.

Decoded as little-endian:

```
Bytes:     00 e3 23 21 00 00 00 00
Reversed:  00 00 00 00 21 23 e3 00
Value:     556,000,000 satoshis ≈ 5.56 BTC
```

The second output follows the same pattern:

```
Bytes:     00 0f e2 08 01 00 00 00
Reversed:  00 00 00 01 08 e2 0f 00
Value:     4,444,000,000 satoshis ≈ 44.44 BTC
```

This reversal affects:
- Version numbers
- Transaction IDs (txid) — displayed byte-reversed when shown in block explorers
- Output amounts (64-bit unsigned integers)
- Sequence numbers and locktime

Our example shows version `01000000`. Reversed, that's `00000001`, which equals 1. Locktime at the end is `00000000`, reversing to 0, meaning the transaction can be confirmed immediately.

A common mistake for beginners is to read these bytes left-to-right as if they were big-endian. The resulting values will be astronomically wrong.

---

## 6. SegWit and Witness Data

The original Bitcoin transaction format bundled authorization data (signatures) into the `scriptSig` field. In 2017, Segregated Witness (SegWit) moved that data to a new structure called the **witness**, placed after the outputs.

This separation solved two problems. First, it prevented transaction malleability — a bug where third parties could alter unconfirmed transactions. Second, it reduced fees because witness bytes count less toward the block size ("weight") limit.

A SegWit transaction looks structurally different:

```
Version
Marker byte (0x00)
Flag byte (non-zero but "0x01" in practice; this decoder only accepts this value)
Input count
Inputs
Output count
Outputs
Witness data (for each input, including empty stacks)
Locktime (earliest time or block height)
```

Notice the marker and flag bytes inserted between version and input count. Without detecting these two bytes, a decoder would misinterpret the marker as input count.

Each input has its own witness stack. A stack starts with a count of its items, followed by each item as a length and that many bytes of data. An input with no witness items is just a single ```00``` byte, a count of zero.

A typical SegWit P2WPKH witness contains exactly two items:

1. A DER-encoded signature plus a sighash byte
2. A compressed public key

Our example transaction is **pre-SegWit**, so it contains no marker, flag, or witness section. This simplicity makes it ideal for learning the basics. The decoder in this project also handles SegWit transactions, but they follow a different branch of logic.

---

## 7. Putting It Together

The decoding process is deterministic and reversible. Given the same raw hex, the decoder will produce the same output every time. The challenge is not mathematical difficulty — it's precision. A single off-by-one error in offset tracking, a misread CompactSize prefix, or a forgotten byte reversal will propagate through every subsequent field.

This is why transaction decoders serve as excellent exercises in systems programming. They demand:
- Careful attention to byte-level detail.
- Careful handling of malformed input (which this decoder does not yet do).
- Familiarity with consensus rules that have evolved since 2009.

Understanding how bytes translate into fields demystifies the blockchain. What once looked like indecipherable gibberish becomes a structured ledger of transfers.

---

*Written for beginners exploring Bitcoin protocol work. The mainnet transaction example is txid fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4.*
