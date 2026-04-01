import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 🔐 KEYS
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]

CHANNEL_ID = "C0AQBDG19EY"  # cambia si quieres


# 🔎 SCRAPING (simple de momento)
def get_opportunities():
    url = "https://www.cdti.es/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    ayudas = []

    for h in soup.find_all("h2")[:5]:
        texto = h.text.strip()
        if texto:
            ayudas.append({
                "titulo": texto,
                "descripcion": texto
            })

    return ayudas


# 🧠 IA → ANALIZA
def analyze_with_ai(ayuda):
    prompt = f"""
Evalúa esta ayuda para una startup B2B de IA.

Devuelve EXACTAMENTE:
Score: X/10
Motivo: breve

Título: {ayuda['titulo']}
Descripción: {ayuda['descripcion']}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# 🚀 SLACK
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


# 🔥 MAIN PIPELINE
if __name__ == "__main__":
    ayudas = get_opportunities()

    resultados = []

    for ayuda in ayudas:
        analysis = analyze_with_ai(ayuda)

        # filtro básico
        if any(x in analysis for x in ["8/10", "9/10", "10/10"]):
            resultados.append(f"{ayuda['titulo']}\n{analysis}")

    if resultados:
        mensaje = "\n\n---\n\n".join(resultados)
        send_to_slack(f"🚀 *Funding Radar*\n\n{mensaje}")
