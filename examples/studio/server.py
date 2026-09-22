"""Loopback-only development host; no extra web framework or notebook dependency."""

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

from .adapter import Studio


ASSETS = Path(__file__).parent / "web"


def serve(port=8765):
    studio = Studio()

    class Handler(BaseHTTPRequestHandler):
        def reply(self, value, status=200, mime="application/json"):
            body = value if isinstance(value, bytes) else json.dumps(value, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
                self.reply({"error": "Use this studio's local address"}, 403)
                return
            if self.path == "/api/state":
                self.reply(studio.state())
            elif self.path == "/api/export":
                self.reply(studio.workspace.to_json().encode())
            elif self.path in ("/", "/studio.js", "/context.js", "/studio.css", "/expressions.js", "/groups.js", "/drafts.js"):
                name = "studio.html" if self.path == "/" else self.path[1:]
                mime = {".html": "text/html", ".js": "text/javascript", ".css": "text/css"}[Path(name).suffix]
                self.reply((ASSETS / name).read_bytes(), mime=mime)
            else:
                self.reply({"error": "Not found"}, 404)

        def do_POST(self):
            # A local study is not a public service. Refuse cross-origin mutations.
            origin = f"http://127.0.0.1:{self.server.server_port}"
            if (self.headers.get("Host") != origin.removeprefix("http://")
                    or self.headers.get("Origin") not in (None, origin)
                    or self.headers.get("Content-Type") != "application/json"):
                self.reply({"error": "Use this studio's local page"}, 403)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                limit = 34 * 1024 * 1024 if self.path == "/api/import" else 1024 * 1024
                if not 0 < size <= limit:
                    raise ValueError("Request exceeds the study's input budget")
                body = json.loads(self.rfile.read(size))
                revision = body["revision"]
                studio.check(revision)
                if self.path == "/api/preview":
                    result = studio.preview(body["command"], revision)
                elif self.path == "/api/commit":
                    result = studio.commit(body["token"], revision)
                elif self.path == "/api/cancel":
                    studio.pending = None
                    result = studio.state()
                elif self.path in ("/api/undo", "/api/redo"):
                    result = studio.history(self.path[5:], revision, body["active"])
                elif self.path == "/api/inspect":
                    result = studio.inspect(body["name"], body["ref"], revision)
                elif self.path == "/api/inspect-driver":
                    result = studio.inspect_ref(body["ref"], revision)
                elif self.path == "/api/groups":
                    result = studio.groups(body["name"], body["by"], revision)
                elif self.path == "/api/import":
                    result = studio.reopen(body["capture"], revision)
                else:
                    self.reply({"error": "Unknown command"}, 404)
                    return
                self.reply(result)
            except (ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError) as error:
                self.reply({"error": str(error)}, 400)

        def log_message(self, *_):
            pass

    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Kaleion studio: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    serve(parser.parse_args().port)
