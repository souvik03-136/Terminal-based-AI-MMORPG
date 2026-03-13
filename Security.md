# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 1.x.x | ✅ Yes |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please email **security@yourdomain.com** with:

1. A clear description of the vulnerability
2. Steps to reproduce it
3. Potential impact
4. Any suggested fixes (optional but appreciated)

We will acknowledge receipt within **48 hours** and provide a timeline for a fix within **7 days** for critical issues.

## Scope

In scope for security reports:
- Remote code execution via crafted player input
- API key exposure or leakage
- Denial of service through crafted commands
- Cross-player data leakage (AI context contamination)
- Authentication bypass (if auth is added in future)

Out of scope:
- Bugs without security impact (use the Bug Report issue template)
- Issues in dependencies not triggered by this project

## Responsible Disclosure

We follow responsible disclosure: we will credit researchers in the release notes (with their permission) once the fix is deployed.