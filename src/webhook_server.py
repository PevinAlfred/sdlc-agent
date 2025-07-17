from flask import Flask, request, jsonify
from src.orchestrator import orchestrate_pipeline
import hmac
import os

app = Flask(__name__)
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# Optional: verify GitHub webhook signature
def verify_signature(payload, signature):
    if not GITHUB_WEBHOOK_SECRET:
        return True
    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=payload, digestmod='sha256')
    expected = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route("/webhook", methods=["POST"])
def github_webhook():
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 403
    event = request.headers.get('X-GitHub-Event', '')
    if event == "pull_request":
        pr_data = request.json.get("pull_request", {})
        orchestrate_pipeline(pr_data)
        return jsonify({"status": "orchestrator triggered"})
    return jsonify({"status": "ignored", "event": event})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
