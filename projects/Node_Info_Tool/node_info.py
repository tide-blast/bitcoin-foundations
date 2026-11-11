import requests
import time
import sys

def read_cookie(path):
    with open(path, "r") as f:
        content = f.read().strip()   # reads the whole file into one string and strips any newlines.
    rpcuser, rpcpassword = content.split(":",1)   # splits the content into two variables before/after ":"
    auth = (rpcuser, rpcpassword)
    return auth

def rpc_call(method, params, auth, url="http://127.0.0.1:38332/"):
    payload = {
        "jsonrpc": "1.0",
        "id": "node_info",
        "method": method,
        "params": params
    }

    response = requests.post(url, json=payload, auth=auth)  #Request sent to the node
    if response.status_code == 401:                         #status_code: the number (ex.: 200, 401, 404, 500) sent from the node
        raise RuntimeError("Authentication failed")

    data = response.json()
    if data["error"] is not None:
        raise RuntimeError(f"Node returned an error: {data['error']['message']} (code {data['error']['code']})")

    return data

def format_chain_section(info, now=None):
    if now is None:                # "now" defaults to the real time. Tests pass a fixed value so the output is predictable.
        now = time.time()

    lines = [
            f"Chain:              {info['chain']}",
            f"Validated blocks:   {info['blocks']}",
            f"Blocks remaining:   {info['headers'] - info['blocks']}",
            f"Difficulty:         {info['difficulty']:.4f}",
            f"Latest block:       {int((now - info['time']) // 60)} minutes ago",
            f"Sync progress:      {info['verificationprogress'] * 100:.2f}%",
            ]

    return "\n".join(lines)


def format_network_section(info):
    if info['networkactive']:   #Do not need to directly verify with "== True"
        networkstatus = "Yes"
    else:
        networkstatus = "No"

    lines = [
            f"Node software:      {info['subversion']}",
            f"Network active:     {networkstatus}",
            f"Connections:        {info['connections']} ({info['connections_in']} in, {info['connections_out']} out)",
            f"Clock offset:       {info['timeoffset']} s",
            ]    

    return "\n".join(lines)


def format_mempool_section(info):
    lines = [
            f"Transactions:       {info['size']}",
            f"Virtual size:       {info['bytes'] / 1000:.1f} kB",
            f"Total fees:         {info['total_fee']:.8f} BTC",
            ]    

    return "\n".join(lines)


def main():        
    if len(sys.argv) > 1:   #sys.argv = Saves the command-line arguments as strings in a list. Starts at "0", the script-name (not "python3").
                            #Example command prompt: python3 node_info.py <cookie file path>
                            # Word "1" should be <cookie file path>.
        cookie_path = sys.argv[1].strip()   #strip removes spaces of newline characters
        try:                                #Error handling for a cookie path issue
            auth = read_cookie(cookie_path)
        except FileNotFoundError:
            print(f"Cookie file not found: {cookie_path}")
            sys.exit(1)
    else:
        print("Usage: python3 node_info.py <cookie file path>")
        sys.exit(1)
        
    try:
        chain = rpc_call("getblockchaininfo", [], auth)["result"]
        network = rpc_call("getnetworkinfo", [], auth)["result"]
        mempool = rpc_call("getmempoolinfo", [], auth)["result"]
    except requests.exceptions.ConnectionError:
        print("Could not connect to the node at 127.0.0.1:38332. Is bitcoind running?")
        sys.exit(1)
    except RuntimeError as e:
        print(e)
        sys.exit(1)
    
    print("CHAIN INFO:")
    print(format_chain_section(chain))
    print()    
    print("NETWORK INFO:")
    print(format_network_section(network))
    print()
    print("MEMPOOL INFO:")
    print(format_mempool_section(mempool))


if __name__ == "__main__":
    main()

