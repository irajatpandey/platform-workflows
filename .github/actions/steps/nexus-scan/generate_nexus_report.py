#!/usr/bin/env python3
"""
Generate a rich, glassmorphism HTML Dashboard report for Nexus IQ Dependency Policy Scan.
"""

import json
import html
from pathlib import Path

summary_path = Path("reports/nexus-scan-summary.json")
audit_path = Path("reports/nexus-policy-audit.txt")
html_path = Path("reports/nexus-report.html")

app_id = "Unknown App"
stage = "build"
nexus_url = "Offline Audit"
status = "COMPLETED"

if summary_path.exists():
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        app_id = data.get("application_id", app_id)
        stage = data.get("stage", stage)
        nexus_url = data.get("nexus_url", nexus_url) or "Offline Mode"
        status = data.get("status", status)
    except Exception as e:
        print(f"Warning parsing nexus-scan-summary.json: {e}")

audit_lines = []
if audit_path.exists():
    audit_text = audit_path.read_text(encoding="utf-8")
    audit_lines = [line.strip() for line in audit_text.splitlines() if line.strip()]

rows = ""
for line in audit_lines[:50]: # limit to top 50
    rows += f"<tr><td><code>{html.escape(line)}</code></td></tr>"

if not rows:
    rows = '<tr><td style="text-align:center; color: #94a3b8; padding: 2rem;">No dependency vulnerabilities or policy violations detected! 🎉</td></tr>'

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus IQ Dependency Audit Report</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-green: #10b981;
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }}
        body {{ background: var(--bg-gradient); color: var(--text-primary); min-height: 100vh; padding: 2rem 1.5rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}

        header {{
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--card-border);
        }}
        .title-group h1 {{
            font-size: 2.2rem; font-weight: 700;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .title-group p {{ color: var(--text-secondary); font-size: 0.95rem; margin-top: 0.25rem; }}

        .qg-banner {{
            display: flex; align-items: center; gap: 1rem;
            padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 2rem;
            backdrop-filter: blur(12px); border: 1px solid rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.15);
        }}
        .qg-icon-circle {{
            width: 50px; height: 50px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.8rem; font-weight: bold; background: rgba(16, 185, 129, 0.25); color: var(--accent-green);
        }}

        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 2rem; }}
        .kpi-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.25rem; backdrop-filter: blur(10px); }}
        .kpi-title {{ color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; text-transform: uppercase; }}
        .kpi-value {{ font-size: 1.6rem; font-weight: 700; margin-top: 0.5rem; word-break: break-all; }}

        .section-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.5rem; backdrop-filter: blur(10px); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
        td {{ padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.9rem; }}
        code {{ color: #a78bfa; font-family: monospace; word-break: break-all; }}

        footer {{ text-align: center; color: var(--text-secondary); font-size: 0.85rem; margin-top: 3rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="title-group">
                <h1>Nexus IQ Dependency Policy Report</h1>
                <p>Third-Party Component Vulnerability & License Compliance Audit</p>
            </div>
        </header>

        <div class="qg-banner">
            <div class="qg-icon-circle">✓</div>
            <div>
                <h2>Dependency Policy Audit: {html.escape(status)}</h2>
                <p>Third-party libraries evaluated against open-source vulnerability databases and organization policies.</p>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Application ID</div>
                <div class="kpi-value" style="color: var(--accent-cyan);">{html.escape(app_id)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Lifecycle Stage</div>
                <div class="kpi-value" style="color: var(--accent-purple);">{html.escape(stage)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Nexus Server</div>
                <div class="kpi-value" style="font-size: 1.1rem; color: var(--text-secondary);">{html.escape(nexus_url)}</div>
            </div>
        </div>

        <div class="section-card">
            <h3 style="margin-bottom: 1rem;">Policy Audit Log Output</h3>
            <table>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>

        <footer>
            Generated automatically by platform-workflows GitHub Action Pipeline.
        </footer>
    </div>
</body>
</html>
"""

html_path.write_text(html_content, encoding="utf-8")
print(f"Successfully generated Nexus HTML Report at: {html_path}")
