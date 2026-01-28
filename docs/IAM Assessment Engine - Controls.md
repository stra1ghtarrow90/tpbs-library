
#  IAM Assessment Engine — **First 20 Core Controls**

(Designed for **Microsoft Entra ID** + AD hybrids)

---

## Domain 1: Authentication Strength (AUTH)

### **IAM-AUTH-001 — MFA enforced for all users**

**Objective:** Prevent credential-only compromise
**Risk:** Account takeover
**Evidence:** MFA registration + enforcement
**Scoring:**

* 0 → MFA disabled for users
* 1 → MFA enabled but exceptions exist
* 2 → MFA enforced for all users (incl. guests)

---

### **IAM-AUTH-002 — Phishing-resistant MFA for privileged roles**

**Objective:** Defend against token/session theft
**Risk:** Privilege escalation
**Evidence:** Auth strength / FIDO2 / CBA
**Scoring:**

* 0 → Push/SMS allowed
* 1 → Number matching only
* 2 → FIDO2 / CBA enforced

---

### **IAM-AUTH-003 — Legacy authentication blocked**

**Objective:** Remove MFA bypass paths
**Risk:** Silent compromise
**Evidence:** CA policy + sign-in logs
**Scoring:**

* 0 → Legacy auth enabled
* 1 → Partially blocked
* 2 → Fully blocked tenant-wide

---

### **IAM-AUTH-004 — Authentication strength aligned to risk**

**Objective:** Match auth strength to access sensitivity
**Risk:** Over-trusting weak auth
**Evidence:** CA policies using auth strength
**Scoring:**

* 0 → Single global policy
* 1 → Multiple policies, inconsistent
* 2 → Risk-based auth strength enforced

---

##  Domain 2: Conditional Access (CA)

### **IAM-CA-001 — Conditional Access enforced for all access**

**Objective:** Ensure every sign-in is evaluated
**Risk:** Policy bypass
**Evidence:** CA policy coverage
**Scoring:**

* 0 → CA limited / optional
* 1 → CA covers users only
* 2 → CA covers users + guests + apps

---

### **IAM-CA-002 — Location & device context enforced**

**Objective:** Reduce stolen-credential abuse
**Risk:** External compromise
**Evidence:** Named locations / device filters
**Scoring:**

* 0 → No context checks
* 1 → Location OR device checks
* 2 → Location AND device enforced

---

### **IAM-CA-003 — High-risk sign-ins blocked or remediated**

**Objective:** Detect and respond to identity attacks
**Risk:** Account takeover
**Evidence:** Identity Protection policies
**Scoring:**

* 0 → Risk signals unused
* 1 → Alert-only
* 2 → Auto-block or force reset

---

##  Domain 3: Privileged Access (PRIV)

### **IAM-PRIV-001 — Privileged roles are time-bound**

**Objective:** Reduce standing access
**Risk:** Persistent compromise
**Evidence:** PIM role assignments
**Scoring:**

* 0 → Permanent admins exist
* 1 → Mixed permanent / eligible
* 2 → All privileged roles eligible only

---

### **IAM-PRIV-002 — Privileged access requires MFA on activation**

**Objective:** Prevent privilege abuse
**Risk:** Role hijacking
**Evidence:** PIM settings
**Scoring:**

* 0 → No MFA on activation
* 1 → MFA optional
* 2 → MFA mandatory

---

### **IAM-PRIV-003 — Privileged role approvals enforced**

**Objective:** Add human control to elevation
**Risk:** Insider abuse
**Evidence:** PIM approval workflow
**Scoring:**

* 0 → No approval
* 1 → Approval for some roles
* 2 → Approval for all high-risk roles

---

### **IAM-PRIV-004 — Break-glass accounts secured & tested**

**Objective:** Ensure emergency access without abuse
**Risk:** Irrecoverable lockout or misuse
**Evidence:** Account config + test logs
**Scoring:**

* 0 → No break-glass
* 1 → Exists but untested / weak
* 2 → Tested, monitored, excluded safely

---

##  Domain 4: Identity Lifecycle (LCM)

### **IAM-LCM-001 — Joiner / mover / leaver automation**

**Objective:** Remove human lag
**Risk:** Orphaned access
**Evidence:** Provisioning workflows
**Scoring:**

* 0 → Manual processes
* 1 → Partial automation
* 2 → Fully automated lifecycle

---

### **IAM-LCM-002 — Leaver access revoked within SLA**

**Objective:** Minimise post-employment risk
**Risk:** Ex-employee access
**Evidence:** Disable timestamps
**Scoring:**

* 0 → No defined SLA
* 1 → SLA exists but breached
* 2 → Consistently met SLA

---

### **IAM-LCM-003 — Guest access lifecycle enforced**

**Objective:** Prevent eternal guest accounts
**Risk:** External persistence
**Evidence:** Guest expiry policies
**Scoring:**

* 0 → Guests never expire
* 1 → Manual review
* 2 → Auto-expiry enforced

---

##  Domain 5: Workload Identity (WORK)

### **IAM-WORK-001 — Workloads use managed identities**

**Objective:** Eliminate secrets
**Risk:** Credential leakage
**Evidence:** App registrations
**Scoring:**

* 0 → Secrets everywhere
* 1 → Mixed secrets & MI
* 2 → Managed identity only

---

### **IAM-WORK-002 — Secrets & certs rotated automatically**

**Objective:** Reduce blast radius
**Risk:** Long-lived compromise
**Evidence:** Credential expiry config
**Scoring:**

* 0 → No rotation
* 1 → Manual rotation
* 2 → Automated rotation

---

### **IAM-WORK-003 — Workload permissions are least-privilege**

**Objective:** Limit service blast radius
**Risk:** Lateral movement
**Evidence:** App role assignments
**Scoring:**

* 0 → Directory-wide perms
* 1 → Over-permissioned apps
* 2 → Minimal scoped access

---

##  Domain 6: Monitoring & Detection (MON)

### **IAM-MON-001 — Identity events centrally logged**

**Objective:** Enable detection & forensics
**Risk:** Blind compromise
**Evidence:** Log forwarding config
**Scoring:**

* 0 → Logs not retained
* 1 → Logs retained locally
* 2 → Logs sent to SIEM

---

### **IAM-MON-002 — Alerts on privileged & risky activity**

**Objective:** Detect abuse early
**Risk:** Undetected escalation
**Evidence:** Alert rules
**Scoring:**

* 0 → No alerts
* 1 → Alerts without response
* 2 → Alerts with runbooks

---

