import os, json
from typing import Dict, List
from backend.services.analysis.py_ast import parse_python_files
from backend.services.analysis.prompts import DEV_SUMMARY_PROMPT, ARCH_TAXONOMY_PROMPT, SEC_POSTURE_PROMPT
from backend.services.analysis.providers import call_dev_agent, call_arch_agent, call_sec_agent
from backend.services.scanners.semgrep_runner import run_semgrep
from backend.services.scanners.bandit_runner import run_bandit
from backend.services.scanners.osv_runner import run_osv_scan
from backend.services.analysis.risk import aggregate_findings
from backend.services.learning.store import save_metric

class AnalysisResult:
    def __init__(self, inline_comments, summary):
        self.inline_comments = inline_comments
        self.summary = summary

def run_full_analysis(repo_dir: str, changed_files: List[str], diffs: str, pr_data: Dict):
    ast_summary = parse_python_files(repo_dir, changed_files)
    dev_out = call_dev_agent(DEV_SUMMARY_PROMPT, diffs, ast_summary)
    arch_out = call_arch_agent(ARCH_TAXONOMY_PROMPT, diffs, ast_summary)
    sec_out = call_sec_agent(SEC_POSTURE_PROMPT, diffs, ast_summary)

    semgrep_res = run_semgrep(repo_dir)
    bandit_res = run_bandit(repo_dir)
    osv_res = run_osv_scan(repo_dir)

    risk = aggregate_findings(
        changed_files=changed_files,
        diffs=diffs,
        dev=dev_out,
        arch=arch_out,
        sec=sec_out,
        semgrep=semgrep_res,
        bandit=bandit_res,
        osv=osv_res,
        pr_data=pr_data,
    )

    # Save some high-level metrics for the dashboard
    try:
        repo = pr_data.get("owner_repo", "unknown")
        save_metric(repo, "semgrep_issues", float(len(semgrep_res.get("results") or [])))
        save_metric(repo, "bandit_issues", float(len(bandit_res.get("results") or [])))
        # Count deps with vulns
        osv_count = 0.0
        for dep, res in zip(osv_res.get("dependencies", []), osv_res.get("results", [])):
            if res and res.get("vulns"):
                osv_count += 1.0
        save_metric(repo, "osv_vulnerable_deps", osv_count)
    except Exception:
        pass

    return AnalysisResult(inline_comments=risk.inline_comments, summary=risk.summary)
