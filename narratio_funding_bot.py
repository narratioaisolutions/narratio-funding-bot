import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
CHANNEL_ID = "C0AQBDG19EY"


def get_opportunities():
    url = "https://www.cdti.es/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    ayudas = []

    for h in soup.find_all("h2")[:5]:
        ayudas.append({
            "titulo": h.text.strip(),
            "descripcion": h.text.strip()
        })

    return ayudas


def analyze_with_ai(ayuda):
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{
            "role": "user",
            "content": f"""
Evalúa esta ayuda para una startup B2B de IA.

Devuelve:
Score (1-10)
Motivo breve

Título: {ayuda['titulo']}
Descripción: {ayuda['descripcion']}
"""
        }]
    )

    return response.choices[0].message.content


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


if __name__ == "__main__":
    ayudas = get_opportunities()

    mensajes = []

    for ayuda in ayudas:
        analysis = analyze_with_ai(ayuda)

        if any(x in analysis for x in ["8", "9", "10"]):
            mensajes.append(f"{ayuda['titulo']}\n{analysis}\n")

    if mensajes:
        texto = "\n---\n".join(mensajes)
        send_to_slack(f"🚀 Funding Radar:\n\n{texto}")
