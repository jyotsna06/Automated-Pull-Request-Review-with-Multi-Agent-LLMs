import os, json, glob, re, requests

OSV_API = os.getenv("OSV_API_BASE", "https://api.osv.dev/v1")

def _py_requirements(repo_dir):
    reqs = []
    for p in glob.glob(os.path.join(repo_dir, "**/requirements*.txt"), recursive=True):
        with open(p, "r", encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+-]+)", line.strip())
                if m:
                    reqs.append(("PyPI", m.group(1), m.group(2)))
    return reqs

def _npm_packages(repo_dir):
    lock = os.path.join(repo_dir, "package-lock.json")
    if not os.path.exists(lock):
        return []
    with open(lock, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    deps = []
    def walk(node):
        for name, info in (node.get("dependencies") or {}).items():
            ver = info.get("version")
            if ver:
                deps.append(("npm", name, ver))
            walk(info)
    walk(data)
    return deps

def _bulk_query(packages):
    if not packages:
        return []
    payload = {"queries": []}
    for eco, name, version in packages:
        payload["queries"].append({
            "package": {"ecosystem": eco, "name": name},
            "version": version
        })
    resp = requests.post(f"{OSV_API}/querybatch", json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json().get("results", [])

def run_osv_scan(repo_dir: str):
    py = _py_requirements(repo_dir)
    js = _npm_packages(repo_dir)
    results = _bulk_query(py + js)
    return {"dependencies": py + js, "results": results}
