
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class COSBATCHI(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(
            data, ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_json({
                "name": "COSBATCHI AI",
                "status": "online",
                "version": "1.0"
            })
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path != "/ask":
            self.send_json({"error": "Not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            question = data.get("question", "").strip()

            if not question:
                self.send_json({"error": "Empty question"}, 400)
                return

            self.send_json({
                "answer": "استقبل COSBATCHI سؤالك: " + question,
                "engine": "COSBATCHI CORE"
            })

        except Exception:
            self.send_json({"error": "Invalid request"}, 400)

    def log_message(self, format, *args):
        print("COSBATCHI:", args[0])

port = int(os.environ.get("PORT", 10000))

server = HTTPServer(("0.0.0.0", port), COSBATCHI)

print("COSBATCHI AI SERVER 1.0")
print("Server is running on port", port)

server.serve_forever()
          
