import requests

# 🔐 TU WEBHOOK DE SLACK
SLACK_WEBHOOK = "PEGA_AQUI_TU_WEBHOOK"

# 🔎 BÚSQUEDAS
queries = [
    "subvenciones startups España 2026 ENISA CDTI",
    "EIC Accelerator 2026 convocatoria",
    "ayudas startups tecnologicas España abiertas"
]

# 🚫 FILTRO DE LINKS NO RELEVANTES
def clean(link):
    blacklist = ["blog", "medium", "guia", "pdf"]
    return not any(b in link for b in blacklist)

# 🧠 IDENTIFICAR PROGRAMA
def extract_program(title):
    t = title.lower()

    if "enisa" in t:
        return "ENISA"
    if "cdti" in t or "neotec" in t:
        return "CDTI NEOTEC 2026"
    if "eic" in t:
        return "EIC Accelerator Open 2026"

    return None

# 🏛 PRIORIDAD A FUENTE OFICIAL
def is_official(link):
    return any(domain in link for domain in [
        "enisa.es",
        "cdti.es",
        "europa.eu"
    ])

# 🤖 PROBABILIDAD SIMPLE
def evaluate(title, snippet):
    text = (title + " " + snippet).lower()

    if "subvención" in text or "grant" in text:
        return 60
    if "préstamo" in text:
        return 40
    if "europe" in text:
        return 20

    return 10

# 🧾 FORMATO FINAL (TIPO CLAUDE)
def format_message(opps):
    msg = "🔎 Rastreo de ayudas públicas — Semana actual\n\n"
    msg += "Convocatorias abiertas con encaje para Narratio (IA, SaaS B2B, startup, I+D+i, internacionalización):\n\n"

    for i, o in enumerate(opps, 1):

        # descripciones tipo memo
        if o["title"] == "CDTI NEOTEC 2026":
            desc = "Subvención a fondo perdido hasta €325K (70–85% del presupuesto). Startups de base tecnológica <3 años. Apertura marzo/abril — cierre estimado abril/mayo. Concurrencia competitiva."
        elif o["title"] == "ENISA":
            desc = "Préstamo participativo €25K–€1.5M sin avales. Abierta todo el año (FIFO). Fondos propios ≥ importe solicitado."
        elif o["title"] == "EIC Accelerator Open 2026":
            desc = "Grant hasta €2.5M + equity hasta €10M. Short proposal abierta permanentemente. Cut-offs periódicos durante el año."
        else:
            desc = "Convocatoria relevante para startups tecnológicas."

        emoji = "🚨" if o["prob"] >= 50 else ""

        msg += f"{i}. {o['title']} {emoji}\n"
        msg += f"{desc}\n"
        msg += f"{o['link']}\n\n"

    return msg

# 🌐 BÚSQUEDA (SERPAPI)
def search(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": "TU_API_KEY"
    }

    res = requests.get(url, params=params)
    data = res.json()

    return data.get("organic_results", [])

# 🚀 MAIN
def run():
    programs = {}

    for q in queries:
        results = search(q)

        for r in results:
            title = r.get("title", "")
            link = r.get("link", "")
            snippet = r.get("snippet", "")

            if not clean(link):
                continue

            program = extract_program(title)
            if not program:
                continue

            prob = evaluate(title, snippet)

            # deduplicación + prioridad oficial
            if program in programs:
                if is_official(link):
                    programs[program] = {
                        "title": program,
                        "link": link,
                        "prob": prob
                    }
            else:
                programs[program] = {
                    "title": program,
                    "link": link,
                    "prob": prob
                }

    # ordenar por probabilidad
    opportunities = sorted(programs.values(), key=lambda x: x["prob"], reverse=True)

    top = opportunities[:4]

    if top:
        message = format_message(top)

        requests.post(
            SLACK_WEBHOOK,
            json={"text": message}
        )

# ▶️ EJECUTAR
if __name__ == "__main__":
    run()
