from flask import Flask, request, jsonify
from src.orchestrator import orchestrate_pipeline
from src.deploy.auto_deployer import auto_deploy
from src.deploy.deployer import deploy_application
import logging
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

    if event == "push":
        try:
            repo = request.json["repository"]["full_name"]
            # ref is like 'refs/heads/main', get the branch name
            ref = request.json.get("ref", "refs/heads/main")
            branch = ref.split("/")[-1]
            script_path = auto_deploy(repo, branch)
            logging.info(f"Deployment script generated and saved at {script_path} for {repo}@{branch}")
            # Execute the deployment script
            deploy_application(script_path)
            return jsonify({"status": "deployment script executed", "script_path": script_path})
        except Exception as e:
            logging.exception("Failed to auto-deploy:")
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ignored", "event": event})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
