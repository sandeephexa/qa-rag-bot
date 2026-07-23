import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def classify_ticket(ticket_description: str) -> dict:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "system", "content":"""Classify support tickets into categories.
                Return JSON with: category, priority, summary
                Categories: billing, technical, account, general
                Priorities: low, medium, high, urgent"""},
        {"role": "user", "content": ticket_description}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

ticket = "I've been charged twice for my subscription this month!"
result = classify_ticket(ticket)
print(result)