import requests
import os

# 🔑 KEYS (desde GitHub Secrets)
SERP_API_KEY = os.environ.get("SERP_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

# 🔍 QUERIES
queries = [
    "subvenciones startups IA España convocatoria",
    "EU funding AI startups open call",
    "CDTI ayudas innovación tecnológica empresas plazo abierto"
]

# 🔍 BUSCAR CON SERPAPI
def search(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "num": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("organic_results", [])


# 🧠 ANALIZAR CON OPENAI
def analyze(title, snippet):
    prompt = f"""
    Evalúa si esta ayuda encaja para una startup B2B SaaS de IA (Narratio).

    HIGH = muy relevante
    MEDIUM = interesante
    LOW = no relevante

    {title}
    {snippet}
    """

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
        )

        data = response.json()

        if "choices" not in data:
            return "LOW - error API"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"LOW - error {e}"


# 💬 ENVIAR A SLACK
def send_to_slack(message):
    if not SLACK_WEBHOOK:
        raise ValueError("❌ SLACK_WEBHOOK no definido")

    requests.post(SLACK_WEBHOOK, json={"text": message})


# 🚀 MAIN
def run():
    for query in queries:
        results = search(query)

        for r in results:
            title = r.get("title")
            link = r.get("link")
            snippet = r.get("snippet", "")

            analysis = analyze(title, snippet)

            # 👉 FILTRO
            if "LOW" in analysis:
                continue

            message = f"""
🚨 AYUDA DETECTADA

{title}

{analysis}

{link}
"""

            send_to_slack(message)


if __name__ == "__main__":
    run()
