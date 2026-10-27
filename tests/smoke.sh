#!/bin/sh
# Smoke tests: --help for every script, then qask and tps.py against a local stub server. No VM or model needed.
set -e
here=$(cd "$(dirname "$0")/.." && pwd)
for s in rig-up rig-down rig-status provision fetch-models qask rig-queue; do
  RIG_VM=127.0.0.1 "$here/bin/$s" --help >/dev/null || { echo "FAIL --help $s"; exit 1; }
done
for s in tps.py bench.py; do python3 "$here/bin/$s" --help >/dev/null || { echo "FAIL --help $s"; exit 1; }; done
for s in "$here"/bin/* "$here"/vm/*.sh; do
  [ -f "$s" ] || continue
  if head -1 "$s" | grep -q python; then python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$s"; else bash -n "$s"; fi || { echo "FAIL syntax $s"; exit 1; }
done
tmp=$(mktemp -d); trap 'kill $pid 2>/dev/null; rm -rf "$tmp"' EXIT
cat >"$tmp/stub.py" <<'P'
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        b = json.dumps({"choices": [{"message": {"content": "hello from stub"}}], "usage": {"completion_tokens": 3}}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass
s = HTTPServer(("127.0.0.1", 0), H); print(s.server_port, flush=True); s.serve_forever()
P
python3 "$tmp/stub.py" >"$tmp/port" & pid=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -s "$tmp/port" ] && break; sleep 0.3; done
url=http://127.0.0.1:$(cat "$tmp/port")
[ "$(RIG_DRIVER=$url "$here/bin/qask" hi)" = "hello from stub" ] || { echo "FAIL qask"; exit 1; }
RIG_DRIVER=$url python3 "$here/bin/tps.py" | grep -q "OK" || { echo "FAIL tps"; exit 1; }
echo "smoke ok"
