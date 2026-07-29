#!/usr/bin/env python3
"""
Generate a rich, interactive HTML Dashboard report for SonarQube / SonarCloud scan results.
"""

import os
import json
import urllib.request
import urllib.error
import html
from pathlib import Path

# Target output files
report_dir = Path("reports")
report_dir.mkdir(parents=True, exist_ok=True)
html_path = report_dir / "sonarqube-report.html"

# Environment variables
sonar_token = os.environ.get("SONAR_TOKEN", "")
project_key = os.environ.get("PROJECT_KEY", "")
organization = os.environ.get("ORGANIZATION", "")
host_url = os.environ.get("SONAR_HOST_URL", "https://sonarcloud.io").rstrip("/")

def make_request(endpoint):
    url = f"{host_url}{endpoint}"
    req = urllib.request.Request(url)
    if sonar_token:
        # Basic Auth with token as username and empty password
        import base64
        auth_header = base64.b64encode(f"{sonar_token}:".encode("utf-8")).decode("utf-8")
        req.add_header("Authorization", f"Basic {auth_header}")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Warning: Failed to fetch {url}: {e}")
    return None

# Fetch Quality Gate Status
qg_data = make_request(f"/api/qualitygates/project_status?projectKey={project_key}&organization={organization}")

# Fetch Component Measures
measures_metrics = "bugs,vulnerabilities,code_smells,security_hotspots,coverage,duplicated_lines_density,ncloc,reliability_rating,security_rating,sqale_rating"
measures_data = make_request(f"/api/measures/component?component={project_key}&metricKeys={measures_metrics}")

# Fetch Issues
issues_data = make_request(f"/api/issues/search?componentKeys={project_key}&ps=50&resolved=false")

# Parse Quality Gate
qg_status = "UNKNOWN"
qg_conditions = []
if qg_data and "projectStatus" in qg_data:
    ps = qg_data["projectStatus"]
    qg_status = ps.get("status", "UNKNOWN")
    qg_conditions = ps.get("conditions", [])

# Parse Measures
measures_dict = {}
if measures_data and "component" in measures_data and "measures" in measures_data["component"]:
    for m in measures_data["component"]["measures"]:
        measures_dict[m["metric"]] = m.get("value", "N/A")

# Parse Issues
issues_list = []
if issues_data and "issues" in issues_data:
    issues_list = issues_data["issues"]

# Helper for ratings (1=A, 2=B, 3=C, 4=D, 5=E)
def format_rating(val):
    try:
        num = int(float(val))
        return {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}.get(num, str(val))
    except:
        return str(val)

# Styling classes for Quality Gate
qg_class = "qg-passed" if qg_status in ["OK", "PASSED"] else "qg-failed"
qg_icon = "✓" if qg_status in ["OK", "PASSED"] else "✕"

# Generate Quality Gate Conditions Table Rows
qg_rows = ""
for cond in qg_conditions:
    c_status = cond.get("status", "N/A")
    metric = cond.get("metricKey", "").replace("_", " ").title()
    comparator = cond.get("comparator", "")
    error_thresh = cond.get("errorThreshold", "-")
    actual = cond.get("actualValue", "N/A")
    badge_cls = "badge-passed" if c_status == "OK" else "badge-failed"
    qg_rows += f"""
    <tr>
        <td><span class="badge {badge_cls}">{html.escape(c_status)}</span></td>
        <td><strong>{html.escape(metric)}</strong></td>
        <td>{html.escape(str(comparator))} {html.escape(str(error_thresh))}</td>
        <td><strong>{html.escape(str(actual))}</strong></td>
    </tr>
    """

# Generate Issues Table Rows
issue_rows = ""
for issue in issues_list:
    sev = issue.get("severity", "INFO")
    i_type = issue.get("type", "CODE_SMELL").replace("_", " ").title()
    comp = issue.get("component", "").split(":")[-1]
    line = issue.get("line", "-")
    msg = issue.get("message", "No description")
    
    sev_cls = f"sev-{sev.lower()}"
    issue_rows += f"""
    <tr>
        <td><span class="badge {sev_cls}">{html.escape(sev)}</span></td>
        <td>{html.escape(i_type)}</td>
        <td class="file-path">{html.escape(comp)}:{line}</td>
        <td>{html.escape(msg)}</td>
    </tr>
    """

if not issue_rows:
    issue_rows = '<tr><td colspan="4" style="text-align:center; color: #94a3b8; padding: 2rem;">No open issues found! Excellent code quality. 🎉</td></tr>'

# Format metrics
bugs_val = measures_dict.get("bugs", "0")
vuln_val = measures_dict.get("vulnerabilities", "0")
smells_val = measures_dict.get("code_smells", "0")
hotspots_val = measures_dict.get("security_hotspots", "0")
cov_val = measures_dict.get("coverage", "0")
dup_val = measures_dict.get("duplicated_lines_density", "0")
lines_val = measures_dict.get("ncloc", "0")

rel_rating = format_rating(measures_dict.get("reliability_rating", 1))
sec_rating = format_rating(measures_dict.get("security_rating", 1))
maint_rating = format_rating(measures_dict.get("sqale_rating", 1))

sonar_dashboard_url = f"{host_url}/dashboard?id={project_key}"

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SonarQube SAST Report - {html.escape(project_key)}</title>
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
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --accent-orange: #f59e0b;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        body {{
            background: var(--bg-gradient);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem 1.5rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--card-border);
        }}

        .title-group h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .title-group p {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }}

        .sonar-link-btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.25rem;
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.4);
            color: #c4b5fd;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .sonar-link-btn:hover {{
            background: rgba(139, 92, 246, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
        }}

        /* Quality Gate Banner */
        .qg-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
        }}

        .qg-banner.qg-passed {{
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.3);
        }}

        .qg-banner.qg-failed {{
            background: rgba(239, 68, 68, 0.15);
            border-color: rgba(239, 68, 68, 0.3);
        }}

        .qg-status {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .qg-icon-circle {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            font-weight: bold;
        }}

        .qg-passed .qg-icon-circle {{
            background: rgba(16, 185, 129, 0.25);
            color: var(--accent-green);
        }}

        .qg-failed .qg-icon-circle {{
            background: rgba(239, 68, 68, 0.25);
            color: var(--accent-red);
        }}

        .qg-text h2 {{
            font-size: 1.4rem;
            font-weight: 600;
        }}

        .qg-text p {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        /* KPI Cards Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}

        .kpi-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.25rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        }}

        .kpi-title {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .kpi-value {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0.5rem 0 0.2rem 0;
        }}

        .kpi-rating {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.85rem;
        }}

        .rating-a {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); }}
        .rating-b {{ background: rgba(6, 182, 212, 0.2); color: var(--accent-cyan); }}
        .rating-c {{ background: rgba(245, 158, 11, 0.2); color: var(--accent-orange); }}
        .rating-d, .rating-e {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }}

        /* Table Section */
        .section-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
        }}

        .section-header {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
        }}

        th, td {{
            padding: 0.85rem 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.92rem;
        }}

        th {{
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }}

        tr:hover td {{
            background: rgba(255, 255, 255, 0.03);
        }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .badge-passed {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); }}
        .badge-failed {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }}
        .sev-blocker, .sev-critical {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }}
        .sev-major {{ background: rgba(245, 158, 11, 0.2); color: var(--accent-orange); }}
        .sev-minor, .sev-info {{ background: rgba(6, 182, 212, 0.2); color: var(--accent-cyan); }}

        .file-path {{
            font-family: monospace;
            color: #cbd5e1;
        }}

        footer {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-top: 3rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="title-group">
                <h1>SonarQube SAST Report</h1>
                <p>Project: <strong>{html.escape(project_key)}</strong> &bull; Organization: <strong>{html.escape(organization)}</strong></p>
            </div>
            <a href="{html.escape(sonar_dashboard_url)}" target="_blank" class="sonar-link-btn">
                Open in SonarCloud &rarr;
            </a>
        </header>

        <!-- Quality Gate Status Banner -->
        <div class="qg-banner {qg_class}">
            <div class="qg-status">
                <div class="qg-icon-circle">{qg_icon}</div>
                <div class="qg-text">
                    <h2>Quality Gate Status: {html.escape(qg_status)}</h2>
                    <p>All strict quality rules evaluated against project standards.</p>
                </div>
            </div>
        </div>

        <!-- KPI Metrics Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Bugs</div>
                <div class="kpi-value" style="color: var(--accent-red);">{html.escape(str(bugs_val))}</div>
                <span class="kpi-rating rating-{rel_rating.lower()}">Rating {rel_rating}</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Vulnerabilities</div>
                <div class="kpi-value" style="color: var(--accent-orange);">{html.escape(str(vuln_val))}</div>
                <span class="kpi-rating rating-{sec_rating.lower()}">Rating {sec_rating}</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Security Hotspots</div>
                <div class="kpi-value" style="color: var(--accent-purple);">{html.escape(str(hotspots_val))}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Code Smells</div>
                <div class="kpi-value" style="color: var(--accent-cyan);">{html.escape(str(smells_val))}</div>
                <span class="kpi-rating rating-{maint_rating.lower()}">Rating {maint_rating}</span>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Coverage</div>
                <div class="kpi-value" style="color: var(--accent-green);">{html.escape(str(cov_val))}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Duplications</div>
                <div class="kpi-value">{html.escape(str(dup_val))}%</div>
            </div>
        </div>

        <!-- Quality Gate Conditions -->
        <div class="section-card">
            <div class="section-header">
                <span>Quality Gate Conditions</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Metric</th>
                        <th>Threshold</th>
                        <th>Actual Value</th>
                    </tr>
                </thead>
                <tbody>
                    {qg_rows if qg_rows else '<tr><td colspan="4">No Quality Gate conditions specified.</td></tr>'}
                </tbody>
            </table>
        </div>

        <!-- Code Issues Breakdown -->
        <div class="section-card">
            <div class="section-header">
                <span>Detected Open Issues ({len(issues_list)})</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Type</th>
                        <th>Component & Line</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {issue_rows}
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
print(f"Successfully generated SonarQube HTML Report at: {html_path}")
