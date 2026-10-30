# Unit tests for tx_decoder.py
#
# Run from the folder that contains tx_decoder.py and this file:
#     python3 -m pytest -v
#
# Each test calls part of the decoder on an input whose correct answer is
# already known, then uses `assert` to check the decoder returns that answer.
# For the real transactions, the "known answer" is what Bitcoin Core itself
# decoded (getrawtransaction <txid> true, or decoderawtransaction for the
# legacy example).

import hashlib
from pathlib import Path

import pytest

from tx_decoder import (
    hex_to_value_LEndian,
    reverse_hex_bytes,
    parse_compactsize,
    parse_version,
    parse_locktime,
    decode_transaction,
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def test_little_endian_version_example():
    # "02000000" reversed by bytes is "00000002", which is 2
    assert hex_to_value_LEndian("02000000") == 2


def test_little_endian_locktime_example():
    # worked by hand in Module 6: c93c0e00 -> 933065
    assert hex_to_value_LEndian("c93c0e00") == 933065


def test_little_endian_two_bytes():
    # "1001" -> bytes 10 01 -> reversed 01 10 -> 0x0110 -> 272
    assert hex_to_value_LEndian("1001") == 272


def test_reverse_hex_bytes_reverses_byte_pairs_not_characters():
    # a character-level reversal would give "ddccbbaa" only by accident;
    # this input shows the pairs stay intact
    assert reverse_hex_bytes("aabbccdd") == "ddccbbaa"
    assert reverse_hex_bytes("1001") == "0110"


# ---------------------------------------------------------------------------
# parse_compactsize: each branch, plus a non-zero starting offset
# ---------------------------------------------------------------------------

def test_compactsize_single_byte():
    assert parse_compactsize("03", 0) == (3, 2)


def test_compactsize_upper_edge_of_single_byte():
    # 0xfc = 252 is the largest value that is its own count
    assert parse_compactsize("fc", 0) == (252, 2)


def test_compactsize_fd_branch():
    assert parse_compactsize("fd1001", 0) == (272, 6)


def test_compactsize_fe_branch():
    assert parse_compactsize("fe10010000", 0) == (272, 10)


def test_compactsize_ff_branch():
    assert parse_compactsize("ff1001000000000000", 0) == (272, 18)


def test_compactsize_respects_starting_offset():
    # two junk bytes (4 characters) come first, then a count of 3.
    # Offsets count hex CHARACTERS, so we start at 4 and finish at 6.
    assert parse_compactsize("aaaa03", 4) == (3, 6)


# ---------------------------------------------------------------------------
# parse_version and parse_locktime
# ---------------------------------------------------------------------------

def test_parse_version():
    assert parse_version("0200000000", 0) == (2, 8)


def test_parse_locktime_with_offset():
    assert parse_locktime("00000000c93c0e00", 8) == (933065, 16)


# ---------------------------------------------------------------------------
# Constructed transactions (built by hand, not from the network)
# ---------------------------------------------------------------------------

def _legacy_input(script_len_hex, script_hex):
    return ("aa" * 32 + "00000000" + script_len_hex + script_hex + "ffffffff")


def test_constructed_legacy_transaction():
    raw = ("02000000" "01" + _legacy_input("01", "ab") +
           "01" "0008af2f00000000" "01" "cd" "c93c0e00")
    r = decode_transaction(raw)
    assert r["Version"] == 2
    assert r["TX Inputs"] == [{"txid": "aa" * 32, "vout": 0,
                               "scriptSig": "ab", "sequence": 4294967295}]
    assert r["TX Outputs"] == [{"value": 800000000, "scriptPubKey": "cd"}]
    assert r["Witness"] == []
    assert r["Locktime"] == 933065


def test_script_length_that_needs_the_fd_branch():
    # script length is written as fd 0300 (= 3 bytes), not as a single byte
    raw = ("02000000" "01" + _legacy_input("fd0300", "abcdef") +
           "01" "0008af2f00000000" "01" "cd" "00000000")
    r = decode_transaction(raw)
    assert r["TX Inputs"][0]["scriptSig"] == "abcdef"
    assert r["Locktime"] == 0


def test_constructed_segwit_one_input():
    raw = ("02000000" "0001" "01" + _legacy_input("00", "") +
           "01" "0008af2f00000000" "01" "cd" +
           "02" "01ab" "01cd" +                       # witness: 2 items
           "c93c0e00")
    r = decode_transaction(raw)
    assert r["TX Inputs"][0]["scriptSig"] == ""
    assert r["Witness"] == [["ab", "cd"]]
    assert r["Locktime"] == 933065


def test_constructed_segwit_two_inputs_one_empty_stack():
    raw = ("02000000" "0001" "02" +
           "aa" * 32 + "00000000" "00" "ffffffff" +
           "bb" * 32 + "01000000" "00" "ffffffff" +
           "01" "0008af2f00000000" "01" "cd" +
           "02" "01ab" "02cdef" +                     # input 0: two items
           "00" +                                     # input 1: empty stack
           "c93c0e00")
    r = decode_transaction(raw)
    assert [i["txid"] for i in r["TX Inputs"]] == ["aa" * 32, "bb" * 32]
    assert r["TX Inputs"][1]["vout"] == 1
    assert r["Witness"] == [["ab", "cdef"], []]
    assert r["Locktime"] == 933065


def test_unexpected_flag_byte_raises_error():
    with pytest.raises(ValueError, match="flag"):
        decode_transaction("02000000" "0005" "01")


# ---------------------------------------------------------------------------
# Real transactions. Expected values are what Bitcoin Core decoded.
# Amounts are in satoshis (Core shows BTC: e.g. 1.00000052 BTC = 100000052).
# ---------------------------------------------------------------------------

def test_real_segwit_p2wpkh_spend_with_taproot_outputs():
    # signet tx 3258177b...4f9b
    raw = "02000000000101347b0c50e1502483d82a27e5ed34ad2bd845eef27602eb7cb79bc88c25b273110600000000fdffffff07c38b7d2311000000160014004bde0ec8b987dea272d27f55b3a662fb52929800c2eb0b000000002251201f3365c8af420f3243be272cff3bdcc3be470d350bd5f04602a952fa19af7b6500e1f505000000002251204a6041f54b8cf8b2d48c6f725cb0514e51e5e7e7ac429c33da62e98765dd62f320bcbe00000000002251204a98aa12ded9f6c53e2164b90dd95d38f4be1c342ceec770c7d62d1844217cec10270000000000002251200ca90d733d23dc7def2aa2fc6ff7b15089007a38d2cec439409e6228b439165a00e1f5050000000022512097d7bdd432ae45b2ac485f144e90bb8db58cdf4fdb0e9195cefdd1736b5d52831057aa0c000000002251201604edaeb6ccf8793fac9dc24ca431406f1539502709b384e03429cf9b8de4230247304402206f92c990449007bd56b7c3cf3d39b6e621b2f74b39807e356a5b95947da384bd022043d19ea6f750782db45a66b815729ce20269bbec6938d1c0a6077db2794ba18901210389f8073ad8c686e610a46ba5b99b5ee0b368f8016f8be5d5e3f97584ff9254a1f1010500"
    r = decode_transaction(raw)
    assert r["Version"] == 2
    assert r["TX Inputs"] == [{
        "txid": "1173b2258cc89bb77ceb0276f2ee45d82bad34ede5272ad8832450e1500c7b34",
        "vout": 6, "scriptSig": "", "sequence": 4294967293}]
    assert r["TX Outputs"] == [
        {"value": 73609874371, "scriptPubKey": "0014004bde0ec8b987dea272d27f55b3a662fb529298"},
        {"value": 200000000, "scriptPubKey": "51201f3365c8af420f3243be272cff3bdcc3be470d350bd5f04602a952fa19af7b65"},
        {"value": 100000000, "scriptPubKey": "51204a6041f54b8cf8b2d48c6f725cb0514e51e5e7e7ac429c33da62e98765dd62f3"},
        {"value": 12500000, "scriptPubKey": "51204a98aa12ded9f6c53e2164b90dd95d38f4be1c342ceec770c7d62d1844217cec"},
        {"value": 10000, "scriptPubKey": "51200ca90d733d23dc7def2aa2fc6ff7b15089007a38d2cec439409e6228b439165a"},
        {"value": 100000000, "scriptPubKey": "512097d7bdd432ae45b2ac485f144e90bb8db58cdf4fdb0e9195cefdd1736b5d5283"},
        {"value": 212490000, "scriptPubKey": "51201604edaeb6ccf8793fac9dc24ca431406f1539502709b384e03429cf9b8de423"},
    ]
    assert r["Witness"] == [[
        "304402206f92c990449007bd56b7c3cf3d39b6e621b2f74b39807e356a5b95947da384bd022043d19ea6f750782db45a66b815729ce20269bbec6938d1c0a6077db2794ba18901",
        "0389f8073ad8c686e610a46ba5b99b5ee0b368f8016f8be5d5e3f97584ff9254a1"]]
    assert r["Locktime"] == 328177


def test_real_two_input_taproot_keypath_spend():
    # signet tx fbef8d40...3682
    raw = "02000000000102e99f454fa0909c0267e1f27d9ea3f552c9c8663e6ce14a46bbbca47347ce753b0000000000fdffffff1f60afaa6567d220f89f4cea74020faba40e1bbc56f348fef46f09d6006ca4120100000000fdffffff0234e1f50500000000225120b4de836e347a18d1f823f135a5d20db71a4edead9e1b58887fc604f0ed19e18fbd3a4500000000002251201b74628529b98cfdb18a84abc24066ed400fa4cc3b786793dde4f6950106f9670140ae4fbfe6f98e580583c72d7c0686cb24eae9fd0e9863ca5f2170a9adf6945f0ce7e9dfd2d4772297970d2f1918064250ba75647fce3e50aba95212011b2f14790140227abad7215c0b73d62b292007a15d5801020cf7c9e853605f09f7cf1d443f3c14aae7054949e0d19841e241b09321261f859c621392d809ae0c0ac286fada6c00000000"
    r = decode_transaction(raw)
    assert r["Version"] == 2
    assert r["TX Inputs"] == [
        {"txid": "3b75ce4773a4bcbb464ae16c3e66c8c952f5a39e7df2e167029c90a04f459fe9",
         "vout": 0, "scriptSig": "", "sequence": 4294967293},
        {"txid": "12a46c00d6096ff4fe48f356bc1b0ea4ab0f0274ea4c9ff820d26765aaaf601f",
         "vout": 1, "scriptSig": "", "sequence": 4294967293},
    ]
    assert r["TX Outputs"] == [
        {"value": 100000052, "scriptPubKey": "5120b4de836e347a18d1f823f135a5d20db71a4edead9e1b58887fc604f0ed19e18f"},
        {"value": 4537021, "scriptPubKey": "51201b74628529b98cfdb18a84abc24066ed400fa4cc3b786793dde4f6950106f967"},
    ]
    assert r["Witness"] == [
        ["ae4fbfe6f98e580583c72d7c0686cb24eae9fd0e9863ca5f2170a9adf6945f0ce7e9dfd2d4772297970d2f1918064250ba75647fce3e50aba95212011b2f1479"],
        ["227abad7215c0b73d62b292007a15d5801020cf7c9e853605f09f7cf1d443f3c14aae7054949e0d19841e241b09321261f859c621392d809ae0c0ac286fada6c"],
    ]
    assert r["Locktime"] == 0


def test_real_coinbase_transaction():
    # signet tx 20c6888b...bb6c (first transaction of block 328163)
    raw = "020000000001010000000000000000000000000000000000000000000000000000000000000000ffffffff0f03e301050a2f7369676e65743a332ffeffffff02472c4a95000000001600141ebfbc64c4d28f44c7afac95df51b1281986e6de0000000000000000776a24aa21a9ed9945820e9c48ec36db01926bbe14f76f0a562fbf9bbd1e792e37445df53599564c4fecc7daa24900473044022033bda7b18caefb7bb1a50bb3b673dd352f5fa00c5696f230125dcef449b8f82b02206f971a5455445b9284eed687dbe0efdae5bbb0617ef1300c326cff21f2544f10010001200000000000000000000000000000000000000000000000000000000000000000e2010500"
    r = decode_transaction(raw)
    assert r["Version"] == 2
    # a coinbase input has a null previous output: all-zero txid, vout 0xffffffff
    assert r["TX Inputs"] == [{
        "txid": "00" * 32, "vout": 4294967295,
        "scriptSig": "03e301050a2f7369676e65743a332f", "sequence": 4294967294}]
    assert r["TX Outputs"] == [
        {"value": 2504666183, "scriptPubKey": "00141ebfbc64c4d28f44c7afac95df51b1281986e6de"},
        {"value": 0, "scriptPubKey": "6a24aa21a9ed9945820e9c48ec36db01926bbe14f76f0a562fbf9bbd1e792e37445df53599564c4fecc7daa24900473044022033bda7b18caefb7bb1a50bb3b673dd352f5fa00c5696f230125dcef449b8f82b02206f971a5455445b9284eed687dbe0efdae5bbb0617ef1300c326cff21f2544f100100"},
    ]
    # the witness reserved value: one item of 32 zero bytes
    assert r["Witness"] == [["00" * 32]]
    assert r["Locktime"] == 328162


def test_real_segwit_with_p2wsh_and_taproot_outputs():
    # signet tx 59f269d0...6352 (segwit, despite an earlier "non-segwit" label)
    raw = "02000000000101591a6dbf59a71ed1b158eead2eb0fc5e03e47852d90540c7e2fac0bcc6f772930200000000ffffffff034c1d000000000000220020fffb3e42a31b55afb18cb468ddb26550b7dd65f270434599992bc49f61cac74bc40900000000000022512052d19a46c1a8cd90001a816420448b612d9c13bdb50d02d716d411deb94dc93002aa4b000000000022512078c3e54e137bb0224a41e56e99cfbb17579982b357834b9433015435b3db89260140e8d1bce94f93c68cba51ea012fcaeab68a1f335bb9bb35cbe7daa45cae855397d350e1eccb2403322597a0af782b1b32d2d4531c47c2df93644ef83f0b0bfbdc00000000"
    r = decode_transaction(raw)
    assert r["Version"] == 2
    assert r["TX Inputs"] == [{
        "txid": "9372f7c6bcc0fae2c74005d95278e4035efcb02eadee58b1d11ea759bf6d1a59",
        "vout": 2, "scriptSig": "", "sequence": 4294967295}]
    assert r["TX Outputs"] == [
        {"value": 7500, "scriptPubKey": "0020fffb3e42a31b55afb18cb468ddb26550b7dd65f270434599992bc49f61cac74b"},
        {"value": 2500, "scriptPubKey": "512052d19a46c1a8cd90001a816420448b612d9c13bdb50d02d716d411deb94dc930"},
        {"value": 4958722, "scriptPubKey": "512078c3e54e137bb0224a41e56e99cfbb17579982b357834b9433015435b3db8926"},
    ]
    assert r["Witness"] == [[
        "e8d1bce94f93c68cba51ea012fcaeab68a1f335bb9bb35cbe7daa45cae855397d350e1eccb2403322597a0af782b1b32d2d4531c47c2df93644ef83f0b0bfbdc"]]
    assert r["Locktime"] == 0


def test_real_legacy_p2pkh_transaction():
    # example from the Bitcoin developer docs; decoded by Core with
    # decoderawtransaction (txid c7736a0a...ffba)
    raw = "01000000017b1eabe0209b1fe794124575ef807057c77ada2138ae4fa8d6c4de0398a14f3f00000000494830450221008949f0cb400094ad2b5eb399d59d01c14d73d8fe6e96df1a7150deb388ab8935022079656090d7f6bac4c9a94e0aad311a4268e082a725f8aeae0573fb12ff866a5f01ffffffff01f0ca052a010000001976a914cbc20a7664f2f69e5355aa427045bc15e7c6c77288ac00000000"
    r = decode_transaction(raw)
    assert r["Version"] == 1
    assert r["TX Inputs"] == [{
        "txid": "3f4fa19803dec4d6a84fae3821da7ac7577080ef75451294e71f9b20e0ab1e7b",
        "vout": 0,
        "scriptSig": "4830450221008949f0cb400094ad2b5eb399d59d01c14d73d8fe6e96df1a7150deb388ab8935022079656090d7f6bac4c9a94e0aad311a4268e082a725f8aeae0573fb12ff866a5f01",
        "sequence": 4294967295}]
    assert r["TX Outputs"] == [{
        "value": 4999990000,
        "scriptPubKey": "76a914cbc20a7664f2f69e5355aa427045bc15e7c6c77288ac"}]
    assert r["Witness"] == []
    assert r["Locktime"] == 0


# ---------------------------------------------------------------------------
# Large real mainnet transaction, checked against its published txid.
#
# The raw hex lives in test_data/ because it is about 43,000 characters long.
# Unlike the tests above, the expected answer here does not come from our own
# decoder or from Bitcoin Core's JSON: it is the transaction's txid on the
# Bitcoin network. A txid is the double SHA-256 hash of the transaction's
# non-witness bytes, so if we rebuild those bytes from the decoded fields and
# hash them, the result equals the real txid only if every field was decoded
# correctly (version, every input, every output, locktime).
# ---------------------------------------------------------------------------

def _compactsize_bytes(n):
    if n <= 252:
        return n.to_bytes(1, "little")
    if n <= 0xffff:
        return b"\xfd" + n.to_bytes(2, "little")
    if n <= 0xffffffff:
        return b"\xfe" + n.to_bytes(4, "little")
    return b"\xff" + n.to_bytes(8, "little")


def _serialize(decoded, with_witness):
    """Rebuild the raw transaction bytes from decode_transaction()'s result."""
    out = decoded["Version"].to_bytes(4, "little")
    if with_witness:
        out += b"\x00\x01"                                # marker and flag
    out += _compactsize_bytes(len(decoded["TX Inputs"]))
    for tx_in in decoded["TX Inputs"]:
        out += bytes.fromhex(tx_in["txid"])[::-1]           # back to stored byte order
        out += tx_in["vout"].to_bytes(4, "little")
        script = bytes.fromhex(tx_in["scriptSig"])
        out += _compactsize_bytes(len(script)) + script
        out += tx_in["sequence"].to_bytes(4, "little")
    out += _compactsize_bytes(len(decoded["TX Outputs"]))
    for tx_out in decoded["TX Outputs"]:
        script = bytes.fromhex(tx_out["scriptPubKey"])
        out += tx_out["value"].to_bytes(8, "little")
        out += _compactsize_bytes(len(script)) + script
    if with_witness:
        for stack in decoded["Witness"]:
            out += _compactsize_bytes(len(stack))
            for item in stack:
                item_bytes = bytes.fromhex(item)
                out += _compactsize_bytes(len(item_bytes)) + item_bytes
    out += decoded["Locktime"].to_bytes(4, "little")
    return out


def test_real_mainnet_143_inputs_matches_published_txid():
    hex_path = Path(__file__).parent / "test_data" / "mainnet_84a907af.hex"
    raw = hex_path.read_text().strip()
    r = decode_transaction(raw)

    # shape of the transaction
    assert len(r["TX Inputs"]) == 143
    assert len(r["TX Outputs"]) == 11
    assert len(r["Witness"]) == 143          # one witness stack per input

    # independent check: the txid recomputed from the decoded fields must equal
    # the transaction's real txid on the network
    legacy_bytes = _serialize(r, with_witness=False)
    txid = hashlib.sha256(hashlib.sha256(legacy_bytes).digest()).digest()[::-1].hex()
    assert txid == "84a907af154b062212e56cae5a201b812d17abf096bd32cc67a5c91203e7c83b"

    # nothing skipped or lost: re-encoding everything, witness included,
    # reproduces the original hex exactly
    assert _serialize(r, with_witness=True).hex() == raw
