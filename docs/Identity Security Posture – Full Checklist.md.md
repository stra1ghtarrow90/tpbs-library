
# Identity Security Posture – Full Checklist

---

## SECTION 1 — Entra ID (Azure AD) Security Posture

### 1.1 Authentication & MFA

**Coverage**

* ☐ 100% of users covered by MFA (incl. guests)
* ☐ 100% of admin roles covered by MFA
* ☐ Break-glass accounts exist (≤2)
* ☐ Break-glass accounts excluded *only* where necessary
* ☐ Break-glass accounts are monitored & alerted on

**Authentication strength**

* ☐ Authentication Methods Policy configured (not legacy per-user MFA)
* ☐ SMS disabled or restricted
* ☐ Voice disabled
* ☐ App-based MFA preferred
* ☐ Passwordless enabled (WHfB / FIDO2)
* ☐ Phishing-resistant MFA enforced for privileged roles

**Legacy authentication**

* ☐ Legacy authentication blocked tenant-wide
* ☐ SMTP AUTH disabled or exception-documented
* ☐ POP / IMAP disabled
* ☐ No CA policies relying on “legacy MFA”

**Red flags**

* MFA enforced “for admins only”
* Any legacy protocol still allowed
* MFA exclusions larger than break-glass

---

### 1.2 Conditional Access (CA)

**Policy design**

* ☐ Policies apply to *All cloud apps*
* ☐ Policies use “All users” with exclusions (not allowlists)
* ☐ No overlapping or conflicting CA logic
* ☐ Named locations limited and reviewed

**Core CA policies**

* ☐ Require MFA for all users
* ☐ Block legacy authentication
* ☐ Require compliant or hybrid-joined device
* ☐ Require MFA for admin roles
* ☐ Require phishing-resistant MFA for admins
* ☐ Block high-risk sign-ins
* ☐ Block high-risk users

**Operational**

* ☐ CA policies documented
* ☐ CA changes logged and monitored
* ☐ CA insights reviewed quarterly

**Red flags**

* App-specific CA sprawl
* “Temporary” exclusions still present
* CA policies in report-only forever

---

### 1.3 Privileged Access & Roles

**Role hygiene**

* ☐ Global Admin count ≤5
* ☐ No standing Global Admins
* ☐ PIM enabled for all privileged roles
* ☐ PIM approval required for GA
* ☐ Activation justification required
* ☐ Activation duration ≤4 hours

**Scope minimisation**

* ☐ Use least-privileged roles (not GA)
* ☐ Separate admin and user accounts
* ☐ No synced on-prem admins holding Entra roles

**Red flags**

* Permanent GA assignments
* Admins using day-to-day accounts
* Shared admin accounts

---

### 1.4 Identity Protection & Monitoring

* ☐ Identity Protection licensed & enabled
* ☐ Risk-based sign-in policies enforced
* ☐ Risk-based user policies enforced
* ☐ Password reset on high-risk users
* ☐ Sign-in logs retained ≥30 days
* ☐ Alerts routed to SIEM / SOC

---

### 1.5 Devices & Endpoint Trust

* ☐ Device compliance enforced via CA
* ☐ Hybrid join required for internal apps
* ☐ Intune compliance policies enforced
* ☐ No “browser-only MFA” loopholes

---

### 1.6 External Identities (B2B)

* ☐ Guest MFA enforced
* ☐ Guest access restricted
* ☐ Guest lifecycle review enabled
* ☐ Guest admin role assignment blocked

---

## SECTION 2 — Active Directory Security Posture

### 2.1 Tiering & Privilege Separation

**Tier model**

* ☐ Tier-0 (DCs, ADFS, Entra Connect) defined
* ☐ Tier-1 (servers) defined
* ☐ Tier-2 (workstations) defined
* ☐ Admins restricted to their tier only

**Admin separation**

* ☐ Separate admin accounts per tier
* ☐ No DA accounts logging into Tier-2
* ☐ Interactive logons restricted via GPO
* ☐ PAWs / SAWs used for Tier-0

**Red flags**

* DA logons on laptops
* Shared admin accounts
* No tier enforcement

---

### 2.2 Credential Security

* ☐ NTLM restricted or disabled
* ☐ SMB signing enforced
* ☐ LDAP signing enforced
* ☐ Credential Guard enabled
* ☐ LSASS protection enabled
* ☐ Cached credentials minimised

---

### 2.3 Domain Admin & Tier-0

* ☐ Domain Admins ≤5
* ☐ No service accounts in Domain Admins
* ☐ No scheduled tasks running as DA
* ☐ No delegation on DA accounts
* ☐ SIDHistory reviewed and minimal

---

### 2.4 Service Accounts

* ☐ All service accounts inventoried
* ☐ No service accounts with DA rights
* ☐ gMSA used where possible
* ☐ SPNs reviewed for kerberoasting risk
* ☐ Password rotation enforced
* ☐ No interactive logon rights

**Red flags**

* Static passwords
* SPNs + weak passwords
* “Temporary” service accounts

---

### 2.5 Attack Path Analysis (MANDATORY)

* ☐ BloodHound run
* ☐ Shortest path to Domain Admin documented
* ☐ ACL abuse identified
* ☐ Delegation abuse identified
* ☐ Unconstrained delegation eliminated
* ☐ Findings tracked to remediation

If this is unchecked → **you do not know your AD posture**

---

### 2.6 Hardening & Hygiene

* ☐ CIS benchmark reviewed
* ☐ Legacy OS removed
* ☐ SYSVOL secured
* ☐ GPO permissions reviewed
* ☐ AdminSDHolder understood & monitored

---

## SECTION 3 — Hybrid Identity (Entra + AD)

### 3.1 Entra Connect / Sync

* ☐ Sync account is least-privileged
* ☐ No Domain Admin rights
* ☐ Sync server treated as Tier-0
* ☐ PTA agents hardened
* ☐ Seamless SSO assessed

---

### 3.2 Hybrid Attack Surface

* ☐ Cloud admins not synced from AD
* ☐ On-prem service accounts not synced unnecessarily
* ☐ Token theft scenarios considered
* ☐ Password hash sync risks understood

---

## SECTION 4 — Detection, Response & Drift

### 4.1 Monitoring

* ☐ Admin role changes alerted
* ☐ MFA bypass alerts configured
* ☐ CA policy changes alerted
* ☐ Break-glass usage alerted
* ☐ Risky sign-ins triaged

---

### 4.2 Review Cadence

* ☐ Monthly Entra Secure Score review
* ☐ Quarterly BloodHound delta analysis
* ☐ Quarterly service account review
* ☐ Annual tiering validation

---

## SECTION 5 — Scoring & Reporting

Score each domain 0–10:

| Domain               | Score | Notes |
| -------------------- | ----- | ----- |
| Entra Authentication |       |       |
| Conditional Access   |       |       |
| Privileged Access    |       |       |
| AD Tiering           |       |       |
| AD Attack Paths      |       |       |
| Hybrid Controls      |       |       |

**Overall posture**

* 🟢 8–10 = Strong
* 🟡 5–7 = Moderate risk
* 🔴 <5 = Material identity risk

---

## Executive Truth (the bit most miss)

> **If an attacker compromises AD, they can reach Entra.
> If they compromise Entra, they can often pivot to AD.
> Identity is one attack surface.**

---