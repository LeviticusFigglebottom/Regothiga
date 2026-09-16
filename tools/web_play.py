#!/usr/bin/env python3
"""Play Vespergard locally.

    python3 play.py        then open http://127.0.0.1:8060

A plain static server is not enough: this is the threaded build, it needs
SharedArrayBuffer, and browsers only grant that to a cross-origin-isolated
page. These are the same three headers the Vercel deployment sends.
"""
import functools, http.server, os, sys, webbrowser

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

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8060
here = os.path.dirname(os.path.abspath(__file__))
url = "http://127.0.0.1:%d/index.html" % port
print("Vespergard at", url, " (Ctrl-C to stop)")
try:
    webbrowser.open(url)
except Exception:
    pass
http.server.ThreadingHTTPServer(
    ("127.0.0.1", port), functools.partial(Handler, directory=here)
).serve_forever()
