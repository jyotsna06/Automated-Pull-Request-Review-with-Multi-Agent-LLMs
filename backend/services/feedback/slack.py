import os, json, requests

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

def notify_critical(owner_repo: str, pr_number: int, findings: int):
    if not SLACK_WEBHOOK_URL:
        return
    payload = {
        "text": f"Critical findings detected in {owner_repo} PR #{pr_number}: {findings}"
    }
    requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
