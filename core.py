
import re
import json
import os
import unicodedata

class COSBATCHICore:

    def __init__(self):
        self.knowledge_file = os.path.join(
            os.path.dirname(__file__),
            "cosbatchi_knowledge.json"
        )
        self.knowledge = self.load_knowledge()

    def load_knowledge(self):
        try:
            with open(
                self.knowledge_file,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def normalize(self, text):
        text = text.lower()
        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r"[\u064B-\u065F]", "", text)
        text = text.replace("ـ", "")
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def understand(self, question):
        question = self.normalize(question)

        if not question:
            return {
                "answer": "من فضلك اكتب سؤالك.",
                "confidence": 0
            }

        best_answer = None
        best_score = 0

        for key, answer in self.knowledge.items():
            normalized_key = self.normalize(key)

            if question == normalized_key:
                return {
                    "answer": answer,
                    "confidence": 1.0
                }

            question_words = set(question.split())
            key_words = set(normalized_key.split())

            if not key_words:
                continue

            score = len(
                question_words & key_words
            ) / len(key_words)

            if score > best_score:
                best_score = score
                best_answer = answer

        if best_score >= 0.5:
            return {
                "answer": best_answer,
                "confidence": round(best_score, 2)
            }

        return {
            "answer": "لا أملك معلومات كافية للإجابة عن هذا السؤال بعد.",
            "confidence": 0
        }


COSBATCHI_CORE = COSBATCHICore()
          
