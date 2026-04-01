import requests
import time

# 🔑 KEYS
SERP_API_KEY = "TU_SERPAPI_KEY"
OPENAI_API_KEY = "TU_OPENAI_KEY"
SLACK_WEBHOOK = "TU_SLACK_WEBHOOK"

# 🔍 QUERIES (afinadas)
queries = [
    "subvenciones startups IA España convocatoria",
    "EU funding AI startups open call",
    "CDTI ayudas innovación tecnológica empresas plazo abierto",
]

# 🧠 ANALISIS IA
def analyze_with_openai(title, snippet):
    prompt = f"""
    Analiza si esta ayuda encaja para:

    Startup B2B SaaS de IA / data infra (Narratio)

    Debe cumplir:
    - Empresa privada
    - Tecnología / innovación
    - Escalable

    Descarta:
    - ONGs
    - investigación académica

    Resultado:
    HIGH / MEDIUM / LOW + motivo

    Texto:
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

# 🔍 BUSCADOR SERPAPI
def search(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "num": 5
    }

    res = requests.get(url, params=params).json()
    return res.get("organic_results", [])

# 💬 SLACK
def send_to_slack(message):
    requests.post(SLACK_WEBHOOK, json={"text": message})

# 🚀 RUN
def run():
    for query in queries:
        results = search(query)

        for r in results:
            title = r.get("title")
            link = r.get("link")
            snippet = r.get("snippet", "")

            analysis = analyze_with_openai(title, snippet)

            if "HIGH" in analysis or "MEDIUM" in analysis:
                message = f"""
🚨 NUEVA AYUDA DETECTADA

{title}

{analysis}

{link}
"""
                send_to_slack(message)

# 🔁 LOOP
if __name__ == "__main__":
    while True:
        run()
        time.sleep(86400)  # cada 24h
