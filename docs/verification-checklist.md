# Vulcan Penetration Testing Verification Checklists

## Pre-Engagement
- [ ] Written authorization obtained and documented
- [ ] Scope clearly defined (IP ranges, domains, exclusions)
- [ ] Rules of engagement agreed (testing hours, DoS restrictions)
- [ ] Emergency contacts exchanged
- [ ] Backup/rollback procedures confirmed with client

## Reconnaissance
- [ ] DNS enumeration completed (subdomains, MX, NS, TXT records)
- [ ] OSINT gathering performed (employees, technologies, leaked credentials)
- [ ] Network range identification confirmed
- [ ] Service fingerprinting matches known asset inventory
- [ ] Attack surface map reviewed and validated

## Scanning & Enumeration
- [ ] Port scan results verified (no false positives from WAF/IDS)
- [ ] Service versions confirmed with banner grabbing
- [ ] Web application technology stack identified
- [ ] Authentication endpoints enumerated
- [ ] API endpoints discovered and documented

## Vulnerability Assessment
- [ ] Automated scan results triaged and validated
- [ ] False positives identified and removed
- [ ] Vulnerabilities prioritized by exploitability + business impact
- [ ] CVE references verified against NVD
- [ ] CVSS scores calculated with environmental metrics

## Exploitation
- [ ] Each exploit attempt logged with timestamp
- [ ] Exploitation limited to authorized scope
- [ ] Evidence captured (screenshots, command output, hashes)
- [ ] No destructive actions performed
- [ ] Lateral movement paths documented

## Post-Exploitation
- [ ] Privilege escalation paths documented
- [ ] Data access scope assessed (without exfiltration)
- [ ] Persistence mechanisms identified (not installed)
- [ ] Network pivot opportunities mapped
- [ ] All artifacts cleaned up

## Reporting
- [ ] Executive summary written in business language
- [ ] Technical findings include reproduction steps
- [ ] CVSS scores and risk ratings assigned
- [ ] Remediation recommendations prioritized
- [ ] Evidence properly sanitized (no client PII in screenshots)
- [ ] Report delivered via encrypted channel
