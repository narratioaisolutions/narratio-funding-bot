import os
import requests
from datetime import datetime

# 🔐 Token de Slack desde GitHub Secrets
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]

# 📢 ID del canal (el tuyo ya lo tienes)
CHANNEL_ID = "C0AQBDG19EY"


# 🧠 1. Aquí defines las ayudas (luego lo automatizamos)
def get_opportunities():
    return [
        {
            "name": "EIC Accelerator",
            "deadline": "Junio / Septiembre 2026",
            "link": "https://eic.ec.europa.eu/",
            "fit": "Deeptech + AI + infraestructura → encaje directo Narratio",
            "priority": "🔥 ALTA"
        },
        {
            "name": "CDTI NEOTEC",
            "deadline": "Abril/Mayo 2026",
            "link": "https://www.cdti.es/",
            "fit": "Subvención para startups tecnológicas",
            "priority": "🔥 ALTA"
        },
        {
            "name": "ENISA",
            "deadline": "Abierta",
            "link": "https://www.enisa.es/",
            "fit": "Financiación no dilutiva complementaria",
            "priority": "🟡 MEDIA"
        }
    ]


# ✍️ 2. Formato del mensaje
def format_message(data):
    today = datetime.now().strftime("%d/%m/%Y")

    msg = f"*Narratio Funding Radar — {today}*\n\n"

    for i, d in enumerate(data, 1):
        msg += f"{i}. *{d['name']}* ({d['priority']})\n"
        msg += f"Deadline: {d['deadline']}\n"
        msg += f"Link: {d['link']}\n"
        msg += f"Fit: {d['fit']}\n\n"

    return msg


# 🚀 3. Envío a Slack
def send_to_slack(message):
    response = requests.post(
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

    print(response.json())


# ▶️ 4. Ejecución
if __name__ == "__main__":
    data = get_opportunities()
    message = format_message(data)
    send_to_slack(message)
