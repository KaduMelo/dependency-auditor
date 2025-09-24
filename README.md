# Dependency Auditor

**Dependency Auditor** is a reusable GitHub Action designed to help developers and teams analyze and audit their project dependencies across multiple ecosystems.  

It detects outdated, deprecated, or legacy libraries, checks for security vulnerabilities (CVE-based), evaluates license risks, and generates structured, actionable audit reports. Each report is automatically saved as a Markdown file and delivered via pull request in the target repository.

## ✨ Features
- Works across multiple package managers (`npm`, `pip`, `go`, `cargo`, `maven`, `gradle`, `composer`, etc.).
- Identifies outdated, deprecated, and unmaintained dependencies.
- Detects vulnerabilities with CVE references.
- Evaluates license compatibility and potential legal risks.
- Highlights critical files relying on risky dependencies.
- Generates a comprehensive **Dependency Audit Report** in Markdown.
- Opens an automated Pull Request with the audit report.

## 🚀 How It Works
1. Install the workflow in your project and call the reusable action.
2. The action runs the dependency auditor agent (powered by LLM + LangChain).
3. A complete audit is performed using dependency manifests and lockfiles.
4. The report is generated and pushed to your repository under `/docs/agents/dependency-auditor/`.
5. A pull request is created with the latest findings.

## 🔒 Security
The action requires an `OPENAI_API_KEY` secret, which should only be configured in the **central audit repository**.  
Projects that consume this action inherit the secret without exposing it publicly.

## 📦 Example Usage

```yaml
name: Project Security Audit

on:
  workflow_dispatch:
  schedule:
    - cron: "0 3 * * 1" # Every Monday at 3AM

jobs:
  audit:
    uses: your-org/dependency-auditor/.github/workflows/audit.yml@v1
    secrets: inherit
