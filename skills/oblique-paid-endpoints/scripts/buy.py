#!/usr/bin/env python3
"""Buy one result from an oblique.markets paid route over x402 (USDC on Base).

A self-contained reference buyer: no x402 SDK, two dependencies (requests, eth-account).
It performs the same loop the SDKs perform, in the open:

  1. send the request unpaid and read the HTTP 402 quote
  2. refuse anything above your ceiling (--max-usd) before signing
  3. sign an EIP-3009 transferWithAuthorization for exactly the quoted amount
  4. retry once with PAYMENT-SIGNATURE and print the JSON result plus the decoded receipt

Usage:
  scripts/buy.py bazaar-pulse --key-file ./buyer.key
  scripts/buy.py 'base-usdc-balance?address=0x970007590aCC5C938cd51345B17AF51B1B40D3Ab' --key-file ./buyer.key
  scripts/buy.py web-extract --post '{"url":"https://example.com"}' --max-usd 0.05 --key-file ./buyer.key
  scripts/buy.py bazaar-pulse --quote-only            # no key needed: print the quote, exit

--key-file is a file holding either a bare 0x hex private key or JSON with a "private_key"
field. The key is read from that file only, never from the command line or the shell.
Use a dedicated wallet holding a little USDC on Base. Only the x402 `exact` scheme on an
EVM network is implemented (Base by default); Solana and MPP need the SDKs named in SKILL.md.

Exit codes: 0 settled · 2 no usable 402 · 3 quote above ceiling · 4 payment rejected ·
5 input rejected by the route (a 4xx after payment settles nothing).
"""
import argparse
import base64
import json
import secrets
import sys
import time

import requests

DEFAULT_HOST = "https://api.oblique.markets"
PAID_PREFIX = "/api/v1/paid/"
USER_AGENT = "oblique-skills/1.2.0 (oblique-paid-endpoints)"
CHAIN_IDS = {"eip155:8453": 8453}


def load_key(path):
    from eth_account import Account  # only needed once we actually pay

    with open(path) as f:
        raw = f.read().strip()
    if raw.startswith("{"):
        raw = json.loads(raw)["private_key"]
    return Account.from_key(raw)


def route_url(route, host):
    if route.startswith("http://") or route.startswith("https://"):
        return route
    if route.startswith("/"):
        return host + route
    return host + PAID_PREFIX + route


def pick_accept(challenge, network):
    for a in challenge.get("accepts") or []:
        if a.get("network") == network and a.get("scheme", "exact") == "exact":
            return a
    return None


def atomic_to_usd(amount):
    return int(amount) / 1_000_000


def sign_exact(accept, acct, chain_id):
    """EIP-3009 transferWithAuthorization for exactly the quoted amount."""
    from eth_account.messages import encode_typed_data

    asset = accept["asset"]
    amount = int(accept.get("amount") or accept["maxAmountRequired"])
    now = int(time.time())
    authorization = {
        "from": acct.address,
        "to": accept["payTo"],
        "value": amount,
        "validAfter": 0,
        "validBefore": now + min(int(accept.get("maxTimeoutSeconds") or 60), 3600) + 600,
        "nonce": "0x" + secrets.token_hex(32),
    }
    extra = accept.get("extra") or {}
    typed = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": extra.get("name", "USD Coin"),
            "version": extra.get("version", "2"),
            "chainId": chain_id,
            "verifyingContract": asset,
        },
        "message": authorization,
    }
    signed = acct.sign_message(encode_typed_data(full_message=typed))
    sig = signed.signature.hex()
    if not sig.startswith("0x"):
        sig = "0x" + sig
    return {
        "x402Version": 2,
        "scheme": "exact",
        "network": accept["network"],
        "payload": {
            "signature": sig,
            "authorization": {k: (str(v) if isinstance(v, int) else v) for k, v in authorization.items()},
        },
    }


def decode_receipt(header_value):
    if not header_value:
        return None
    padded = header_value + "=" * (-len(header_value) % 4)
    try:
        return json.loads(base64.b64decode(padded))
    except Exception:
        return {"raw": header_value}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("route", help="slug (bazaar-pulse), path (/api/v1/paid/time) or full URL; query string allowed")
    ap.add_argument("--key-file", help="file holding the buyer private key (hex, or JSON with private_key)")
    ap.add_argument("--post", help="JSON body; makes the request a POST")
    ap.add_argument("--max-usd", type=float, default=0.01, help="refuse quotes above this (default 0.01)")
    ap.add_argument("--network", default="eip155:8453", help="CAIP-2 network to pay on (default Base)")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--quote-only", action="store_true", help="print the quote and exit without paying")
    args = ap.parse_args()

    url = route_url(args.route, args.host)
    method = "POST" if args.post is not None else "GET"
    body = json.loads(args.post) if args.post is not None else None
    headers = {"User-Agent": USER_AGENT}

    r = requests.request(method, url, json=body, headers=headers, timeout=30)
    if r.status_code != 402:
        print(f"expected 402, got {r.status_code}: {r.text[:300]}")
        return 2
    challenge = r.json()
    accept = pick_accept(challenge, args.network)
    if accept is None:
        offered = [a.get("network") for a in challenge.get("accepts") or []]
        print(f"no exact-scheme quote for {args.network}; offered: {offered}")
        return 2
    usd = atomic_to_usd(accept.get("amount") or accept["maxAmountRequired"])
    print(f"quote  {method} {url}")
    print(f"       {usd:.6f} USD on {accept['network']}  payTo={accept['payTo']}  asset={accept['asset']}")
    info = (challenge.get("extensions") or {}).get("bazaar", {}).get("info") or {}
    if info.get("input"):
        print("input  " + json.dumps(info["input"])[:400])
    if args.quote_only:
        return 0
    if usd > args.max_usd:
        print(f"refused: quote {usd:.6f} USD is above the ceiling {args.max_usd:.6f} USD (nothing signed)")
        return 3
    if not args.key_file:
        print("no --key-file given; nothing signed (use --quote-only to just read quotes)")
        return 3
    chain_id = CHAIN_IDS.get(accept["network"])
    if chain_id is None:
        print(f"network {accept['network']} is not an EVM chain this script knows")
        return 2

    acct = load_key(args.key_file)
    payment = sign_exact(accept, acct, chain_id)
    headers["PAYMENT-SIGNATURE"] = base64.b64encode(json.dumps(payment).encode()).decode()
    r2 = requests.request(method, url, json=body, headers=headers, timeout=60)

    receipt = decode_receipt(r2.headers.get("PAYMENT-RESPONSE"))
    if r2.status_code == 402:
        print(f"payment rejected: {r2.text[:400]}")
        return 4
    if r2.status_code >= 400:
        print(f"route rejected the input ({r2.status_code}), nothing settled: {r2.text[:400]}")
        return 5
    print(f"paid   {r2.status_code} from {acct.address}")
    if receipt:
        print("receipt " + json.dumps(receipt))
    try:
        print(json.dumps(r2.json(), indent=2)[:4000])
    except ValueError:
        print(r2.text[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
