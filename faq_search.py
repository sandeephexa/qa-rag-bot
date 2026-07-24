import os
from openai import OpenAI
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sandeepkumarboda@localhost:5432/mydb",
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
        try:
            embedding = self._get_embedding(question)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO faqs (question, answer, embedding)
                    VALUES (%s, %s, %s::vector)
                    """,
                    (question, answer, embedding),
                )

            conn.commit()
            print("Inserted:", question)

        except Exception as e:
            print("Insert failed:", e)
            print(f"Adding FAQ: {question}")

            embedding = self._get_embedding(question)

            print(f"Embedding dimensions: {len(embedding)}")

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO faqs (question, answer, embedding)
                    VALUES (%s, %s, %s::vector)
                    """,
                    (question, answer, embedding),
                )

            conn.commit()
            print("FAQ inserted successfully")
            
            
    def search(self, query: str, threshold: float = 0.45):
        query_embedding = self._get_embedding(query)

        with conn.cursor() as cur:
            cur.execute("""
                SELECT question, answer, similarity
                FROM (
                    SELECT
                        question,
                        answer,
                        1 - (embedding <=> %s::vector) AS similarity
                    FROM faqs
                ) t
                WHERE similarity >= %s
                ORDER BY similarity DESC
                LIMIT 1
            """, (query_embedding, threshold))

            row = cur.fetchone()

        if row is None:
            return None

        return {
            "question": row[0],
            "answer": row[1],
            "similarity": row[2],
        }
        

    def _get_embedding(self, text: str) -> str:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )

        embedding = response.data[0].embedding

        return "[" + ",".join(map(str, embedding)) + "]"
# Usage
faq = FAQSearch()
faq.add_faq("How do I cancel my subscription?", "Go to Settings > Billing > Cancel")
faq.add_faq("What payment methods do you accept?", "We accept Visa, Mastercard, PayPal")

result = faq.search("I want to stop paying")
print(result)
if result:
    print(f"Q: {result['question']}")
    print(f"A: {result['answer']}")
    print(f"Confidence: {result['similarity']:.0%}")