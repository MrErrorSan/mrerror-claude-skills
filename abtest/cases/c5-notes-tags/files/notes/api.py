"""The HTTP API: GET /notes[?archived=1], POST /notes, POST /notes/<id>/archive."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import store


class Handler(BaseHTTPRequestHandler):
    conn = None

    def _send(self, status: int, payload) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _owner(self):
        return self.headers.get("X-User")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/notes" or not self._owner():
            return self._send(404, {"error": "not found"})
        query = parse_qs(url.query)
        archived = query.get("archived", ["0"])[0] == "1"
        self._send(200, store.list_notes(self.conn, self._owner(), archived=archived))

    def do_POST(self):
        owner, parts = self._owner(), urlparse(self.path).path.strip("/").split("/")
        if not owner:
            return self._send(401, {"error": "no user"})
        if parts == ["notes"]:
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            note_id = store.add_note(self.conn, owner, data["title"], data.get("body", ""))
            return self._send(201, {"id": note_id})
        if len(parts) == 3 and parts[0] == "notes" and parts[2] == "archive":
            ok = store.archive_note(self.conn, owner, int(parts[1]))
            return self._send(200 if ok else 404, {"archived": ok})
        self._send(404, {"error": "not found"})


def main() -> None:
    Handler.conn = store.connect()
    ThreadingHTTPServer(("127.0.0.1", 8040), Handler).serve_forever()


if __name__ == "__main__":
    main()
