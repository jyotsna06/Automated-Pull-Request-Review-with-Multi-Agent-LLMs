from fastapi import FastAPI, Request, HTTPException
import hmac, hashlib, os, json
from backend.services.common.github_api import post_pr_comment, post_pr_review_summary
from backend.services.common.git_utils import clone_pr_repo
from backend.services.analysis.pipeline import run_full_analysis
from backend.services.learning.store import init_db, save_suggestions
from backend.services.feedback.slack import notify_critical

app = FastAPI()

GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "").encode()

def verify_signature(payload: bytes, signature_header: str) -> bool:
    # GitHub: X-Hub-Signature-256 = sha256=...
    mac = hmac.new(GITHUB_WEBHOOK_SECRET, msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature_header or "")

@app.post("/webhook")
async def github_webhook(request: Request):
    event = request.headers.get("X-GitHub-Event", "")
    sig = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()
    if not verify_signature(body, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body.decode("utf-8"))
    if event == "pull_request":
        action = payload.get("action", "")
        if action in {"opened", "synchronize", "reopened", "edited", "ready_for_review"}:
            repo_full = payload["repository"]["full_name"]
            pr_number = payload["number"]
            head = payload["pull_request"]["head"]
            head_repo = head["repo"]["clone_url"]
            head_sha = head["sha"]
            base_ref = payload["pull_request"]["base"]["ref"]

            clone_dir, changed = clone_pr_repo(head_repo, head_sha)
            analysis = run_full_analysis(
                repo_dir=clone_dir,
                changed_files=changed.files,
                diffs=changed.diffs,
                pr_data={"owner_repo": repo_full, "number": pr_number, "base_ref": base_ref, "head_sha": head_sha},
            )

            # Post inline comments and summary
            for c in analysis.inline_comments:
                post_pr_comment(repo_full, pr_number, c)
            post_pr_review_summary(repo_full, pr_number, analysis.summary)
            # Slack notify for HIGH/CRITICAL findings
            try:
                high_count = sum(1 for c in analysis.inline_comments if c.get("severity", "").upper() in {"HIGH", "CRITICAL"})
                if high_count:
                    notify_critical(repo_full, pr_number, high_count)
            except Exception:
                pass
            # Persist suggestions for dashboard/learning
            try:
                init_db()
                save_suggestions(repo_full, pr_number, analysis.inline_comments)
            except Exception:
                pass

    return {"status": "ok"}

@app.get("/health")
def health():
    return {"ok": True}
