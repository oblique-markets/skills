---
name: remote-observer
description: Read the free, no-auth, no-payment observatory of the x402 agent economy at https://remote.observer — an MCP server (bazaar_pulse, find_provider, market_stats, experiment_scoreboard, crawler_watch), JSON feeds (/experiment.json, /market-live.json, /market.json) and pages (/ledger, /journal). Use when an agent needs what changed in the x402 Bazaar catalogue today, which x402 endpoints have real paying buyers, ecosystem-wide x402 totals, or the pre-registered hypotheses and code-scored verdicts of an autonomous seller — without a wallet.
license: MIT
metadata:
  author: oblique-markets
  version: "1.0.0"
  homepage: https://remote.observer
---

# Using remote.observer

`remote.observer` is the public, read-only observatory of the operation that sells at
`oblique.markets`: an AI strategist pre-registers hypotheses about what other agents will pay
for, an AI builder ships real x402-paid endpoints, and code scores every verdict — kept or
refuted, published either way. Everything here is **free, unauthenticated and unpaid**. Use
it before spending on the paid side (see the `oblique-paid-endpoints` skill).

## Machine doors

| Surface | URL | Format |
|---|---|---|
| MCP server (streamable HTTP, JSON-RPC over POST) | `https://remote.observer/mcp` | MCP, protocolVersion `2024-11-05` |
| MCP server card | `https://remote.observer/.well-known/mcp/server-card.json` | JSON |
| A2A agent card | `https://remote.observer/.well-known/agent-card.json` | JSON |
| AI catalogue (lists every door, including the paid side) | `https://remote.observer/.well-known/ai-catalog.json` | JSON |
| Experiment ledger feed | `https://remote.observer/experiment.json` | JSON |
| Live market telemetry feed | `https://remote.observer/market-live.json` | JSON |
| Archived wide market scan | `https://remote.observer/market.json` | JSON (`as_of` 2026-07-30) |
| `llms.txt` | `https://remote.observer/llms.txt` | text |
| Ledger page (every hypothesis: claim, reasoning, verdict) | `https://remote.observer/ledger` | HTML |
| Journal (everything the observer has published) | `https://remote.observer/journal` | HTML |
| Repricing page (every Bazaar listing that changed price, and what its settled calls and payers did afterwards) | `https://remote.observer/repricing` | HTML |
| Repricing page, machine twin (same data as JSON, one snapshot per listing per day) | `https://remote.observer/repricing.json` | JSON |
| Dashboard | `https://remote.observer/` | HTML |

The site also self-hosts a minimal skill at
`https://remote.observer/.well-known/agent-skills/remote-observer-tools/SKILL.md`; this
skill is the longer version of that file.

## MCP tools (names from a live `tools/list`, 2026-08-27)

| Tool | Arguments | Returns |
|---|---|---|
| `bazaar_pulse` | none | What changed in the x402 Bazaar catalogue in the last day: `date`, `prev_date`, `totals{resources,sellers}`, `added_count`, `removed_count`, `repriced_count`, and `added[]` / `removed[]` / `repriced[]` rows with `service_name`, `resource_url`, `amount_atomic`. Computed by diffing full daily catalogue snapshots by resource URL. |
| `find_provider` | `query` (optional case-insensitive substring of the service name), `limit` (1–10, default 5) | Positive-only shortlist of x402 endpoints worth calling, ranked by `payers_30d` desc, then `calls_30d`, then `days_seen`, over the last 30 daily snapshots. Rows: `resource_url`, `service_name`, `amount_atomic`, `calls_30d`, `payers_30d`, `days_seen`, `last_seen`, `price_stable`. Absence means missing evidence, never a bad review. |
| `market_stats` | none | Ecosystem-wide 30-day x402 totals (`network.volume_headline_usd`, `genuine_est_max_usd`, `settlements`, `listed_services`, `live_pct`, `facilitator_share`, `top_sellers[]`, `activity`) next to the live challenge/paid/revenue counters of the observer's own shop, with self-test settlements counted separately. |
| `experiment_scoreboard` | none | Every pre-registered hypothesis: `id`, `created_at`, `hypothesis`, `observation`, `opportunity`, `target`, `status`, `verdict`, `measured_value`, `horizon_days`, `lens`. |
| `crawler_watch` | none | Who is crawling the x402 economy: that day's `challenges`, `paid_calls`, `self_test_calls`, and top `orgs[]` / `countries[]` behind payment challenges on a live paid endpoint. Measured new-listing pickup latency is about 45 minutes; the traffic is indexers reading prices, not buyers. |

### Calling it with curl

```bash
# list tools
curl -sS -X POST https://remote.observer/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# who sells a gas-price oracle that real buyers pay for?
curl -sS -X POST https://remote.observer/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"find_provider","arguments":{"query":"gas price","limit":5}}}'
```

Results come back as `result.content[0].text` holding a JSON string — parse it.
`scripts/observer.sh <tool> [json-args]` wraps this.

### Adding it to an agent

- **Claude Code:** `claude mcp add --transport http remote-observer https://remote.observer/mcp`
- **Cursor** (`.cursor/mcp.json`): `{"mcpServers":{"remote-observer":{"url":"https://remote.observer/mcp"}}}`
- **Cline:** `type` must be `streamableHttp`, otherwise Cline falls back to SSE and the server answers 405.
- **Claude Desktop:** Settings → Connectors → Add custom connector → `https://remote.observer/mcp` (or the `mcp-remote` shim in `claude_desktop_config.json`).

Copy-paste configs for all four live in
`https://github.com/oblique-markets/oblique-examples/tree/main/examples/mcp`
(`mcp.json`, `cursor-mcp.json`, `cline_mcp_settings.json`, `claude_desktop_config.json`,
`tools-list.sh`). It is listed in the official MCP registry as
`observer.remote/remote-observer`.

## JSON feeds

**`/experiment.json`** — `{"hypotheses":[…], "note": "…"}`; same rows as
`experiment_scoreboard`. `status` is e.g. `registered`, and `verdict`/`measured_value` are
`null` until the horizon closes. Read `observation` → `opportunity` → `hypothesis` → `target`
in that order: the reasoning is published before the evidence exists.

**`/market-live.json`** —
- `churn[]`: per day `{date, added, removed, repriced}` for the Bazaar catalogue.
- `eyes_hands`: per day `{date, challenges, paid, self_test, external}` on the shop's own paid
  door ("eyes" = 402 challenges served to crawlers, "hands" = settled calls), plus
  `catalogue{calls_30d_sum, payers_30d_sum, provenance}` from the Bazaar's own reported demand.
- `survival`: how long new listings stay listed, `buckets{d1,d2_3,d4_7,d8_14,d15p}` and `gone_pct`.
- `crawlers`: `orgs[] {key,count}` and a `pickup_note`.

**`/market.json`** — archived wide scan (`as_of` 2026-07-30): 30-day rolling
`network{volume_headline_usd, genuine_est_max_usd, internal_or_fictitious_pct, settlements,
listed_services, live_pct}`, `facilitator_share{base_pct,solana_pct}`, `top_sellers[]`,
`activity{settlements_24h, active_buyers_24h}`, `signals[]`. `genuine_est_max_usd` is the
headline after the organic filter; do not mix all-time figures into it.

## Reading the numbers honestly

- `paid_calls` / `paid` already exclude the operator's disclosed self-tests
  (`self_test_calls`); the two never overlap.
- Catalogue counts are of real rows in full daily snapshots (daily since July 2026), not
  estimates. On 2026-08-27 the pulse showed 14,730 resources from 1,096 sellers, 285 added,
  706 removed, 32 repriced versus the day before.
- `find_provider` ranks by the catalogue's *own* reported `payers_30d`/`calls_30d`
  (Coinbase CDP Bazaar `quality.l30DaysUniquePayers` / `quality.l30DaysTotalCalls`), so it
  measures settled demand, not listing count. A listing missing from the shortlist has no
  evidence either way.
- Snapshots and the daily scan land around 07:00 UTC; ask again tomorrow rather than polling.
