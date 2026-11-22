import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from groq import Groq

PORT = int(os.environ.get("PORT", 8765))
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


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
        if self.path.split("?")[0] in ["/", "/health"]:
            self.send_json({
                "status": "COSBATCHI ONLINE",
                "version": "3.0"
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
                    "answer": "مفتاح Groq غير مضبوط في الخادم."
                }, 500)
                return

            history = data.get("history", [])

            if not isinstance(history, list):
                history = []

            messages = [
                {
                    "role": "system",
                    "content": "أنت COSBATCHI AI، مساعد ذكي. أجب باللغة العربية بوضوح واحترافية، وتذكر سياق المحادثة السابقة."
                }
            ]

            messages += history[-20:]

            messages.append({
                "role": "user",
                "content": question
            })

            client = Groq(
                api_key=GROQ_API_KEY,
                timeout=60
            )

            result = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            answer = result.choices[0].message.content

            self.send_json({"answer": answer})

        except Exception as error:
            print("COSBATCHI ERROR:", repr(error))

            self.send_json({
                "answer": "حدث خطأ في الاتصال: " + str(error)
            }, 502)


print("COSBATCHI SERVER 3.0")
print("Server is running on port", PORT)

HTTPServer(("0.0.0.0", PORT), COSBATCHIHandler).serve_forever()
                                                           
