import os
from openai import OpenAI
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/mydb",
)
client = OpenAI()
conn = psycopg2.connect(DATABASE_URL)

class FAQSearch:
    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS faqs (
                    id SERIAL PRIMARY KEY,
                    question TEXT,
                    answer TEXT,
                    embedding vector(1536)
                )
            """)
        conn.commit()

    def add_faq(self, question: str, answer: str):
        embedding = self._get_embedding(question)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO faqs (question, answer, embedding) VALUES (%s, %s, %s::vector)",
                (question, answer, embedding),
            )
        conn.commit()

    def search(self, query: str, threshold: float = 0.7) -> dict | None:
        query_embedding = self._get_embedding(query)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT question, answer, 1 - (embedding <=> %s::vector) AS similarity
                FROM faqs
                WHERE 1 - (embedding <=> %s::vector) > %s
                ORDER BY embedding <=> %s::vector
                LIMIT 1
            """, (query_embedding, query_embedding, threshold, query_embedding))
            row = cur.fetchone()
            if row:
                return {"question": row[0], "answer": row[1], "similarity": row[2]}
        return None

    def _get_embedding(self, text: str) -> str:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return str(response.data[0].embedding)

# Usage
faq = FAQSearch()
faq.add_faq("How do I cancel my subscription?", "Go to Settings > Billing > Cancel")
faq.add_faq("What payment methods do you accept?", "We accept Visa, Mastercard, PayPal")

result = faq.search("I want to stop paying")
if result:
    print(f"Q: {result['question']}")
    print(f"A: {result['answer']}")
    print(f"Confidence: {result['similarity']:.0%}")