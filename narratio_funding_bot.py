import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 🔐 KEYS
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]

CHANNEL_ID = "C0AQBDG19EY"


# 🔎 SCRAPING
def get_opportunities():
    print("🔎 Buscando ayudas...")

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

    print(f"✅ Ayudas encontradas: {len(ayudas)}")
    return ayudas


# 🧠 IA
def analyze_with_ai(ayuda):
    print(f"\n🧠 Analizando: {ayuda['titulo']}")

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

    resultado = response.choices[0].message.content

    print("📊 Resultado IA:")
    print(resultado)

    return resultado


# 🚀 SLACK
def send_to_slack(message):
    print("\n🚀 Enviando a Slack...")

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

    print("📡 Respuesta Slack:", response.text)


# 🔥 MAIN
if __name__ == "__main__":
    print("🚀 INICIO FUNDING BOT\n")

    ayudas = get_opportunities()

    resultados = []

    for ayuda in ayudas:
        analysis = analyze_with_ai(ayuda)

        # 🔥 MODO PRUEBA PRO → NO FILTRA NADA
        resultados.append(f"{ayuda['titulo']}\n{analysis}")

    if resultados:
        mensaje = "\n\n---\n\n".join(resultados)

        today = datetime.now().strftime("%d/%m/%Y")

        mensaje_final = f"🚀 Funding Radar TEST — {today}\n\n{mensaje}"

        print("\n📨 MENSAJE FINAL:")
        print(mensaje_final)

        send_to_slack(mensaje_final)

    else:
        print("❌ No hay resultados")
