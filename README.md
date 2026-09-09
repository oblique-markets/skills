# oblique-markets/skills

[Agent Skills](https://agentskills.io) for the x402 agent economy, published by
[Oblique Markets](https://oblique.markets). Each skill is a `SKILL.md` an agent loads on
demand, written from the live surfaces (every URL, price and field name was read from the
running services on the date stamped inside each file).

```bash
npx skills add oblique-markets/skills            # skills.sh CLI — pick skills interactively
npx skills add oblique-markets/skills --all      # install all three to every detected agent
npx skills add oblique-markets/skills --list     # just list them
```

Hermes Agent: `hermes skills tap add oblique-markets/skills`, then
`hermes skills install oblique-markets/skills/skills/oblique-paid-endpoints` (or any of the
three). The skills pass Hermes's install-time security scan as community skills (verdict
`safe`: no secret reads from the environment, pinned installs, no remote code fetches). The
files are plain agentskills.io `SKILL.md` documents, so any ClawHub-style index or agent that
reads that format (Claude Code, Cursor, Codex, OpenCode, Cline, OpenClaw, …) can use them.
`skills.sh.json` at the root carries the category groupings hubs display.

## Skills

| Skill | What it teaches an agent |
|---|---|
| [`oblique-paid-endpoints`](skills/oblique-paid-endpoints/SKILL.md) | Buying from `https://api.oblique.markets/api/v1/paid/*`: the HTTP 402 loop over x402 (USDC on Base or Solana, `PAYMENT-SIGNATURE`) and MPP/Tempo (`Authorization: Payment`), the discovery surfaces (`x402.json`, `openapi.json`, agent card, paid MCP), worked SDK clients in [oblique-examples](https://github.com/oblique-markets/oblique-examples), and a when-to-use table for thirteen cheap routes. Ships `scripts/buy.py` (a self-contained x402 buyer that settles a real Base USDC payment, with a spend ceiling), `scripts/quote.sh` (decode any 402 without paying), `scripts/catalog.py` (print today's catalogue) and a 65-route price snapshot. |
| [`remote-observer`](skills/remote-observer/SKILL.md) | The free, no-auth observatory at [remote.observer](https://remote.observer): the MCP server's five tools (`bazaar_pulse`, `find_provider`, `market_stats`, `experiment_scoreboard`, `crawler_watch`), the JSON feeds (`/experiment.json`, `/market-live.json`, `/market.json`), the ledger and journal pages, and how to read the numbers. Includes `observer.sh`. |
| [`x402-bazaar-research`](skills/x402-bazaar-research/SKILL.md) | Answering "what sells in the x402 economy" with the nine `bazaar-*` market-data routes ($0.002–$0.50): what `l30DaysUniquePayers` / `calls_30d` mean, the organic-demand rule (≥5 payers and ≥5 calls per payer), one example call per route, and recipes. |

## Try the paid flow in one minute

```bash
git clone https://github.com/oblique-markets/skills && cd skills/skills/oblique-paid-endpoints
pip install requests==2.32.5 eth-account==0.13.7
scripts/buy.py bazaar-pulse --quote-only                 # free: read the $0.002 quote
printf '%s' '0xYOUR_PRIVATE_KEY' > buyer.key             # a dedicated Base wallet with a little USDC
scripts/buy.py bazaar-pulse --key-file buyer.key         # pays $0.002, prints the JSON and the tx hash
```

## Layout

```
skills.sh.json                  category groupings (skills.sh schema; read by hubs)
skills/
  oblique-paid-endpoints/   SKILL.md  references/catalog.md  scripts/buy.py  scripts/quote.sh  scripts/catalog.py
  remote-observer/          SKILL.md  scripts/observer.sh
  x402-bazaar-research/     SKILL.md
```

Prices and catalogue contents drift; the catalogue at
<https://oblique.markets/.well-known/x402.json> is the source of truth and each 402 challenge
is authoritative for the call it quotes. `scripts/catalog.py` regenerates the snapshot.

## Links

- Shop: <https://oblique.markets> · API: <https://api.oblique.markets> · paid MCP: <https://api.oblique.markets/mcp>
- Observatory: <https://remote.observer> · free MCP: <https://remote.observer/mcp>
- Worked clients and MCP configs: <https://github.com/oblique-markets/oblique-examples>
- Field notes: <https://x.com/obliquemarkets>

## License

MIT — see [LICENSE](LICENSE).
