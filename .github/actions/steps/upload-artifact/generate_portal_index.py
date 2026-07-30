#!/usr/bin/env python3
"""
Generate a Unified Security & Quality Portal index.html linking to all security audit reports.
"""

from pathlib import Path

reports_dir = Path("reports")
reports_dir.mkdir(parents=True, exist_ok=True)
index_path = reports_dir / "index.html"

# Check which reports exist
has_sonar = (reports_dir / "sonarqube-report.html").exists()
has_gitleaks = (reports_dir / "gitleaks-report.html").exists()
has_nexus = (reports_dir / "nexus-report.html").exists()
has_checkov = (reports_dir / "checkov-report.html").exists()

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organization Security & Quality Governance Portal</title>
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
            --accent-blue: #38bdf8;
            --accent-green: #10b981;
            --accent-purple: #8b5cf6;
            --accent-orange: #f59e0b;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }}
        body {{ background: var(--bg-gradient); color: var(--text-primary); min-height: 100vh; padding: 3rem 1.5rem; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}

        header {{
            text-align: center; margin-bottom: 3.5rem;
        }}
        header h1 {{
            font-size: 2.8rem; font-weight: 700;
            background: linear-gradient(90deg, #38bdf8, #a78bfa, #f472b6);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        header p {{ color: var(--text-secondary); font-size: 1.1rem; }}

        .portal-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem;
        }}

        .portal-card {{
            background: var(--card-bg); border: 1px solid var(--card-border);
            border-radius: 20px; padding: 2rem 1.5rem; text-decoration: none;
            color: var(--text-primary); backdrop-filter: blur(12px);
            transition: all 0.35s ease; display: flex; flex-direction: column; justify-content: space-between;
        }}

        .portal-card:hover {{
            transform: translateY(-8px);
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        }}

        .card-icon {{
            width: 60px; height: 60px; border-radius: 16px; display: flex;
            align-items: center; justify-content: center; font-size: 1.8rem; margin-bottom: 1.25rem;
        }}

        .card-title {{ font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem; }}
        .card-desc {{ color: var(--text-secondary); font-size: 0.9rem; line-height: 1.4; margin-bottom: 1.5rem; }}

        .card-btn {{
            display: inline-flex; align-items: center; justify-content: space-between;
            width: 100%; padding: 0.75rem 1rem; border-radius: 12px;
            background: rgba(255, 255, 255, 0.05); font-weight: 600; font-size: 0.9rem;
            color: #e2e8f0; transition: background 0.2s;
        }}

        .portal-card:hover .card-btn {{
            background: rgba(255, 255, 255, 0.15); color: #fff;
        }}

        footer {{ text-align: center; color: var(--text-secondary); font-size: 0.9rem; margin-top: 4rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Security & Quality Governance Portal</h1>
            <p>Unified Automated Pipeline Audits & Compliance Reports</p>
        </header>

        <div class="portal-grid">
            <!-- SonarQube Card -->
            <a href="sonarqube-report.html" class="portal-card">
                <div>
                    <div class="card-icon" style="background: rgba(56, 189, 248, 0.15); color: var(--accent-blue);">🛡️</div>
                    <div class="card-title">SonarQube SAST</div>
                    <div class="card-desc">Static Application Security Testing, Quality Gate status, bugs, and code ratings.</div>
                </div>
                <div class="card-btn">View SAST Report &rarr;</div>
            </a>

            <!-- Gitleaks Card -->
            <a href="gitleaks-report.html" class="portal-card">
                <div>
                    <div class="card-icon" style="background: rgba(244, 114, 182, 0.15); color: #f472b6;">🔑</div>
                    <div class="card-title">Gitleaks Secrets</div>
                    <div class="card-desc">Hardcoded credentials, API keys, tokens, and private key detection audit.</div>
                </div>
                <div class="card-btn">View Secrets Report &rarr;</div>
            </a>

            <!-- Nexus IQ Card -->
            <a href="nexus-report.html" class="portal-card">
                <div>
                    <div class="card-icon" style="background: rgba(139, 92, 246, 0.15); color: var(--accent-purple);">📦</div>
                    <div class="card-title">Nexus IQ Policy</div>
                    <div class="card-desc">Third-party component vulnerability, open-source policy, and license compliance.</div>
                </div>
                <div class="card-btn">View Nexus Report &rarr;</div>
            </a>

            <!-- Checkov Card -->
            <a href="checkov-report.html" class="portal-card">
                <div>
                    <div class="card-icon" style="background: rgba(16, 185, 129, 0.15); color: var(--accent-green);">🐳</div>
                    <div class="card-title">Checkov IaC & Docker</div>
                    <div class="card-desc">Dockerfile security misconfigurations, CIS benchmarks, and container policy audit.</div>
                </div>
                <div class="card-btn">View Checkov Report &rarr;</div>
            </a>
        </div>

        <footer>
            Platform Governance CI/CD Pipeline &bull; Automated Security Reporting
        </footer>
    </div>
</body>
</html>
"""

index_path.write_text(html_content, encoding="utf-8")
print(f"Successfully generated Portal index.html at: {index_path}")
