---
name: oblique-paid-endpoints
description: Buy pay-per-call API results from oblique.markets (https://api.oblique.markets/api/v1/paid/*) over HTTP 402 — x402 with USDC on Base or Solana, or MPP/Tempo — with no account and no API key. Use when an agent needs x402 Bazaar market data, Base chain state (gas, block, USDC balance, tx status), web extraction, sentiment, task routing or LLM inference and can pay a few tenths of a cent per call from its own wallet.
license: MIT
metadata:
  author: oblique-markets
  version: "1.0.0"
  homepage: https://oblique.markets
---

# Buying from oblique.markets paid endpoints

Every route under `https://api.oblique.markets/api/v1/paid/*` answers an unpaid request
with **HTTP 402** and a machine-readable quote. You pay the quoted amount, retry the same
request with a payment header, and get JSON. There are no accounts and no API keys; the
payment is the authentication. Two rails are offered on the same 402 (dual-stack):

| Rail | Networks / asset | Retry header | Success header |
|---|---|---|---|
| **x402 v2** | Base `eip155:8453` USDC · Solana `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` USDC | `PAYMENT-SIGNATURE: <base64 payment payload>` | `PAYMENT-RESPONSE` |
| **MPP (Machine Payments Protocol)** | Tempo mainnet chainId `4217`, method `tempo`, intent `charge`, currency `0x20c0000000000000000000000000000000000000` (pathUSD) | `Authorization: Payment <base64url credential>` | `Payment-Receipt` |

Prices are per call, quoted in USD and settled in stablecoin atomic units (6 decimals:
`"2000"` = $0.002). As of 2026-08-27 the catalogue lists 59 paid routes from $0.001079 to
$1.00. Use an SDK that handles the 402 loop; do not hand-roll signatures.

## Discovery surfaces (all free, no auth)

| What | URL |
|---|---|
| x402 catalogue — every route with method, price, scheme, pay-to | `https://oblique.markets/.well-known/x402.json` |
| OpenAPI 3.1 — request bodies, query params, response schemas | `https://oblique.markets/openapi.json` |
| `llms.txt` (prices inline) | `https://api.oblique.markets/llms.txt` |
| Paid MCP server (59 tools, same routes; listing is free, each call is paid) | `https://api.oblique.markets/mcp` |
| Health (free) | `https://api.oblique.markets/health` |
| Worked clients: TypeScript + Python + MCP configs | `https://github.com/oblique-markets/oblique-examples` |
| Full catalogue snapshot with prices | [references/catalog.md](references/catalog.md) |

## Step 1 — read the quote (free)

```bash
curl -si https://api.oblique.markets/api/v1/paid/bazaar-pulse
```

The 402 carries the quote three ways at once:

- **`PAYMENT-REQUIRED` header** — base64 of the x402 v2 `PaymentRequired` JSON.
- **JSON body** — the same object, readable:
  `{"x402Version":2,"accepts":[{"scheme":"exact","network":"eip155:8453","amount":"2000","payTo":"0x9700…D3Ab","asset":"0x8335…2913","maxTimeoutSeconds":60,…},{"network":"solana:5eykt4…","amount":"2000","payTo":"GYyT…ykdS","asset":"EPjF…Dt1v",…}],"extensions":{"bazaar":{"info":{"input":…,"output":{"example":…}}}}}`.
  `extensions.bazaar.info` tells you the input shape and shows an example output **before you
  pay** — read it.
- **`WWW-Authenticate: Payment id="…", realm="api.oblique.markets", method="tempo", intent="charge", request="<base64url>", expires="…"`** — the MPP challenge. `request` decodes to
  `{"amount":"2000","currency":"0x20c0…0000","methodDetails":{"chainId":4217,"supportedModes":["pull"]},"recipient":"0xD96A…3D6d"}`.

`x-payment-amount: $0.002` is also set as a convenience. The challenge is authoritative:
take `amount`, `payTo`, `asset`, `network` from it, never from memory.

## Step 2 — pay and retry

### x402 (Base or Solana USDC)

Use the v2 SDKs; they read the 402, pick a network you configured, sign the USDC
authorization, and retry with `PAYMENT-SIGNATURE`. Working files in
`oblique-markets/oblique-examples`:

| Client | File | Run |
|---|---|---|
| TypeScript, `@x402/fetch` + viem | `examples/typescript/x402-fetch/index.ts` (buys `/api/v1/paid/time`, $0.01) | `npm install && npm start` |
| TypeScript, Vercel AI SDK `tool()` | `examples/typescript/vercel-ai-tool/bazaar-pulse-tool.ts` (buys `bazaar-pulse`) | `npm install && npm start` |
| Python, `x402[requests,evm]` | `examples/python/requests/pay_for_time.py` | `pip install -r requirements.txt && python pay_for_time.py` |
| Python, LangChain `@tool` | `examples/python/langchain-tool/bazaar_pulse_tool.py` | `pip install -r requirements.txt && python bazaar_pulse_tool.py` |

All four read a `PRIVATE_KEY` env var for a Base wallet holding a little USDC and set an
explicit per-payment ceiling so a mispriced challenge fails instead of spending. Use a
dedicated, thinly funded wallet. Note the SDK generation: x402 **v2** (`@x402/fetch` 2.x,
`x402` 2.x on PyPI, CAIP-2 network ids, `PAYMENT-REQUIRED`/`PAYMENT-RESPONSE` headers). The
v1 packages (`x402-fetch` 1.x, `X-PAYMENT` header) are deprecated and will not match.

Python sketch (mirrors `pay_for_time.py`):

```python
import os
from eth_account import Account
from x402 import SchemeRegistration, prefer_network, x402ClientConfig, x402ClientSync
from x402.http.clients.requests import x402_requests
from x402.mechanisms.evm.exact import ExactEvmScheme
from x402.mechanisms.evm.signers import EthAccountSigner

signer = EthAccountSigner(Account.from_key(os.environ["PRIVATE_KEY"]))
config = x402ClientConfig(
    schemes=[SchemeRegistration(network="eip155:*", client=ExactEvmScheme(signer=signer))],
    spend_controls={"max_amount_per_payment": "$0.05"},   # ceiling: a mispriced quote fails, not spends
    policies=[prefer_network("eip155:8453")],             # Base; register x402.mechanisms.svm.exact for Solana
)
session = x402_requests(x402ClientSync.from_config(config))  # requests.Session: 402 → sign → retry
r = session.get("https://api.oblique.markets/api/v1/paid/base-gas-price", timeout=30)
r.raise_for_status()
print(r.json(), r.headers.get("PAYMENT-RESPONSE"))            # JSON result + base64 settlement receipt
```

(`pip install "x402[requests,evm]>=2.20.0"`; identical to `pay_for_time.py`.)

### MPP / Tempo

The MPP credential is `Authorization: Payment <base64url JSON>` where the JSON is
`{"challenge":{…echoed WWW-Authenticate params…},"payload":{…tempo-specific signed
transfer…}}` (spec: `https://paymentauth.org/draft-httpauth-payment-00.txt`, §5.2). The
`mppx` client builds it for you:

```ts
import { privateKeyToAccount } from 'viem/accounts'
import { Mppx, tempo } from 'mppx/client'          // npm install mppx viem
Mppx.create({ methods: [tempo({ account: privateKeyToAccount(process.env.PRIVATE_KEY) })] })
// installs a payment-aware fetch: 402 → sign Tempo charge → retry with Authorization: Payment
const r = await fetch('https://api.oblique.markets/api/v1/paid/bazaar-pulse')
```

A successful MPP response carries `Payment-Receipt` (base64url JSON). Docs: `https://mpp.dev`
(Tempo charge: `/payment-methods/tempo/charge`).

## Step 3 — read the result

200 with `application/json`. Shapes are in `openapi.json` and in the challenge's
`extensions.bazaar.info.output.example`. Payment failures come back as a fresh 402 (x402 puts
the reason in the body `error`; MPP uses RFC 9457 problem details). A 4xx other than 402 with
a valid payment means the input was rejected (check the schema) — no charge is settled.

## When to use which cheap route

Prices from the live catalogue on 2026-08-27. GET routes take query params; POST routes take
JSON bodies. Every one is also a paid MCP tool (`bazaar_pulse`, `base_gas_price`, …).

| Route | Price | Use it when you need… | Input |
|---|---|---|---|
| `GET /api/v1/paid/bazaar-pulse` | $0.002 | the x402 Bazaar's latest daily snapshot: totals, top services by settled calls/payers, networks | none |
| `GET /api/v1/paid/bazaar-price-stats` | $0.002 | how Bazaar listings are priced: min/p25/p50/p75/p90/max, USD bands, per-network medians | `?network=base` or `solana` (optional) |
| `GET /api/v1/paid/base-gas-price` | $0.002 | current Base gas price + EIP-1559 base fee (wei and gwei) with block number | none |
| `GET /api/v1/paid/base-block-number` | $0.002 | current Base mainnet block height from redundant public RPCs | none |
| `GET /api/v1/paid/base-usdc-balance` | $0.003 | a wallet's USDC balance on canonical Base USDC (atomic + formatted) | `?address=0x…` (40 hex) |
| `GET /api/v1/paid/base-tx-status` | $0.003 | success/revert, block, confirmations, gas used, effective gas price of a Base tx | `?hash=0x…` (64 hex) |
| `GET /api/v1/paid/x402-facilitator-health` | $0.003 | whether the x402 rail is up: live probes of Dexter `/supported` and Coinbase CDP with status + latency | none |
| `POST /api/v1/paid/web-extract` | $0.03 | one page as JSON: url, title, meta description, cleaned text, timestamp | `{"url":"https://…"}` |
| `POST /api/v1/paid/sentiment` | $0.05 | sentiment of a text block or of current coverage of a topic | `{"query":"…"}` per OpenAPI; the challenge also advertises `{"text":…}` / `{"topic":…}` |
| `POST /api/v1/paid/mpp-route` | $0.01 | a ranked top-3 of catalogued services for a natural-language task, with prices, payment methods and MCP schemas | `{"task":"…","price_cap":0.05,"preferred_chain":"base\|solana\|tempo"}` (`task` required) |

Other frequently useful routes: `time` / `echo` ($0.01, the smallest end-to-end payment
test), `crypto-price` ($0.004), `x402-endpoint-verify` ($0.02, lint someone else's 402),
`settlement-verify` ($0.01, prove a Base USDC settlement landed), `inference` (OpenRouter
proxy; `$1.00` maximum on Base under the `upto` scheme, `$0.01` fixed on Solana; models at the
free `GET /api/v1/models`). The full list with prices is in
[references/catalog.md](references/catalog.md).

## Rules of thumb

- Fetch the quote first (free) and compare `amount` against your ceiling before paying.
- Snapshot-based Bazaar routes update once a day; do not re-buy the same day expecting change.
- Prefer Base for `exact` payments (both facilitators cover it); Solana needs the fee-payer the
  challenge names in `extra.feePayer`.
- `scripts/quote.sh <route>` prints the decoded quote for any route without paying.
- The free observatory at `https://remote.observer` (see the `remote-observer` skill) already
  answers the daily Bazaar diff and provider ranking at no cost — pay here for the fuller
  paid variants (`bazaar-trending`, `bazaar-seller-rank`, `bazaar-market-report`, …) or for
  non-market routes.
