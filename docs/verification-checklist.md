# 🔍 Vulcan — Penetration Testing Verification Checklist

A structured checklist for confirming that each phase of a Vulcan-driven assessment produced valid, complete, and actionable results. Inspired by the agentskills.io pattern of "how to confirm success" verification sections.

---

## 1. Reconnaissance Verification

| # | Check | How to Verify | Expected Result | Pass? |
|---|-------|--------------|-----------------|-------|
| 1.1 | Subdomain discovery | Compare discovered subdomains against certificate transparency logs | All CT-logged subdomains found |  |
| 1.2 | Port scan accuracy | Verify open ports with manual `nmap -sV` on sample hosts | Services match Vulcan's findings |  |
| 1.3 | Technology fingerprinting | Cross-reference with Wappalyzer or manual inspection | Tech stack correctly identified |  |
| 1.4 | DNS enumeration | Validate discovered DNS records via `dig` or `nslookup` | Records confirmed independently |  |
| 1.5 | OSINT completeness | Manual search for target on Shodan, Censys | No major assets missed |  |

## 2. Vulnerability Scanning Verification

| # | Check | How to Verify | Expected Result | Pass? |
|---|-------|--------------|-----------------|-------|
| 2.1 | Finding accuracy | Manually confirm top 5 findings | ≥80% true positive rate |  |
| 2.2 | Severity alignment | Compare CVSS scores with NVD entries | Scores match or justified deviation |  |
| 2.3 | Template coverage | Review Nuclei templates used vs. target tech stack | Relevant templates were selected |  |
| 2.4 | False positive rate | Manually test 10 random "informational" findings | <20% are noise |  |
| 2.5 | Scanner diversity | Check which tools contributed findings | ≥3 different tools produced results |  |

## 3. Exploitation Verification

| # | Check | How to Verify | Expected Result | Pass? |
|---|-------|--------------|-----------------|-------|
| 3.1 | Exploit success | Replay exploitation steps manually | Same result achieved |  |
| 3.2 | Evidence capture | Check screenshots and command output | Clear proof of exploitation |  |
| 3.3 | Impact assessment | Verify what data/access was obtained | Impact accurately described |  |
| 3.4 | Scope compliance | Review all exploitation targets | No out-of-scope systems touched |  |
| 3.5 | Cleanup verification | Check for leftover shells, files, accounts | Target restored to pre-test state |  |

## 4. Authentication & Access Testing

| # | Check | How to Verify | Expected Result | Pass? |
|---|-------|--------------|-----------------|-------|
| 4.1 | Credential testing | Verify lockout thresholds were respected | No accounts locked out |  |
| 4.2 | Password policy check | Test discovered policy against NIST guidelines | Policy gaps documented |  |
| 4.3 | Session management | Verify session tokens for randomness, expiry | Weaknesses accurately reported |  |
| 4.4 | MFA testing | Confirm MFA bypass claims | Bypass reproducible or correctly flagged |  |
| 4.5 | Privilege escalation | Replay escalation path independently | Same access level achieved |  |

## 5. Web Application Testing

| # | Check | How to Verify | Expected Result | Pass? |
|---|-------|--------------|-----------------|-------|
| 5.1 | SQL Injection | Replay SQLMap with same parameters | Injection confirmed |  |
| 5.2 | XSS validation | Test payloads in browser manually | Alert/DOM manipulation confirmed |  |
| 5.3 | SSRF/IDOR | Verify access to unauthorized resources | Unauthorized access reproduced |  |
| 5.4 | File upload | Retest upload bypass with known malicious file | Bypass confirmed |  |
| 5.5 | API security | Test API endpoints with modified tokens/params | Findings reproduced |  |

## 6. Report Quality Verification

| # | Check | How to Verify | Expected Result | Pass? |
|---|-------|--------------|-----------------|-------|
| 6.1 | Executive summary | Non-technical stakeholder review | Understandable without jargon |  |
| 6.2 | Finding detail | Each finding has: description, impact, evidence, remediation | All 4 sections present |  |
| 6.3 | Remediation quality | Check fixes against OWASP guidance | Recommendations are actionable and correct |  |
| 6.4 | Evidence chain | Follow evidence from finding to proof | Clear, verifiable chain |  |
| 6.5 | Severity accuracy | Cross-reference with manual assessment | Severity appropriate for context |  |
| 6.6 | Completeness | All tested areas represented in report | No orphaned test results |  |

## 7. Operational Verification

| # | Check | How to Verify | Expected Result | Pass? |
|---|-------|--------------|-----------------|-------|
| 7.1 | Scan duration | Compare with expected time for scope | Within reasonable bounds |  |
| 7.2 | Target impact | Monitor target during/after scan | No service degradation |  |
| 7.3 | Data handling | Verify sensitive data storage/transmission | Encrypted and access-controlled |  |
| 7.4 | Log integrity | Review Vulcan execution logs | Complete, unmodified log trail |  |
| 7.5 | Reproducibility | Re-run same assessment | Consistent findings (±10%) |  |

---

## Using This Checklist

### Before the Assessment
1. Define scope and rules of engagement
2. Confirm authorization documentation
3. Set up monitoring on target systems
4. Establish communication channels

### During the Assessment
1. Spot-check findings as they emerge
2. Monitor target health
3. Document any scope changes or incidents

### After the Assessment
1. Complete all verification sections above
2. Calculate overall confidence: `verified_checks / total_checks × 100`
3. Flag any checks that failed for investigation
4. Include verification summary in final report

### Confidence Scoring

| Score | Rating | Action |
|-------|--------|--------|
| 90-100% | ✅ High Confidence | Report ready for delivery |
| 70-89% | ⚠️ Moderate Confidence | Investigate failed checks before delivery |
| <70% | ❌ Low Confidence | Re-run affected assessment phases |
