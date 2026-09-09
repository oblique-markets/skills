#!/usr/bin/env python3
"""Print the live oblique.markets paid catalogue as a Markdown table (free, no wallet).

Reads the seller's x402 discovery document and prints one row per paid route with
method, path, price, category and what it returns. This is the script that generates
references/catalog.md; run it whenever you want today's prices instead of the snapshot.

Usage:
  scripts/catalog.py                 # Markdown table of the live catalogue
  scripts/catalog.py --json          # the routes as JSON (path, method, price, priceAtomic, category, description)
  scripts/catalog.py --grep bazaar   # only routes whose path or description matches

Routes whose slug or description leans on a third-party product name are omitted by
default (they are scheduled for renaming and keep answering meanwhile); pass
--skip-pattern '' to print every route the catalogue advertises.
"""
import argparse
import json
import re
import sys

import requests

CATALOG_URL = "https://oblique.markets/.well-known/x402.json"
DEFAULT_SKIP = r"^/api/v1/paid/rep-|-compatible\b|-shaped\b|equivalent of"


def clean_description(text):
    text = (text or "").strip()
    m = re.match(r"^Use when [^.]*\. Returns (.*)$", text, re.S)
    if m:
        text = m.group(1).strip()
    text = re.sub(r"\s*\$\d[\d.]*(?: per call[^.]*| (?:maximum|fixed)[^.]*)?\.?\s*$", "", text)
    text = text.strip()
    if text and text[-1] not in ".!?":
        text += "."
    return text


def fetch(url):
    r = requests.get(url, headers={"User-Agent": "oblique-skill-catalog/1.1"}, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--grep", help="case-insensitive filter on path + description")
    ap.add_argument("--skip-pattern", default=DEFAULT_SKIP, help="regex; matching path+description rows are omitted")
    ap.add_argument("--url", default=CATALOG_URL)
    args = ap.parse_args()

    doc = fetch(args.url)
    rows = []
    skipped = 0
    for e in doc.get("endpoints", []):
        path = e.get("path") or ""
        desc = e.get("description") or ""
        hay = path + " " + desc
        if args.skip_pattern and re.search(args.skip_pattern, hay, re.I):
            skipped += 1
            continue
        if args.grep and not re.search(args.grep, hay, re.I):
            continue
        rows.append({
            "method": e.get("method", "GET"),
            "path": path,
            "price": e.get("price"),
            "priceAtomic": e.get("priceAtomic"),
            "category": e.get("bazaarCategory"),
            "description": clean_description(desc),
            "networks": [p.get("network") for p in e.get("paymentOptions") or []],
            "mpp": bool(e.get("mpp")),
        })

    if args.json:
        json.dump({"source": args.url, "routes": rows, "omitted": skipped}, sys.stdout, indent=1)
        print()
        return 0

    seller = doc.get("seller") or {}
    print(f"# oblique.markets paid catalogue — {len(rows)} routes (read live from {args.url})")
    print()
    if isinstance(seller, dict) and seller.get("name"):
        print(f"Seller: {seller.get('name')}. ", end="")
    print(f"x402 version {doc.get('x402Version')}; every route also answers an MPP challenge. "
          f"Prices are per call in USD; atomic units are USDC with 6 decimals. "
          f"{skipped} route(s) pending renaming are omitted from this table.")
    print()
    print("| Method | Path | Price | Category | What it returns |")
    print("|---|---|---|---|---|")
    for r in rows:
        d = r["description"].replace("|", "\\|")
        print(f"| {r['method']} | `{r['path']}` | {r['price']} | {r['category'] or ''} | {d} |")
    print()
    nets = doc.get("networks") or {}
    if nets:
        print("## Pay-to addresses advertised by the catalogue")
        print()
        for net, v in nets.items():
            if isinstance(v, dict):
                print(f"- `{net}`: asset `{v.get('asset')}` → `{v.get('payTo')}`")
        print()
    facs = doc.get("facilitators") or {}
    if facs:
        parts = []
        for net, v in facs.items():
            if isinstance(v, dict):
                parts.append(f"`{net}` → {v.get('name')} `{v.get('url')}`")
            elif isinstance(v, str):
                parts.append(f"`{net}` → `{v}`")
        print("Facilitators: " + "; ".join(parts))
        print()
    print("Never hard-code these: the 402 challenge for each request carries the authoritative "
          "`payTo`, `asset`, `amount` and `network`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
