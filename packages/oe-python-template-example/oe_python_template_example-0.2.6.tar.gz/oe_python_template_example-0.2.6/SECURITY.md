# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in OE Python Template Example, please [report it here](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/security/advisories/new).

We take all security reports seriously. Upon receiving a security report, we will:
1. Confirm receipt of the vulnerability report
2. Investigate the issue
3. Work on a fix
4. Release a security update

## Supported Versions

We currently provide security updates for the latest minor version.

## Automated Security Analysis

OE Python Template Example employs several automated tools to continuously monitor and improve security:

### 1. Dependency Vulnerability Scanning

a. **GitHub Dependabot**: Monitors dependencies for known vulnerabilities and automatically creates pull requests to update them when security issues are found. [Dependendabot alerts](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/security/dependabot) published.
b. **Renovate Bot**: Automatically creates pull requests to update dependencies when new versions are available, with a focus on security patches. [Dependency Dashboard](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/issues?q=is%3Aissue%20state%3Aopen%20Dependency%20Dashboard) published.
c. **pip-audit**: Regularly scans Python dependencies for known vulnerabilities using data from the Python Advisory Database. `vulnerabilities.json` published [per release](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/releases).

### 2. Dependency Compliance

a. **cyclonedx-py**: Generates a Software Bill of Materials (SBOM) in SPDX format, listing all components and dependencies used in the project. `sbom.json` (SPDX format) published [per release](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/releases).
b. **pip-licenses**: Exports the licenses of all dependencies to ensure compliance with licensing requirements and avoid using components with problematic licenses. `licenses.csv`, `licenses.json` and `licenses_grouped.json` published [per release](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/releases).

### 3. Static Code Analysis

a. **GitHub CodeQL**: Analyzes code for common vulnerabilities and coding errors using GitHub's semantic code analysis engine. [Code scanning results](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/security/code-scanning) published.
b. **SonarQube**: Performs comprehensive static code analysis to detect code quality issues, security vulnerabilities, and bugs. [Security hotspots](https://sonarcloud.io/project/security_hotspots?id=helmut-hoffer-von-ankershoffen_oe-python-template-example) published.

### 4. Secret Detection
a. **GitHub Secret scanning**: Automatically scans for secrets in the codebase and alerts if any are found. [Secret scanning alerts](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/security/secret-scanning) published.
b. **Yelp/detect-secrets**: Pre-commit hook and automated scanning to prevent accidental inclusion of secrets or sensitive information in commits. [Pre-Commit hook](https://github.com/helmut-hoffer-von-ankershoffen/oe-python-template-example/blob/main/.pre-commit-config.yaml) published.

## Security Best Practices

We follow these security best practices:
1. Regular dependency updates
2. Comprehensive test coverage
3. Code review process for changes by external contributors
4. Automated CI/CD pipelines including security checks
5. Adherence to Python security best practices

We promote security awareness among contributors and users:
1. We indicate security as a priority in our
   [code style guide](CODE_STYLE.md), to be followed by human and agentic
   contributors as mandatory
2. We publish our security posture in SECURITY.md (this document), encouraring
   users to report vulnerabilities.

## Security Compliance

For questions about security compliance or for more details about our security practices, please contact helmuthva@gmail.com.
