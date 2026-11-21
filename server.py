import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(BASE_DIR, "cosbatchi_knowledge.json")

PORT = int(os.environ.get("PORT", 8765))


def load_knowledge():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Knowledge error:", e)
        return {}


class COSBATCHIHandler(BaseHTTPRequestHandler):

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, status, data):
        response = json.dumps(
            data, ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_cors()
        self.send_header(
            "Content-Type", "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/health"):
            self.send_json(200, {
                "status": "COSBATCHI ONLINE",
                "version": "1.2"
            })
        else:
            self.send_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path != "/ask":
            self.send_json(404, {"error": "Not Found"})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            request = json.loads(body.decode("utf-8"))
            question = request.get("question", "").strip().lower()

            knowledge = load_knowledge()

            answer = knowledge.get(
                question,
                "لا أعرف هذه الإجابة بعد. علّمني إياها."
            )

            self.send_json(200, {"answer": answer})

        except Exception as error:
            print("ERROR:", error)
            self.send_json(400, {"error": str(error)})

    def log_message(self, format, *args):
        print("COSBATCHI:", args[0])


server = HTTPServer(("0.0.0.0", PORT), COSBATCHIHandler)

print("COSBATCHI SERVER 1.2")
print("Server is running on port", PORT)

server.serve_forever()
        
