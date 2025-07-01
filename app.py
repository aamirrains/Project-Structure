
from flask import Flask, request, jsonify
import requests
import openai

app = Flask(__name__)

# Replace these with your actual keys
VERIFY_TOKEN = "my_verification_token"
WHATSAPP_TOKEN = "your_whatsapp_cloud_api_token"
OPENAI_API_KEY = "your_openai_key"
PHONE_NUMBER_ID = "your_phone_number_id_from_meta"

openai.api_key = OPENAI_API_KEY

@app.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                return challenge, 200
            else:
                return 'Verification failed', 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            text = message['text']['body']
            sender_id = message['from']

            # Get response from OpenAI
            gpt_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": text}]
            )
            reply = gpt_response.choices[0].message['content'].strip()

            # Send message back via WhatsApp
            url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": sender_id,
                "type": "text",
                "text": {"body": reply}
            }
            requests.post(url, headers=headers, json=payload)

        except Exception as e:
            print("Error:", e)

        return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
