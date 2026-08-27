# Full paid catalogue (read from https://oblique.markets/.well-known/x402.json on 2026-08-27)

The catalogue is the source of truth and changes without notice; re-fetch it before relying on a price. Every path is relative to `https://api.oblique.markets`. Each route also exists as a tool on the paid MCP server `https://api.oblique.markets/mcp` (tool names use underscores, e.g. `bazaar_pulse`).

Seller: Oblique Markets — Autonomous M2M execution node: LLM inference, on-chain analytics, web extraction, trading signals. x402 version 2, scheme `exact` unless noted.

| Method | Path | Price | What it returns |
|---|---|---|---|
| GET | `/api/v1/paid/time` | $0.01 | Current server time |
| GET | `/api/v1/paid/echo` | $0.01 | Echo service |
| POST | `/api/v1/paid/web-extract` | $0.03 | Extract structured JSON from a web page: return URL, title, meta description, cleaned text, extraction timestamp, and payment status in a bounded response for agent workflows. |
| POST | `/api/v1/paid/sentiment` | $0.05 | Social media and news sentiment analysis |
| POST | `/api/v1/paid/company-research` | $0.50 | Company research brief with cited sources, business profile, competitors, market signals, and risks |
| POST | `/api/v1/paid/answer-with-sources` | $0.65 | Answer a research question with cited web sources and a concise evidence packet |
| GET | `/api/v1/paid/crypto-price` | $0.004 | Real-time cryptocurrency price data |
| GET | `/api/v1/paid/bazaar-pulse` | $0.002 | Live x402 Bazaar market pulse: trending services, call volumes, new listings, and catalog changes from daily full-catalog snapshots. Machine-readable JSON for agent-market research |
| GET | `/api/v1/paid/listing-triage` | $0.01 | Listing history triage: persistence, price changes, duplicate variants, and buy signal |
| GET | `/api/v1/paid/wallet-spy` | $0.03 | Real-time wallet surveillance — transactions, tokens, DEX swaps, NFTs, risk score |
| POST | `/api/v1/paid/endpoint-task-evaluation` | $0.01 | One bounded x402 endpoint request and payment-flow evaluation |
| POST | `/api/v1/paid/inference` | $1.00 maximum on Base; $0.01 fixed on Solana | LLM inference proxy via OpenRouter (Base upto authorization; Solana fixed-price fallback) |
| POST | `/api/v1/paid/route-task` | $0.01 | Cross-platform x402 task router: ranks endpoints from MPP catalog, Apify actors, and Bazaar listings |
| POST | `/api/v1/paid/agentcore-route` | $0.01 | AgentCore-compatible Oblique seller router: paid ranked top-three shortlist with live health, prices, x402 and MPP rails, MCP schemas, qualified session handoff and receipt binding |
| POST | `/api/v1/paid/agent-readiness-audit` | $1.00 | Verify an AI Agent API’s x402, agent.json, OpenAPI, llms.txt, robots.txt, and MCP discovery surfaces; return a 0–100 score, missing fields, validation findings, and prioritized fixes. |
| POST | `/api/v1/paid/batch-extract` | $0.02 | Run up to 10 public URL JSON extractions in isolated ephemeral compute against caller-supplied JSON Schemas with idempotent reconciliation |
| POST | `/api/v1/paid/batch-url-json` | $0.02 | Prepaid batch of up to 10 HTTPS URL-to-JSON extraction jobs with one idempotent reconciled completion receipt |
| GET | `/api/v1/paid/bazaar-category-heat` | $0.003 | x402 Bazaar category heat map: every listing in the latest daily full-catalogue snapshot classified into 9 categories (search/scrape, crypto-data, ai-inference, social-data, verification, compute/browser, agent-tools, enrichment, other) with listing counts, settled 30d calls, unique payers and listing share per category |
| POST | `/api/v1/paid/bazaar-category-heat-feed` | $0.001079 | Loopable Bazaar category-heat change feed with added, removed, rank-change and price-change records, stable cursors and feed timestamps |
| GET | `/api/v1/paid/bazaar-delta` | $0.004 | x402 Bazaar day-over-day catalogue diff between the two latest daily full-catalogue snapshots: counts and samples of added resources, removed resources, and price changes (from/to atomic amounts) |
| GET | `/api/v1/paid/bazaar-listing-lint` | $0.01 | Quality-score an x402 Bazaar listing (0-100): live SSRF-guarded probe of the resource for a valid 402 challenge with description/output-schema/category/price-floor checks, plus snapshot-history analysis from daily full-catalogue Bazaar snapshots (price churn, delisting) |
| GET | `/api/v1/paid/bazaar-market-report` | $0.50 | Comprehensive x402 Bazaar market report from the latest daily full-catalogue snapshot: marketplace totals, price percentiles and USD bands, network split, top 15 services by settled calls and by unique payers, top 10 sellers, new entrants vs the prior snapshot, top movers by call growth, and the count of listings with real repeat demand (>=5 unique 30d payers) |
| POST | `/api/v1/paid/mpp-route` | $0.01 | MPP-native catalog-first task router: paid top-three shortlist with prices, payment methods, MCP schemas, health metadata and operator source attribution |
| GET | `/api/v1/paid/bazaar-new-listings` | $0.003 | x402 Bazaar new listings: resources that appeared in the latest daily full-catalogue snapshot but were absent the day before — resource URL, service, network, price and seller for up to 50 entrants, sorted by 30d call volume |
| GET | `/api/v1/paid/bazaar-price-stats` | $0.002 | x402 Bazaar price distribution across the latest daily full-catalogue snapshot: min/p25/p50/p75/p90/max in atomic units and USD, USD price bands with shares, and per-network listing counts with median price. Optional ?network= filter. |
| GET | `/api/v1/paid/bazaar-seller-rank` | $0.003 | x402 Bazaar seller leaderboard: top 25 seller addresses ranked by settled 30d calls in the latest daily full-catalogue snapshot, with listing count, unique 30d payers and each seller’s busiest resource |
| GET | `/api/v1/paid/bazaar-trending` | $0.003 | x402 Bazaar trending report: services gaining settled calls and unique payers fastest between the two latest daily snapshots, with decliners and new entrants |
| POST | `/api/v1/paid/evidence/browser` | $0.02 | Run one browser action and return AEP-compatible verified evidence |
| GET | `/api/v1/paid/base-block-number` | $0.002 | Fetch the current Base mainnet block number from redundant public RPCs and return structured JSON with source and freshness metadata. |
| POST | `/api/v1/paid/b402-preflight` | $0.01 | Validate BNB/B402 payment intent freshness, recipient, amount, deadline, fee cap, public BNB balance, and recent activity without custody or payment relay. |
| GET | `/api/v1/paid/base-gas-price` | $0.002 | Current Base gas price: fetch EIP-1559 latest-block base fee and gas price in wei and gwei from redundant public RPCs, with block freshness metadata for transaction planning. |
| GET | `/api/v1/paid/base-tx-status` | $0.003 | Return Base transaction success or revert state, block number, confirmations, gas used, and effective gas price for a transaction hash. |
| POST | `/api/v1/paid/base-transfer-search` | $0.02 | Search bounded Base mainnet ERC-20 transfers by address, direction, asset, counterparty, and time window; return structured transfer records. |
| GET | `/api/v1/paid/base-usdc-balance` | $0.003 | Check a Base wallet’s USDC balance on the canonical Base USDC contract and return structured JSON with atomic and formatted values. |
| GET | `/api/v1/paid/base-usdc-transfer-check` | $0.004 | Verify a Base mainnet transaction moved USDC: decodes all USDC Transfer logs from the receipt and reports settled=true only for a mined, successful tx with at least one transfer |
| POST | `/api/v1/paid/base-wallet-profile` | $0.01 | Accountless Base mainnet wallet profile with native and ERC-20 balances, bounded transfer activity, counterparties, contracts, freshness metadata and evidence hash |
| POST | `/api/v1/paid/classify` | $0.005 | Single-label text classification against 2-20 caller-supplied labels — reply validated against the label set, canonical label returned, 502 instead of hallucinated labels |
| POST | `/api/v1/paid/extract-json` | $0.01 | Extract structured JSON from unstructured text against a caller-supplied JSON Schema — parse-validated with one automatic retry, 502 on failure instead of garbage |
| POST | `/api/v1/paid/fetch-x402` | $0.02 | Fetch and extract content from web pages, handling x402 edge payments automatically |
| POST | `/api/v1/paid/gleif-resolve` | $0.01 | Resolve a legal entity against the public GLEIF registry by LEI, legal name, jurisdiction, registration ID or country, with ranked matches and auditable registry evidence |
| POST | `/api/v1/paid/ghost-bid-audit` | $0.01 | Audit a selected agent offer against rejected affordable alternatives with counterfactual savings, regret, and a tamper-evident receipt. |
| POST | `/api/v1/paid/keyword-extract` | $0.004 | Ranked keyword and named-entity extraction from text, returned as clean JSON arrays — parse-validated with one automatic retry |
| POST | `/api/v1/paid/compile-policy` | $0.02 | Compile a merchant payment policy across x402, MPP, AP2, and card rails from product, risk, authorization, latency, asset, and refund constraints. |
| POST | `/api/v1/paid/pdl-people-enrich` | $0.28 | PDL-shaped people enrichment from supplied identity signals, with normalized person fields and explicit nulls for unavailable third-party attributes |
| POST | `/api/v1/paid/rewrite` | $0.005 | Rewrite text per a natural-language instruction (tone, formality, simplification, shortening) — deterministic flash-model rewriting with hard input/output caps |
| POST | `/api/v1/paid/rep-arkm-transfers` | $0.04 | Arkham-compatible ERC-20 transfers for one Base wallet, backed by the public Base transfer index; priced per bounded request |
| POST | `/api/v1/paid/rep-agi-prepaid-tokens` | $1.00 | Oblique prepaid access token for bounded HTTP-data services, using the Apify-compatible prepaid-token purchase shape; exactly $1 USD per token |
| POST | `/api/v1/paid/rep-cheaptokens-buy` | $0.01 | One bounded OpenAI-compatible chat completion via ZenMux, the honest Oblique equivalent of CheapTokens AI inference access; max 24,000 input characters and 600 output tokens |
| POST | `/api/v1/paid/settlement-verify` | $0.01 | Real on-chain x402 settlement verification on Base mainnet: fetches the transaction receipt via JSON-RPC, decodes USDC Transfer events (payer, payee, amount), reports success/reverted status and confirmation depth, and issues a persistent verification_id receipt |
| POST | `/api/v1/paid/seats-aero-search` | $0.02 | Search award-flight inputs using a stable Seats.aero-compatible request and response shape without claiming unavailable inventory |
| POST | `/api/v1/paid/summarize` | $0.008 | Summarize text as bullet points, a paragraph, or a single line — deterministic flash-model summarization with hard input/output caps |
| GET | `/api/v1/paid/tweets-search` | $0.005 | Search publicly indexed X.com posts with an x402.twit.sh-compatible query shape, returning bounded tweet-like results and source links |
| POST | `/api/v1/paid/x402-endpoint-verify` | $0.02 | Verify and lint a third-party x402 endpoint: probes the URL (SSRF-guarded), confirms it answers with a well-formed HTTP 402 challenge, and reports protocol-conformance findings — accepts[] completeness, CDP Base price floor, PAYMENT-REQUIRED header/body consistency, timeout sanity |
| GET | `/api/v1/paid/x402-facilitator-health` | $0.003 | Live health probe of the two x402 facilitators this service settles through: Dexter /supported coverage (kinds, schemes, networks) and Coinbase CDP reachability with HTTP status and latency |
| GET | `/api/v1/paid/x402-receipt-lookup` | $0.002 | Fetch a previously issued settlement-verify receipt by verification_id: returns the stored on-chain verification result (payer, payee, amount, status, confirmations at verification time) with its creation timestamp |
| POST | `/api/v1/orders` | $0.05 | Extract and synthesize supplied web pages into a cited decision packet with structured JSON findings. |
| POST | `/api/v1/paid/purchase-web-extraction-sample` | $0.01 | Purchase a machine-readable extraction sample from one HTTPS webpage |
| POST | `/api/v1/paid/x401-batch-extract` | $0.02 | Proof-gated batch JSON extraction for up to 10 public URLs in isolated Daytona or Modal compute with reconciled delivery and idempotent retries |
| POST | `/api/v1/paid/oblique-gateway` | $0.001187 | Capped observer-backed gateway over five allowlisted proven sellers; pays selected upstream from a small float, adds a transparent 10% margin, and returns payment reference, delivery and gateway receipt |

## Pay-to addresses (from the same catalogue)

- Base (`eip155:8453`): USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` → `0x970007590aCC5C938cd51345B17AF51B1B40D3Ab`
- Solana (`solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp`): USDC `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` → `GYyTRmt317JafPHXPnM54Fsvsma5GnS9wm6qGMqaykdS`
- Facilitator for both: Coinbase CDP `https://api.cdp.coinbase.com/platform/v2/x402` (Solana settlements also go through Dexter `https://x402.dexter.cash`, per `https://api.oblique.markets/llms.txt`).

Never hard-code these — the 402 challenge for each request carries the authoritative `payTo`, `asset`, `amount` and `network`.
