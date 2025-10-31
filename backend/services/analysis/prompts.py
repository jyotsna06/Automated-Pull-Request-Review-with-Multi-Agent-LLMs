DEV_SUMMARY_PROMPT = """Summarize what changed in this diff with file/function granularity and highlight risky logic edges, boundary conditions, and misuses of APIs."""
ARCH_TAXONOMY_PROMPT = """Categorize the change using a security taxonomy (authN/Z, crypto, secrets, input validation, concurrency, configuration, dependency use)."""
SEC_POSTURE_PROMPT = """Evaluate the overall security posture impact of this change, linking to concrete code lines and explaining data/control flow implications."""
