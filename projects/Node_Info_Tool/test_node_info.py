# Unit tests for node_info.py
#
# Run from the folder that contains node_info.py and this file:
#     python3 -m pytest -v
#
# None of these tests need a running node. The format functions are checked
# against fixed dictionaries; read_cookie is checked against a throwaway file;
# and rpc_call / main() are checked by swapping the real network call for a
# fake one (pytest's `monkeypatch` does the swapping and undoes it afterwards).

import sys

import pytest
import requests

import node_info
from node_info import (
    read_cookie,
    rpc_call,
    format_chain_section,
    format_network_section,
    format_mempool_section,
)


# ---------------------------------------------------------------------------
# Test data: shaped like real replies from the signet node
# ---------------------------------------------------------------------------

BLOCK_TIME = 1793862647   # a fixed block timestamp, so ages are predictable

CHAIN = {
    "chain": "signet",
    "blocks": 329509,
    "headers": 329509,
    "difficulty": 0.04806969390457064,
    "time": BLOCK_TIME,
    "verificationprogress": 1,
}

NETWORK = {
    "subversion": "/Satoshi:31.1.0/",
    "networkactive": True,
    "connections": 11,
    "connections_in": 0,
    "connections_out": 11,
    "timeoffset": -2,
}

MEMPOOL = {
    "size": 71,
    "bytes": 29129,
    "total_fee": 0.00089255,
}


# ---------------------------------------------------------------------------
# format_chain_section
# ---------------------------------------------------------------------------

def test_chain_section_full_output():
    # the whole report, exactly as it should print (block is 10 minutes old)
    expected = (
        "Chain:              signet\n"
        "Validated blocks:   329509\n"
        "Blocks remaining:   0\n"
        "Difficulty:         0.0481\n"
        "Latest block:       10 minutes ago\n"
        "Sync progress:      100.00%"
    )
    assert format_chain_section(CHAIN, now=BLOCK_TIME + 600) == expected


def test_chain_section_age_is_whole_minutes():
    # 659 seconds is 10 minutes and 59 seconds: floor to 10, no decimal
    result = format_chain_section(CHAIN, now=BLOCK_TIME + 659)
    assert "10 minutes ago" in result
    assert "10.0" not in result


def test_chain_section_blocks_remaining_is_headers_minus_blocks():
    info = dict(CHAIN, blocks=95, headers=100)
    assert "Blocks remaining:   5" in format_chain_section(info, now=BLOCK_TIME)


def test_chain_section_sync_progress_as_percentage():
    info = dict(CHAIN, verificationprogress=0.5)
    assert "Sync progress:      50.00%" in format_chain_section(info, now=BLOCK_TIME)


def test_chain_section_uses_real_clock_when_now_not_given():
    # a block timestamped "right now" should read as 0 minutes ago
    import time
    info = dict(CHAIN, time=int(time.time()))
    assert "Latest block:       0 minutes ago" in format_chain_section(info)


# ---------------------------------------------------------------------------
# format_network_section
# ---------------------------------------------------------------------------

def test_network_section_full_output():
    expected = (
        "Node software:      /Satoshi:31.1.0/\n"
        "Network active:     Yes\n"
        "Connections:        11 (0 in, 11 out)\n"
        "Clock offset:       -2 s"
    )
    assert format_network_section(NETWORK) == expected


def test_network_section_inactive_shows_no():
    info = dict(NETWORK, networkactive=False)
    assert "Network active:     No" in format_network_section(info)


# ---------------------------------------------------------------------------
# format_mempool_section
# ---------------------------------------------------------------------------

def test_mempool_section_full_output():
    expected = (
        "Transactions:       71\n"
        "Virtual size:       29.1 kB\n"
        "Total fees:         0.00089255 BTC"
    )
    assert format_mempool_section(MEMPOOL) == expected


def test_mempool_section_tiny_fee_not_scientific_notation():
    # Python prints 4e-05 for small floats; the report must show 8 decimals
    info = dict(MEMPOOL, total_fee=0.00004)
    result = format_mempool_section(info)
    assert "0.00004000 BTC" in result
    assert "e-05" not in result


def test_mempool_section_empty_pool():
    info = {"size": 0, "bytes": 0, "total_fee": 0}
    expected = (
        "Transactions:       0\n"
        "Virtual size:       0.0 kB\n"
        "Total fees:         0.00000000 BTC"
    )
    assert format_mempool_section(info) == expected


# ---------------------------------------------------------------------------
# read_cookie   (tmp_path is a throwaway folder pytest creates for each test)
# ---------------------------------------------------------------------------

def test_read_cookie_returns_user_and_password(tmp_path):
    cookie = tmp_path / ".cookie"
    cookie.write_text("__cookie__:abc123\n")   # trailing newline, like the real file
    assert read_cookie(str(cookie)) == ("__cookie__", "abc123")


def test_read_cookie_splits_only_on_first_colon(tmp_path):
    cookie = tmp_path / ".cookie"
    cookie.write_text("user:pass:word")
    assert read_cookie(str(cookie)) == ("user", "pass:word")


def test_read_cookie_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_cookie(str(tmp_path / "does-not-exist"))


# ---------------------------------------------------------------------------
# rpc_call   (requests.post is replaced by a fake that returns a canned reply)
# ---------------------------------------------------------------------------

class FakeResponse:
    """Stands in for the object requests.post returns."""

    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


def test_rpc_call_returns_the_parsed_reply(monkeypatch):
    reply = {"result": 329509, "error": None, "id": "node_info"}
    monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse(200, reply))
    assert rpc_call("getblockcount", [], ("u", "p")) == reply


def test_rpc_call_sends_method_params_auth_and_url(monkeypatch):
    seen = {}

    def fake_post(url, json=None, auth=None):
        seen["url"] = url
        seen["json"] = json
        seen["auth"] = auth
        return FakeResponse(200, {"result": 1, "error": None, "id": "node_info"})

    monkeypatch.setattr(requests, "post", fake_post)
    rpc_call("getblockhash", [100], ("u", "p"), url="http://example.test/")

    assert seen["url"] == "http://example.test/"
    assert seen["auth"] == ("u", "p")
    assert seen["json"]["method"] == "getblockhash"
    assert seen["json"]["params"] == [100]


def test_rpc_call_bad_credentials_raises(monkeypatch):
    # a 401 comes with an empty body, so json() must never be reached
    monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse(401, None))
    with pytest.raises(RuntimeError, match="Authentication failed"):
        rpc_call("getblockcount", [], ("wrong", "wrong"))


def test_rpc_call_node_error_raises_with_message_and_code(monkeypatch):
    reply = {"result": None,
             "error": {"code": -32601, "message": "Method not found"},
             "id": "node_info"}
    monkeypatch.setattr(requests, "post", lambda *a, **kw: FakeResponse(404, reply))
    with pytest.raises(RuntimeError) as excinfo:
        rpc_call("notarealcommand", [], ("u", "p"))
    assert "Method not found" in str(excinfo.value)
    assert "-32601" in str(excinfo.value)


# ---------------------------------------------------------------------------
# main()   (capsys captures what it prints; monkeypatch sets the command line)
# ---------------------------------------------------------------------------

def test_main_without_argument_prints_usage_and_exits(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["node_info.py"])
    with pytest.raises(SystemExit) as excinfo:
        node_info.main()
    assert excinfo.value.code == 1
    assert "Usage:" in capsys.readouterr().out


def test_main_missing_cookie_file_exits_with_message(monkeypatch, capsys, tmp_path):
    missing = str(tmp_path / "nope" / ".cookie")
    monkeypatch.setattr(sys, "argv", ["node_info.py", missing])
    with pytest.raises(SystemExit) as excinfo:
        node_info.main()
    assert excinfo.value.code == 1
    assert "Cookie file not found" in capsys.readouterr().out


def test_main_node_unreachable_exits_with_message(monkeypatch, capsys, tmp_path):
    cookie = tmp_path / ".cookie"
    cookie.write_text("__cookie__:abc123")
    monkeypatch.setattr(sys, "argv", ["node_info.py", str(cookie)])

    def refuse(*args, **kwargs):
        raise requests.exceptions.ConnectionError("refused")

    monkeypatch.setattr(node_info, "rpc_call", refuse)
    with pytest.raises(SystemExit) as excinfo:
        node_info.main()
    assert excinfo.value.code == 1
    assert "Could not connect" in capsys.readouterr().out


def test_main_node_error_exits_with_the_error_message(monkeypatch, capsys, tmp_path):
    cookie = tmp_path / ".cookie"
    cookie.write_text("__cookie__:abc123")
    monkeypatch.setattr(sys, "argv", ["node_info.py", str(cookie)])

    def reject(*args, **kwargs):
        raise RuntimeError("Authentication failed")

    monkeypatch.setattr(node_info, "rpc_call", reject)
    with pytest.raises(SystemExit) as excinfo:
        node_info.main()
    assert excinfo.value.code == 1
    assert "Authentication failed" in capsys.readouterr().out


def test_main_prints_all_three_sections(monkeypatch, capsys, tmp_path):
    cookie = tmp_path / ".cookie"
    cookie.write_text("__cookie__:abc123")
    monkeypatch.setattr(sys, "argv", ["node_info.py", str(cookie)])

    replies = {
        "getblockchaininfo": CHAIN,
        "getnetworkinfo": NETWORK,
        "getmempoolinfo": MEMPOOL,
    }

    def fake_rpc_call(method, params, auth, url=None):
        return {"result": replies[method], "error": None, "id": "node_info"}

    monkeypatch.setattr(node_info, "rpc_call", fake_rpc_call)
    node_info.main()

    out = capsys.readouterr().out
    assert "CHAIN INFO:" in out
    assert "NETWORK INFO:" in out
    assert "MEMPOOL INFO:" in out
    assert "Chain:              signet" in out
    assert "Node software:      /Satoshi:31.1.0/" in out
    assert "Transactions:       71" in out
