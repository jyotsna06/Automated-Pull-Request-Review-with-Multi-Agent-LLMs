import subprocess, json, shutil

def run_bandit(repo_dir: str):
    if shutil.which("bandit") is None:
        return {"error": "bandit-not-found", "results": []}
    try:
        res = subprocess.run(
            ["bandit", "-r", ".", "-f", "json"],
            cwd=repo_dir,
            check=True,
            text=True,
            capture_output=True,
        )
        return json.loads(res.stdout)
    except Exception as e:
        return {"error": str(e), "results": []}
