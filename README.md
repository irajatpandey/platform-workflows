# Platform Workflows (`platform-workflows`)

A centralized GitHub Actions library providing reusable workflows and modular composite actions for standardized, secure, and automated CI/CD across organization repositories.

---

## 🏗️ Repository Architecture

```text
platform-workflows/
├── .github/
│   ├── actions/
│   │   └── steps/                    # Reusable Composite Actions
│   │       ├── run-gitleaks/         # Secret scanning with Gitleaks & HTML report generation
│   │       ├── setup-java/           # Java SDK environment setup
│   │       ├── setup-python/         # Python environment setup
│   │       ├── sonarqube/            # SonarCloud SAST scan & Quality Gate wait
│   │       └── upload-artifact/      # Artifact packaging & upload helper
│   │
│   └── workflows/                    # Reusable Workflows (workflow_call)
│       ├── python-ci.yml             # Python CI pipeline (test, coverage, gitleaks, SonarCloud)
│       ├── java-ci.yml               # Java CI pipeline
│       ├── node-ci.yml               # Node.js CI pipeline
│       ├── go-ci.yml                 # Go CI pipeline
│       ├── docker-build.yml          # Container image build & push
│       ├── helm-deploy.yml           # Helm deployment pipeline
│       ├── security.yml              # Security & vulnerability scanning
│       └── ...                       # Additional platform pipelines
└── README.md
```

---

## 🚀 Usage Guide: `python-ci.yml`

The `python-ci.yml` workflow provides an end-to-end Python CI pipeline including test execution, coverage collection (`pytest-cov`), secret scanning (`gitleaks`), and SonarCloud SAST analysis with Quality Gate enforcement.

### Example Caller Workflow (`.github/workflows/my-service-ci.yml`)

In your service repository, invoke the reusable workflow as follows:

```yaml
name: Python Service CI

on:
  push:
    branches:
      - master
      - feature/**
      - release/**
  pull_request:
    branches:
      - master
      - release/**
  workflow_dispatch:
    inputs:
      python-version:
        description: "Python version"
        required: false
        type: string
        default: "3.12"
      exclusions:
        description: "SonarQube exclusions"
        required: false
        type: string
        default: ""
      run-sonar:
        description: "Run SonarQube analysis"
        required: false
        type: boolean
        default: true

jobs:
  ci-pipeline-jobs:
    uses: irajatpandey/platform-workflows/.github/workflows/python-ci.yml@master
    with:
      python-version: ${{ inputs.python-version }}
      exclusions: ${{ inputs.exclusions }}
      run-sonar: ${{ inputs.run-sonar == true || inputs.run-sonar == '' }}
    secrets: inherit
```

---

## ⚙️ Workflow Inputs & Secrets

### `python-ci.yml` Inputs

| Input | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `python-version` | `string` | `"3.12"` | Python version to set up |
| `java-version` | `string` | `"17"` | Java JDK version (required by SonarScanner) |
| `run-sonar` | `boolean` | `true` | Toggle SonarCloud SAST analysis |
| `exclusions` | `string` | `""` | File exclusion patterns for SonarCloud |
| `sonar-project-key` | `string` | `""` *(auto)* | Defaults to `{owner}_{repo}` |
| `sonar-project-name` | `string` | `""` *(auto)* | Defaults to `{repo}` |
| `sonar-organization` | `string` | `""` *(auto)* | Defaults to `{owner}` |
| `sonar-sources` | `string` | `"."` | Source code directory for analysis |

### Secrets Required

| Secret | Description |
| :--- | :--- |
| `SONAR_TOKEN` | SonarCloud User Access Token (configured in caller repository secrets) |

---

## 🛡️ SonarCloud Composite Action (`sonarqube`)

The `sonarqube` composite action ([.github/actions/steps/sonarqube/action.yml](.github/actions/steps/sonarqube/action.yml)) manages SAST analysis for SonarCloud:

- **Non-destructive configuration**: Preserves pre-existing repository `sonar-project.properties` (test paths, custom exclusions, and xunit/coverage report paths).
- **Pre-scan validation**: Validates token presence and API authorization against SonarCloud before starting the scanner.
- **SonarCloud Engine**: Utilizes `SonarSource/sonarcloud-github-action@v3` with Quality Gate status waiting enabled (`-Dsonar.qualitygate.wait=true`).

### Service `sonar-project.properties` Setup

Place a `sonar-project.properties` in your repository root:

```properties
sonar.host.url=https://sonarcloud.io
sonar.projectKey=irajatpandey_Learning-Github-Actions
sonar.organization=irajatpandey
sonar.branch.name=master
sonar.sources=basic-flask-project/app.py,basic-flask-project/static,basic-flask-project/templates
sonar.tests=basic-flask-project/tests
sonar.exclusions=**/.venv/**,**/.pytest_cache/**,**/__pycache__/**
sonar.coverage.exclusions=basic-flask-project/tests/**
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.xunit.reportPath=test-results.xml
```

> **Note for SonarCloud Free Plan**: On SonarCloud Free / Open-Source plans, feature branch analysis requires `sonar.branch.name=master` to route analysis to the main branch.

---

## 🤝 Contributing & Maintenance

When making updates to reusable workflows or composite actions:

1. Test changes on a feature branch (e.g. `@feature-branch` reference in caller workflows).
2. Ensure backward compatibility for existing service repositories.
3. Merge PRs into `master` branch.