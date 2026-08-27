#!/usr/bin/env bash
# Print the payment quote (HTTP 402 challenge) for one oblique.markets paid route, without paying.
# Usage: scripts/quote.sh bazaar-pulse
#        scripts/quote.sh 'base-usdc-balance?address=0x970007590aCC5C938cd51345B17AF51B1B40D3Ab'
#        scripts/quote.sh web-extract POST '{"url":"https://example.com"}'
# Requires: curl, python3. No wallet needed.
set -euo pipefail
route="${1:?route, e.g. bazaar-pulse}"; method="${2:-GET}"; body="${3:-}"
url="https://api.oblique.markets/api/v1/paid/${route#/}"
hdr="$(mktemp)"; trap 'rm -f "$hdr"' EXIT
if [ "$method" = "POST" ]; then
  resp="$(curl -sS -m 30 -A oblique-skill-quote/1.0 -D "$hdr" -X POST -H 'Content-Type: application/json' -d "${body:-{\}}" "$url")"
else
  resp="$(curl -sS -m 30 -A oblique-skill-quote/1.0 -D "$hdr" "$url")"
fi
code="$(sed -n 's#^HTTP/[0-9.]* \([0-9]*\).*#\1#p' "$hdr" | tail -1)"
echo "HTTP $code  $method $url"
grep -i '^x-payment-amount:' "$hdr" || true
python3 - "$resp" "$(grep -i '^www-authenticate:' "$hdr" | sed 's/^[^ ]* //' | tr -d '\r')" <<'EOF'
import sys, json, base64, re
body, wa = sys.argv[1], sys.argv[2]
try:
    d = json.loads(body)
except Exception:
    print(body[:800]); sys.exit(0)
for a in d.get("accepts", []):
    usd = int(a["amount"]) / 1_000_000
    print(f'x402  network={a["network"]}  scheme={a["scheme"]}  amount={a["amount"]} (${usd:.6f})  payTo={a["payTo"]}  asset={a["asset"]}')
m = re.search(r'request="([^"]+)"', wa)
if m:
    raw = m.group(1); raw += "=" * (-len(raw) % 4)
    req = json.loads(base64.urlsafe_b64decode(raw))
    meth = re.search(r'method="([^"]+)"', wa); intent = re.search(r'intent="([^"]+)"', wa)
    print(f'mpp   method={meth.group(1) if meth else "?"} intent={intent.group(1) if intent else "?"} chainId={req.get("methodDetails",{}).get("chainId")} amount={req.get("amount")} currency={req.get("currency")} recipient={req.get("recipient")}')
info = d.get("extensions", {}).get("bazaar", {}).get("info", {})
if info:
    print("input :", json.dumps(info.get("input")))
    ex = info.get("output", {}).get("example")
    if ex is not None:
        print("output example:", json.dumps(ex)[:1200])
EOF
