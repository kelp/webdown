# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | :white_check_mark: |
| < 0.4.0 | :x:                |

## Dependency Security

Webdown takes security seriously. We implement multiple layers of protection:

1. **GitHub Dependabot**: Automatically scans dependencies for vulnerabilities and creates pull requests to address them.
2. **Safety Scanning**: Runs in our CI/CD pipeline to check dependencies against the Safety DB of known vulnerabilities.
3. **Regular Audits**: We schedule weekly security scans to proactively identify potential issues.

## Reporting a Vulnerability

If you discover a security vulnerability in Webdown, please follow these steps:

1. **Do Not Disclose Publicly**: Please don't disclose security vulnerabilities publicly until we've had a chance to address them.
2. **Report via Email**: Send details of the vulnerability to [kelp@plek.org](mailto:kelp@plek.org) with subject "Webdown Security Vulnerability".
3. **Include Details**: Please include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

## Response Process

After receiving a security report, we will:

1. **Acknowledge**: Confirm receipt within 48 hours.
2. **Investigate**: Assess the vulnerability and determine its impact.
3. **Fix**: For confirmed vulnerabilities, develop and test a fix.
4. **Release**: Issue a security release and credit the reporter (unless anonymity is requested).

## Security Best Practices for Users

1. **Keep Updated**: Always use the latest version of Webdown.
2. **Check Dependencies**: Regularly audit your own dependencies if you include Webdown in your projects.
3. **Careful Input Handling**: Be mindful when processing untrusted URL inputs with Webdown.

Thank you for helping keep Webdown secure!
