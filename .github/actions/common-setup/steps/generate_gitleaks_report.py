#!/usr/bin/env python3
import json
import html
from pathlib import Path

report_path = Path("reports/gitleaks.json")
html_path = Path("reports/gitleaks-report.html")

findings = []
if report_path.exists():
    data = json.loads(report_path.read_text())
    findings = data if isinstance(data, list) else data.get("findings", [])

rows = "".join(
    "<tr>"
    f"<td>{html.escape(str(item.get('Description', 'N/A')))}</td>"
    f"<td>{html.escape(str(item.get('File', 'N/A')))}</td>"
    f"<td>{html.escape(str(item.get('Line', 'N/A')))}</td>"
    "</tr>"
    for item in findings
)

html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset=\"utf-8\">
    <title>Gitleaks Report</title>
  </head>
  <body>
    <h1>Gitleaks Report</h1>
    <p>Total findings: {len(findings)}</p>
    <table>
      <tr><th>Description</th><th>File</th><th>Line</th></tr>
      {rows}
    </table>
  </body>
</html>
"""

html_path.write_text(html_content)
print(f"Created report at {html_path}")
