import subprocess, json, shutil

def run_semgrep(repo_dir: str):
    if shutil.which("semgrep") is None:
        return {"error": "semgrep-not-found", "results": []}
    try:
        res = subprocess.run(
            ["semgrep", "scan", "--config", "p/ci", "--json"],
            cwd=repo_dir,
            check=True,
            text=True,
            capture_output=True,
        )
        return json.loads(res.stdout)
    except Exception as e:
        return {"error": str(e), "results": []}
