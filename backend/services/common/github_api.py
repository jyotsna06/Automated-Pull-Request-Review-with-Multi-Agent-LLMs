import os, requests, time, jwt

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID", "")
GITHUB_INSTALLATION_ID = os.environ.get("GITHUB_INSTALLATION_ID", "")
GITHUB_PRIVATE_KEY_PATH = os.environ.get("GITHUB_PRIVATE_KEY_PATH", "")
API = "https://api.github.com"

def _app_jwt() -> str:
    if not (GITHUB_APP_ID and GITHUB_PRIVATE_KEY_PATH):
        return ""
    with open(GITHUB_PRIVATE_KEY_PATH, "r", encoding="utf-8") as fh:
        private_key = fh.read()
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 600, "iss": int(GITHUB_APP_ID)}
    return jwt.encode(payload, private_key, algorithm="RS256")


def _installation_token() -> str:
    app_jwt = _app_jwt()
    if not (app_jwt and GITHUB_INSTALLATION_ID):
        return ""
    url = f"https://api.github.com/app/installations/{GITHUB_INSTALLATION_ID}/access_tokens"
    r = requests.post(url, headers={"Authorization": f"Bearer {app_jwt}", "Accept": "application/vnd.github+json"}, timeout=30)
    r.raise_for_status()
    return r.json().get("token", "")


def _headers():
    token = GITHUB_TOKEN or _installation_token()
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

def post_pr_comment(owner_repo: str, pr_number: int, c: dict):
    # c: {"path","line","side","body","severity"}
    url = f"{API}/repos/{owner_repo}/pulls/{pr_number}/comments"
    payload = {
        "body": c["body"],
        "path": c["path"],
        "line": c["line"],
        "side": c.get("side", "RIGHT"),
    }
    r = requests.post(url, headers=_headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def post_pr_review_summary(owner_repo: str, pr_number: int, summary: str):
    # Create a review with a general comment body
    url = f"{API}/repos/{owner_repo}/pulls/{pr_number}/reviews"
    payload = {"body": summary, "event": "COMMENT"}
    r = requests.post(url, headers=_headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()
