import os, ast
from typing import Dict, List

def parse_python_files(repo_dir: str, changed_files: List[str]) -> Dict:
    result = {}
    for f in changed_files:
        if f.endswith(".py"):
            p = os.path.join(repo_dir, f)
            if not os.path.exists(p):
                continue
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    src = fh.read()
                tree = ast.parse(src)
                result[f] = {
                    "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)],
                    "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
                    "imports": [getattr(n.names[0], "name", "") for n in ast.walk(tree) if isinstance(n, ast.Import)],
                }
            except Exception:
                result[f] = {"error": "parse-failed"}
    return result
