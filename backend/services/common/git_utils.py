import tempfile, subprocess, os
from dataclasses import dataclass
from typing import List

@dataclass
class Changed:
    files: List[str]
    diffs: str  # unified diff text

def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=False)

def out(cmd, cwd=None) -> str:
    res = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    return res.stdout

def clone_pr_repo(clone_url: str, head_sha: str):
    workdir = tempfile.mkdtemp(prefix="prscan_")
    run(["git", "clone", "--no-tags", "--depth", "50", clone_url, workdir])
    run(["git", "fetch", "origin", head_sha], cwd=workdir)
    run(["git", "checkout", head_sha], cwd=workdir)
    # Changed files vs. merge-base or last commit; here we diff against parent
    diffs = out(["git", "show", "--unified=3", head_sha], cwd=workdir)
    files = out(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", head_sha], cwd=workdir).splitlines()
    return workdir, Changed(files=files, diffs=diffs)
