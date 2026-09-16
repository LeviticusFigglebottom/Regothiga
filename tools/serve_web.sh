#!/usr/bin/env bash
# Serves a local web export the way Vercel serves it.
#
# The threaded build needs SharedArrayBuffer, which browsers only hand to a
# cross-origin-isolated page, so a plain `python3 -m http.server` will load the
# engine and then fail. These are the same three headers vercel.json sets, so
# what you see here is what the deployment does.
set -euo pipefail
cd "$(dirname "$0")/.."

DIR="${1:-build/web}"
PORT="${2:-8060}"

if [ ! -f "$DIR/index.html" ]; then
	echo "no export at $DIR — run tools/vercel_build.sh first" >&2
	exit 1
fi

echo "serving $DIR at http://127.0.0.1:$PORT (Ctrl-C to stop)"
python3 - "$DIR" "$PORT" <<'PY'
import functools, http.server, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        super().end_headers()

    def guess_type(self, path):
        if path.endswith(".wasm"):
            return "application/wasm"
        if path.endswith(".pck"):
            return "application/octet-stream"
        return super().guess_type(path)

directory, port = sys.argv[1], int(sys.argv[2])
http.server.ThreadingHTTPServer(
    ("127.0.0.1", port),
    functools.partial(Handler, directory=directory),
).serve_forever()
PY
