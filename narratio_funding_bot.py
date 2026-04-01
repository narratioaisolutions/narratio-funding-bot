import requests

# 🔑 CONFIG (usa GitHub Secrets)
SERP_API_KEY = "${SERP_API_KEY}"
OPENAI_API_KEY = "${OPENAI_API_KEY}"
SLACK_WEBHOOK = "${SLACK_WEBHOOK}"

queries = [
    "subvenciones startups IA España convocatoria",
    "EU funding AI startups open call",
    "CDTI ayudas innovación tecnológica empresas plazo abierto"
]

# 🔍 SERPAPI
def search(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "num": 5
    }
    res = requests.get(url, params=params).json()
    return res.get("organic_results", [])

# 🧠 OPENAI
def analyze(title, snippet):
    prompt = f"""
    Evalúa si esta ayuda encaja para una startup B2B SaaS de IA (Narratio).

    HIGH = muy relevante
    MEDIUM = interesante
    LOW = no relevante

    {title}
    {snippet}
    """

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

    return response.json()["choices"][0]["message"]["content"]

# 💬 SLACK
def send(message):
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

            if "LOW" in analysis:
                continue

            message = f"""
🚨 AYUDA DETECTADA

{title}

{analysis}

{link}
"""
            send(message)

if __name__ == "__main__":
    run()
