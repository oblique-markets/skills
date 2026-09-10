#!/usr/bin/env bash
# Call one free remote.observer MCP tool and print its JSON result.
# Usage: scripts/observer.sh bazaar_pulse
#        scripts/observer.sh find_provider '{"query":"gas price","limit":5}'
#        scripts/observer.sh list            # tools/list
# Requires: curl, python3. No wallet, no auth.
set -euo pipefail
tool="${1:?tool name or 'list'}"; args="${2:-{\}}"
if [ "$tool" = "list" ]; then
  payload='{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
else
  payload="{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$tool\",\"arguments\":$args}}"
fi
curl -sS -m 60 -A "oblique-skills/1.0.1 (remote-observer)" -X POST https://remote.observer/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d "$payload" | python3 -c '
import sys, json
d = json.load(sys.stdin)
if "error" in d:
    print(json.dumps(d["error"], indent=1)); sys.exit(1)
r = d["result"]
if "tools" in r:
    for t in r["tools"]:
        print(t["name"], "-", t.get("description", "").split(" — ")[0][:120])
        print("   args:", json.dumps(t.get("inputSchema", {}).get("properties", {})))
else:
    text = r["content"][0]["text"]
    try:
        print(json.dumps(json.loads(text), indent=1))
    except Exception:
        print(text)
'
