from flask import Flask, request, jsonify
from src.orchestrator import orchestrate_pr_merge_pipeline, orchestrate_branch_push_pipeline
import logging
import hmac
import os
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# GitHub Event Constants
EVENT_PULL_REQUEST = "pull_request"
EVENT_PUSH = "push"
ACTION_CLOSED = "closed"

# Instrument the app with Prometheus metrics. This creates a /metrics endpoint.
metrics = PrometheusMetrics(app)

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

    data = request.json

    if event == EVENT_PULL_REQUEST:
        action = data.get("action")
        pr_data = data.get("pull_request", {})

        # Trigger orchestrator only when a PR is closed and merged into the main branch
        if action == ACTION_CLOSED and pr_data.get("merged") and pr_data.get("base", {}).get("ref") == "main":
            logging.info("PR merged to main, triggering orchestrator.")
            try:
                orchestrate_pr_merge_pipeline(pr_data)
                return jsonify({"status": "orchestrator triggered for merge to main"})
            except Exception as e:
                logging.error(f"Orchestrator pipeline failed: {e}")
                return jsonify({"error": "Orchestrator pipeline failed", "details": str(e)}), 500

        logging.info(f"Ignoring pull_request event (action: {action}, merged: {pr_data.get('merged')}, base_ref: {pr_data.get('base', {}).get('ref')})")
        return jsonify({"status": "ignored", "reason": "not a merge to main"})

    if event == EVENT_PUSH:
        try:
            repo = data["repository"]["full_name"]
            # ref is like 'refs/heads/main', get the branch name
            ref = data.get("ref", "refs/heads/main")
            branch = ref.split("/")[-1]

            # Ignore pushes to main to avoid double-triggering on PR merge
            if branch == 'main':
                logging.info("Ignoring push event to 'main' branch to prevent duplicate action on PR merge.")
                return jsonify({"status": "ignored", "reason": "push to main is handled by PR merge event"})

            # For pushes to other branches, trigger the direct deployment pipeline
            logging.info(f"Push to '{branch}' branch detected, triggering direct deployment orchestrator.")
            orchestrate_branch_push_pipeline(repo, branch)
            return jsonify({"status": "orchestrator triggered for push", "branch": branch})
        except Exception as e:
            logging.exception(f"Failed to orchestrate push event for branch '{branch}':")
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ignored", "event": event})

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.run(host="0.0.0.0", port=5001)
