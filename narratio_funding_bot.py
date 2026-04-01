import requests
import os

SERP_API_KEY = os.environ.get("SERP_API_KEY")
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

queries = [
    "EIC Accelerator 2026 convocatoria",
    "CDTI NEOTEC 2026 ayudas startups",
    "ENISA financiación startups España"
]

BAD_SOURCES = ["linkedin.com", "twitter.com"]

def search(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "num": 5
    }
    return requests.get(url, params=params).json().get("organic_results", [])


def clean(link):
    return link and not any(b in link for b in BAD_SOURCES)


# 🔥 CORE: PROBABILIDAD REAL
def evaluate(title, snippet):
    text = f"{title} {snippet}".lower()

    # default
    prob = 0
    tag = ""
    fit = ""
    urgency = ""

    # 🧠 EIC (muy potente pero difícil)
    if "eic" in text:
        prob = 0.05   # <5% real
        tag = "🔥 ALTA (difícil)"
        fit = "Deeptech + escala + VC-ready"
        urgency = "APLICAR SOLO si narrativa muy sólida"

    # 🧠 CDTI
    elif "cdti" in text or "neotec" in text:
        prob = 0.35
        tag = "🔥 ALTA"
        fit = "Startup tecnológica early-stage"
        urgency = "APLICAR ESTA SEMANA"

    # 🧠 ENISA
    elif "enisa" in text:
        prob = 0.6
        tag = "🟢 ALTA PROBABILIDAD"
        fit = "Complemento financiero"
        urgency = "APLICAR YA (rápido)"

    else:
        return None

    return {
        "tag": tag,
        "prob": prob,
        "fit": fit,
        "urgency": urgency
    }


def format_message(opps):
    message = "🎯 PRIORIDAD SEMANAL\n\n"

    for i, o in enumerate(opps, 1):
        prob_percent = int(o["prob"] * 100)

        message += f"""{i}. {o['title']} ({o['tag']})
Probabilidad: {prob_percent}%
Acción: {o['urgency']}
Fit: {o['fit']}
Link: {o['link']}

"""

    return message


def run():
    opportunities = []

    for q in queries:
        results = search(q)

        for r in results:
            title = r.get("title", "")
            link = r.get("link", "")
            snippet = r.get("snippet", "")

            if not clean(link):
                continue

            eval_data = evaluate(title, snippet)
            if not eval_data:
                continue

            opportunities.append({
                "title": title,
                "link": link,
                **eval_data
            })

    # 🔥 ordenar por probabilidad REAL
    opportunities = sorted(opportunities, key=lambda x: x["prob"], reverse=True)

    # 🔥 top 3 → foco semanal
    top = opportunities[:3]

    if top:
        message = format_message(top)
        requests.post(SLACK_WEBHOOK, json={"text": message})


if __name__ == "__main__":
    run()
