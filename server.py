import os
import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 8765))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class COSBATCHIHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json({"status": "ok"})

    def do_GET(self):
        if self.path in ["/", "/health"]:
            self.send_json({
                "status": "COSBATCHI ONLINE",
                "version": "2.0"
            })
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path != "/ask":
            self.send_json({"error": "Not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > 20000:
                self.send_json({"error": "Invalid request"}, 400)
                return

            data = json.loads(self.rfile.read(length))
            question = str(data.get("question", "")).strip()

            if not question:
                self.send_json({"answer": "اكتب سؤالك أولاً."}, 400)
                return

            if not GROQ_API_KEY:
                self.send_json({
                    "answer": "مفتاح الذكاء الاصطناعي غير مضبوط في الخادم."
                }, 500)
                return

            payload = {
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {
                        "role": "system",
                        "content": "أنت COSBATCHI AI، مساعد ذكي. أجب باللغة العربية بوضوح واحترافية، وساعد المستخدم."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "temperature": 0.7,
                "max_completion_tokens": 800
            }

            request = urllib.request.Request(
                GROQ_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": "Bearer " + GROQ_API_KEY,
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))

            answer = result["choices"][0]["message"]["content"]

            self.send_json({"answer": answer})

        except urllib.error.HTTPError as error:
            print("Groq HTTP error:", error.code)
            self.send_json({
                "answer": "حدث خطأ في خدمة الذكاء الاصطناعي. حاول مرة أخرى."
            }, 502)

        except Exception as error:
            print("Server error:", str(error))
            self.send_json({
                "answer": "حدث خطأ في الخادم. حاول مرة أخرى."
            }, 500)


print("COSBATCHI SERVER 2.0")
print("Server is running on port", PORT)

HTTPServer(("0.0.0.0", PORT), COSBATCHIHandler).serve_forever()
            
