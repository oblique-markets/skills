---
name: x402-bazaar-research
description: Answer "what sells in the x402 economy" questions with oblique.markets market-data routes built from daily full-catalogue snapshots of the x402 Bazaar — bazaar-pulse, bazaar-delta, bazaar-trending, bazaar-new-listings, bazaar-category-heat, bazaar-seller-rank, bazaar-price-stats, bazaar-listing-lint, bazaar-market-report ($0.002–$0.50 per call, paid over x402 or MPP). Use when an agent needs settled-demand evidence (calls_30d, payers_30d, the ≥5 payers × ≥5 calls/payer organic rule), price benchmarks, category heat, seller leaderboards, or listing quality before choosing what to buy or what to sell.
license: MIT
metadata:
  author: oblique-markets
  version: "1.0.0"
  homepage: https://oblique.markets
---

# Researching the x402 Bazaar with oblique.markets

The x402 Bazaar is Coinbase CDP's discovery index of x402-paid resources
(`https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources`). Oblique snapshots the
**full catalogue every day** (since July 2026), stores it, and sells queries over the
snapshots. Every count below is of real rows, diffed by resource URL — not an estimate.

Payment: every route is under `https://api.oblique.markets/api/v1/paid/` and answers 402
first; pay with x402 (USDC on Base `eip155:8453` or Solana) or MPP/Tempo and retry. The
`oblique-paid-endpoints` skill covers the payment loop and worked clients
(`https://github.com/oblique-markets/oblique-examples`). Read any quote for free with
`curl -si <url>`; the 402 body's `extensions.bazaar.info.output.example` shows the response
shape before you pay. Each route is also a tool on `https://api.oblique.markets/mcp`.

## The two fields that matter

The Bazaar attaches a `quality` block to each listing: **`quality.l30DaysUniquePayers`**
(distinct wallets that settled a payment to that resource in the last 30 days) and
**`quality.l30DaysTotalCalls`** (settled calls in the same window). Oblique's routes surface
them as **`payers_30d`** and **`calls_30d`**, per listing, per service (listings grouped by
name), per seller address, per category and per network. They come from the facilitator's
settlement record, so they measure paid demand — listing a resource costs nothing and proves
nothing.

**Organic-demand rule.** Treat a listing as having real, repeat demand only if
`payers_30d >= 5` **and** `calls_30d / payers_30d >= 5`. One wallet hammering an endpoint is
one integration; five distinct wallets each coming back five times is a market. Everything
below that bar is noise from catalogue-sweep bots that buy each listing once (on
2026-08-27 the observer counted 489,703 price-reading challenges against 62 paid calls on one
shop). `bazaar-market-report` publishes the count of listings that clear the payer half of
the rule as `engaged_listings` (>= 5 unique 30d payers); apply the calls-per-payer half
yourself from `calls_30d` and `payers_30d`.

Prices are in USDC atomic units (`amount_atomic`, 6 decimals: `5000` = $0.005).

## Routes, prices, and one example each

Prices read from `https://oblique.markets/.well-known/x402.json` on 2026-08-27. All are
GET; the base URL is `https://api.oblique.markets/api/v1/paid/`. Examples use the Python
x402 session from the `oblique-paid-endpoints` skill (`session = x402_requests(client)`); any
402-aware client works.

| Route | Price | Question it answers |
|---|---|---|
| `bazaar-pulse` | $0.002 | Where is the market today? `totals{resources,sellers,calls_30d}`, `top_services[] {name,listings,calls_30d,payers_30d}`, `networks[]`, `as_of`. |
| `bazaar-delta` | $0.004 | What changed overnight? `added{count,sample[]}`, `removed{count,sample[]}`, `price_changed{count,sample[{resource,from_atomic,to_atomic}]}` between the two latest snapshots. |
| `bazaar-trending` | $0.003 | Who is gaining? `gainers[]`, `decliners[]`, `new_entrants[]`, each `{name,listings,calls_30d,payers_30d,calls_delta,payers_delta,is_new}` day-over-day. |
| `bazaar-new-listings` | $0.003 | What just listed? Up to 50 `{resource,service_name,network,amount_atomic,seller}` present today and absent yesterday, sorted by 30d calls. |
| `bazaar-category-heat` | $0.003 | Which category has the demand? All listings classified into 9 categories (search/scrape, crypto-data, ai-inference, social-data, verification, compute/browser, agent-tools, enrichment, other) with `{listings,calls_30d,payers_30d,share}`. |
| `bazaar-seller-rank` | $0.003 | Who is earning? Top 25 seller addresses by settled 30d calls: `{seller,listings,calls_30d,payers_30d,top_resource}`. |
| `bazaar-price-stats` | $0.002 | What should I charge / expect to pay? `atomic` and `usd` min/p25/p50/p75/p90/max, USD `bands[] {label,count,share}`, `by_network[] {network,n,median_atomic}`. Optional `?network=base` or `solana`. |
| `bazaar-listing-lint` | $0.01 | Is this listing any good? `?resource=<url>` → `score` 0–100, `findings[]`, `history{snapshots_seen,first_seen,last_seen}`, `live{reachable,is_x402}` from a live SSRF-guarded probe plus snapshot history. |
| `bazaar-market-report` | $0.50 | The whole picture in one JSON: totals, price percentiles and bands, network split, top 15 services by calls and by payers, top 10 sellers, new entrants, movers, `engaged_listings`. |

```python
BASE = "https://api.oblique.markets/api/v1/paid/"
pulse    = session.get(BASE + "bazaar-pulse").json()                                   # $0.002
delta    = session.get(BASE + "bazaar-delta").json()                                   # $0.004
trend    = session.get(BASE + "bazaar-trending").json()                                # $0.003
fresh    = session.get(BASE + "bazaar-new-listings").json()                            # $0.003
heat     = session.get(BASE + "bazaar-category-heat").json()                           # $0.003
sellers  = session.get(BASE + "bazaar-seller-rank").json()                             # $0.003
prices   = session.get(BASE + "bazaar-price-stats", params={"network": "base"}).json() # $0.002
lint     = session.get(BASE + "bazaar-listing-lint",
                       params={"resource": "https://x402.shizu.me/gas"}).json()        # $0.01
report   = session.get(BASE + "bazaar-market-report").json()                           # $0.50

organic = [s for s in pulse["top_services"]
           if s["payers_30d"] >= 5 and s["calls_30d"] >= 5 * s["payers_30d"]]
```

Same calls with curl and a wallet-holding client, e.g. `mppx`/`@x402/fetch`, or as MCP
tools `bazaar_pulse`, `bazaar_delta`, `bazaar_trending`, `bazaar_new_listings`,
`bazaar_category_heat`, `bazaar_seller_rank`, `bazaar_price_stats`, `bazaar_listing_lint`,
`bazaar_market_report` on `https://api.oblique.markets/mcp`.

## Recipes

**"What actually sells?"** — `bazaar-pulse` (or `bazaar-market-report` for depth) → apply
the organic rule to `top_services` → cross-check winners with `bazaar-listing-lint` (a high
`score` and `price_stable` history means the demand is not an artefact of a repricing).

**"Is X a crowded category?"** — `bazaar-category-heat`: compare `listings` (supply) with
`payers_30d` (demand) per category; a category with high `share` of listings and low payers
is where one-shot sweep traffic hides.

**"Who are the winners' operators?"** — `bazaar-seller-rank` gives the address and
`top_resource`; feed `top_resource` to `bazaar-listing-lint` and to the free
`find_provider` tool on `https://remote.observer/mcp`.

**"What price is normal?"** — `bazaar-price-stats` `usd.p50` (median) and `bands`. Compare
your candidate price with `by_network` medians; Base and Solana medians differ.

**"What moved since yesterday?"** — `bazaar-delta` for counts and samples,
`bazaar-trending` for the demand side (`calls_delta`, `payers_delta`), `bazaar-new-listings`
for the supply side.

## Caveats

- Snapshots are daily; `as_of` and `compared_to` tell you which days you are looking at.
  Re-buying within the same day returns the same snapshot.
- `calls_30d` / `payers_30d` are the Bazaar's reported values; listings with no `quality`
  block count as 0. Absence is missing evidence, not a bad review.
- A `service_name` can be `null` in the raw catalogue; per-service groupings use the name as
  reported, so unnamed resources fall into the per-resource views (`new-listings`, `delta`,
  `listing-lint`).
- Free alternatives for the cheapest questions: the `remote-observer` skill's `bazaar_pulse`
  (daily diff) and `find_provider` (30-day ranking by `payers_30d`) cost nothing.
