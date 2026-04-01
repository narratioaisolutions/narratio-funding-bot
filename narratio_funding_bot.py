import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 🔐 TOKENS
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

CHANNEL_ID = "C0AQBDG19EY"


# 🔎 1. SCRAPING SIMPLE (ejemplo CDTI/EU fake demo)
def get_opportunities():
    url = "https://www.cdti.es/"  # puedes cambiar luego
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    ayudas = []

    for h in soup.find_all("h2")[:5]:
        ayudas.append({
            "titulo": h.text.strip(),
            "descripcion": h.text.strip()
        })

    return ayudas


# 🧠 2. IA → ANALIZA Y PUNTÚA
def analyze_with_ai(ayuda):
    prompt = f"""
Analiza esta ayuda pública para una startup B2B de IA (tipo Narratio).

Devuelve SOLO esto:
Score (1-10)
Razón breve

Ayuda:
Título: {ayuda['titulo']}
Descripción: {ayuda['descripcion']}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ✍️ 3. FORMATEAR MENSAJE
def format_message(results):
    today = datetime.now().strftime("%d/%m/%Y")

    msg = f"*Narratio Funding Radar — {today}*\n\n"

    for r in results:
        msg += f"*{r['titulo']}*\n"
        msg += f"{r['analysis']}\n\n"

    return msg


# 🚀 4. ENVIAR A SLACK
def send_to_slack(message):
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {SLACK_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "channel": CHANNEL_ID,
            "text": message
        }
    )


# ▶️ 5. PIPELINE
if __name__ == "__main__":
    ayudas = get_opportunities()

    resultados = []

    for a in ayudas:
        analysis = analyze_with_ai(a)

        # filtro simple
        if "8" in analysis or "9" in analysis or "10" in analysis:
            resultados.append({
                "titulo": a["titulo"],
                "analysis": analysis
            })

    if resultados:
        msg = format_message(resultados)
        send_to_slack(msg)
