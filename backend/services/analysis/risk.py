from typing import Dict, List
import re

SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}

def _cvss_severity_from_osv(entry):
    # Prefer provided severity if available, otherwise default MEDIUM
    if not entry:
        return "MEDIUM"
    sev = "MEDIUM"
    for a in entry.get("vulns", []) or []:
        for s in a.get("severity", []) or []:
            score = s.get("score") or ""
            if score.startswith("CVSS:3.1"):
                # naive mapping: rely on provided "type"/"score" if present downstream
                sev = "HIGH"
    return sev

def _category_from_semgrep(finding):
    msg = (finding.get("extra", {}) or {}).get("message", "").lower()
    if any(k in msg for k in ["sql", "injection"]):
        return "SQL Injection"
    if any(k in msg for k in ["xss", "cross-site"]):
        return "XSS"
    if any(k in msg for k in ["secret", "key", "token"]):
        return "Hardcoded Secret"
    if any(k in msg for k in ["auth", "jwt", "session"]):
        return "Authentication"
    if any(k in msg for k in ["config", "insecure", "tls", "ssl"]):
        return "Insecure Config"
    return "General"

def aggregate_findings(changed_files, diffs, dev, arch, sec, semgrep, bandit, osv, pr_data):
    inline_comments = []
    summary_items = []

    # Semgrep findings
    for r in (semgrep.get("results") or []):
        path = r.get("path")
        start = ((r.get("start", {}) or {}).get("line") or 1)
        message = (r.get("extra", {}) or {}).get("message", "Issue")
        category = _category_from_semgrep(r)
        sev = ((r.get("extra", {}) or {}).get("severity") or "MEDIUM").upper()
        fix = (r.get("extra", {}).get("metadata", {}) or {}).get("fix", None)
        body = f"[{category}] {message}\nSuggested fix: {fix or 'add parameterization/validation'}"
        inline_comments.append({
            "path": path, "line": start, "side": "RIGHT", "body": body, "severity": sev
        })

    # Bandit findings
    for f in (bandit.get("results") or []):
        path = f.get("filename")
        line = f.get("line_number") or 1
        test_id = f.get("test_id")
        text = f.get("issue_text")
        sev = (f.get("issue_severity") or "MEDIUM").upper()
        body = f"[Python Security] {test_id}: {text}\nSuggested fix: use safer API / validate inputs"
        inline_comments.append({"path": path, "line": line, "side": "RIGHT", "body": body, "severity": sev})

    # OSV results
    osv_summary = []
    for dep, res in zip(osv.get("dependencies", []), osv.get("results", [])):
        eco, name, ver = dep
        if res and res.get("vulns"):
            sev = _cvss_severity_from_osv(res)
            osv_summary.append(f"{eco}:{name}@{ver} -> {len(res['vulns'])} vulns ({sev})")

    # Agent outputs (assumed structured JSON strings in .text)
    dev_text = dev.get("text", "{}")
    arch_text = arch.get("text", "{}")
    sec_text = sec.get("text", "{}")

    summary_items.append("Semgrep issues: " + str(len(semgrep.get("results") or [])))
    summary_items.append("Bandit issues: " + str(len(bandit.get("results") or [])))
    summary_items.append("OSV vulnerable dependencies: " + str(len([x for x in osv_summary])))

    summary = "Security Review Summary\n" + "\n".join(f"- {s}" for s in summary_items) + \
              ("\nDependency risks:\n" + "\n".join(f"- {s}" for s in osv_summary) if osv_summary else "")

    return type("RiskOut", (), {"inline_comments": inline_comments, "summary": summary})
