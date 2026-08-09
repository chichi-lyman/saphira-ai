import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "saphira_secret_token_123")
GRAPH_API_URL = "https://graph.facebook.com/v19.0"

# Pre-configured sales messaging triggered by keyword matching
AUTOMATED_OFFERS = {
    "default": "Thanks for messaging! Saphira AI here. How can I help you scale your business today?",
    "link": "Here is the direct link to access our newest business tools and automation guides: https://yourdomain.com/checkout",
    "ai": "Looking to deploy custom AI agents for your business? Check out our setup portal here: https://yourdomain.com/ai-agents",
    "price": "Our digital growth packages start at $27. View the complete breakdown here: https://yourdomain.com/pricing"
}

def send_facebook_message(recipient_id, message_text):
    """Sends an automated reply message back to the sender via Meta Graph API."""
    url = f"{GRAPH_API_URL}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    
    response = requests.post(url, params=params, json=payload, headers=headers)
    return response.json()

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta Webhook Verification Endpoint."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print(" Webhook verified successfully with Meta!")
        return challenge, 200
    else:
        print(" Webhook verification failed. Invalid token.")
        return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def handle_webhook_events():
    """Processes inbound DMs and triggers automated responses."""
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                message = messaging_event.get("message", {})
                message_text = message.get("text", "").lower()

                if sender_id and message_text:
                    print(f" Inbound DM received from {sender_id}: '{message_text}'")

                    # Keyword routing logic
                    reply = AUTOMATED_OFFERS["default"]
                    for keyword, offer_text in AUTOMATED_OFFERS.items():
                        if keyword in message_text and keyword != "default":
                            reply = offer_text
                            break

                    # Send reply
                    res = send_facebook_message(sender_id, reply)
                    print(f" Sent response to {sender_id}. Status: {res}")

        return "EVENT_RECEIVED", 200
    
    return "Not Found", 404

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f" Saphira DM Webhook Server running on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
