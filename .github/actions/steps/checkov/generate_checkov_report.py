#!/usr/bin/env python3
"""
Generate a rich, glassmorphism HTML Dashboard report for Checkov IaC & Dockerfile security scan results.
"""

import json
import html
from pathlib import Path

report_path = Path("reports/checkov-report.json")
html_path = Path("reports/checkov-report.html")

passed_count = 0
failed_count = 0
skipped_count = 0
failed_checks = []

if report_path.exists():
    try:
        raw_text = report_path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
        # Checkov output can be a dict or list of dicts (multi-framework)
        results_list = data if isinstance(data, list) else [data]
        for res in results_list:
            summary = res.get("summary", {})
            passed_count += summary.get("passed", 0)
            failed_count += summary.get("failed", 0)
            skipped_count += summary.get("skipped", 0)
            
            results = res.get("results", {})
            failed_checks.extend(results.get("failed_checks", []))
    except Exception as e:
        print(f"Warning parsing checkov-report.json: {e}")

status_str = "PASSED" if failed_count == 0 else "FAILED"
qg_class = "qg-passed" if failed_count == 0 else "qg-failed"
qg_icon = "✓" if failed_count == 0 else "✕"

rows = ""
for item in failed_checks:
    check_id = item.get("check_id", "CKV_UNKNOWN")
    check_name = item.get("check_name", "Security Check Failed")
    file_path = item.get("file_path", "Dockerfile")
    resource = item.get("resource", "N/A")

    rows += f"""
    <tr>
        <td><span class="badge badge-failed">{html.escape(str(check_id))}</span></td>
        <td>{html.escape(str(check_name))}</td>
        <td class="file-path">{html.escape(str(file_path))}</td>
        <td><code>{html.escape(str(resource))}</code></td>
    </tr>
    """

if not rows:
    rows = '<tr><td colspan="4" style="text-align:center; color: #94a3b8; padding: 2rem;">No Dockerfile / IaC security misconfigurations detected! 🎉</td></tr>'

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkov IaC & Dockerfile Security Report</title>
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
            --accent-red: #ef4444;
            --accent-cyan: #06b6d4;
            --accent-purple: #8b5cf6;
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
            display: flex; align-items: center; justify-content: space-between;
            padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 2rem;
            backdrop-filter: blur(12px); border: 1px solid var(--card-border);
        }}
        .qg-banner.qg-passed {{ background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3); }}
        .qg-banner.qg-failed {{ background: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.3); }}

        .qg-icon-circle {{
            width: 50px; height: 50px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.8rem; font-weight: bold;
        }}
        .qg-passed .qg-icon-circle {{ background: rgba(16, 185, 129, 0.25); color: var(--accent-green); }}
        .qg-failed .qg-icon-circle {{ background: rgba(239, 68, 68, 0.25); color: var(--accent-red); }}

        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.25rem; margin-bottom: 2rem; }}
        .kpi-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.25rem; backdrop-filter: blur(10px); }}
        .kpi-title {{ color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; text-transform: uppercase; }}
        .kpi-value {{ font-size: 2rem; font-weight: 700; margin-top: 0.5rem; }}

        .section-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.5rem; backdrop-filter: blur(10px); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
        th, td {{ padding: 0.85rem 1rem; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.92rem; }}
        th {{ color: var(--text-secondary); text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.5px; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}
        .badge-failed {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }}
        .file-path {{ font-family: monospace; color: #cbd5e1; }}
        code {{ background: rgba(0, 0, 0, 0.3); padding: 0.2rem 0.4rem; border-radius: 4px; color: #38bdf8; font-family: monospace; }}

        footer {{ text-align: center; color: var(--text-secondary); font-size: 0.85rem; margin-top: 3rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="title-group">
                <h1>Checkov IaC & Dockerfile Security Report</h1>
                <p>Infrastructure-as-Code & Container Security Misconfiguration Audit</p>
            </div>
        </header>

        <div class="qg-banner {qg_class}">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div class="qg-icon-circle">{qg_icon}</div>
                <div>
                    <h2>Security Audit Status: {status_str}</h2>
                    <p>Dockerfile & IaC templates evaluated against CIS benchmarks and security standards.</p>
                </div>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Passed Checks</div>
                <div class="kpi-value" style="color: var(--accent-green);">{passed_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Failed Checks</div>
                <div class="kpi-value" style="color: {'var(--accent-green)' if failed_count == 0 else 'var(--accent-red)'};">{failed_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Skipped Checks</div>
                <div class="kpi-value" style="color: var(--text-secondary);">{skipped_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Framework</div>
                <div class="kpi-value" style="color: var(--accent-purple);">Dockerfile / IaC</div>
            </div>
        </div>

        <div class="section-card">
            <h3 style="margin-bottom: 1rem;">Failed Security Checks ({len(failed_checks)})</h3>
            <table>
                <thead>
                    <tr>
                        <th>Check ID</th>
                        <th>Policy Name</th>
                        <th>File Path</th>
                        <th>Target Resource</th>
                    </tr>
                </thead>
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
print(f"Successfully generated Checkov HTML Report at: {html_path}")
