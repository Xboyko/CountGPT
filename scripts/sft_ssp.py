"""SSP control-implementation statement examples for CountGPT SFT."""

from __future__ import annotations

CAVEAT = "This is a draft, not assessor-validated."


def _stmt(instruction: str, body: str) -> dict:
    return {"instruction": instruction, "output": body.rstrip() + "\n\n" + CAVEAT}


def examples() -> list[dict]:
    return [
        _stmt(
            "Write a control implementation statement for AU-2 (Event Logging) for a DoD web application, specific enough for an assessor to test.",
            "[System Name] logs security-relevant events using Splunk Enterprise Security as the centralized logging and SIEM platform.\n\n"
            "Events Logged: The system logs authentication attempts (success and failure), privilege escalation events, account creation/modification/deletion, and access to audit logs themselves, in accordance with the Audit and Accountability Policy v1.4.\n\n"
            "Log Review: The Security Operations Engineer reviews automated Splunk alerts daily, with a full manual audit log review conducted weekly by the ISSO.\n\n"
            "Log Retention: Logs are retained in Splunk for 90 days in hot storage and archived to cold storage for an additional 12 months, per the organization's Records Retention Schedule.\n\n"
            "Customer Responsibility: Not applicable - this control is fully implemented and owned by the system provider; no customer-side action is required.",
        ),
        _stmt(
            "Write a control implementation statement for IA-2 (Identification and Authentication) for a DoD system requiring multi-factor authentication.",
            "[System Name] enforces multi-factor authentication (MFA) for all user access using a DoD Common Access Card (CAC) as the primary authentication factor, in combination with a PIN, in accordance with DoD 8500-series policy.\n\n"
            "Privileged Access: Administrator and privileged accounts require CAC-based authentication with no exceptions; password-only authentication is disabled at the identity provider level.\n\n"
            "Remote Access: Remote connections additionally require a DoD-approved VPN client prior to CAC authentication, ensuring MFA is enforced both at the network and application layer.\n\n"
            "Exception Handling: Any request for a temporary local account bypassing CAC authentication (e.g., for a new employee awaiting card issuance) requires ISSO approval, is time-limited to 5 business days, and is logged and reviewed at the next audit cycle.\n\n"
            "Customer Responsibility: Customer agencies are responsible for ensuring their personnel are issued valid, unexpired CAC credentials prior to requesting system access.",
        ),
        _stmt(
            "Write a control implementation statement for SC-7 (Boundary Protection) for a DoD cloud-hosted system.",
            "[System Name] enforces boundary protection through a combination of a cloud-native firewall (AWS Security Groups) and a dedicated web application firewall (WAF) positioned at the network perimeter.\n\n"
            "Ingress/Egress Control: All inbound traffic is denied by default; only explicitly required ports and protocols (HTTPS/443) are permitted. Outbound traffic is restricted to approved destinations required for system functionality.\n\n"
            "Segmentation: The production environment is logically segmented from staging and development environments using separate Virtual Private Clouds (VPCs), with no direct network path between them.\n\n"
            "Monitoring: All boundary traffic logs are forwarded to the centralized Splunk SIEM for real-time monitoring and alerting on anomalous traffic patterns.\n\n"
            "Customer Responsibility: Not applicable - boundary protection is fully implemented and owned by the system provider at the infrastructure layer.",
        ),
        _stmt(
            "Write a control implementation statement for CM-6 (Configuration Settings) for a DoD Windows Server environment.",
            "[System Name] establishes and enforces secure configuration baselines using the applicable DISA Security Technical Implementation Guide (STIG) for Windows Server, currently version [STIG version].\n\n"
            "Baseline Enforcement: Group Policy Objects (GPOs) enforce STIG-required settings across all domain-joined servers, with configuration compliance validated using SCAP-compliant scanning tools on a monthly basis.\n\n"
            "Deviation Handling: Any required deviation from a STIG setting due to operational necessity is documented as a Security Requirements Traceability Matrix (SRTM) exception, approved by the ISSO, and tracked as a POA&M item if it introduces residual risk.\n\n"
            "Change Control: Configuration changes to baseline settings require submission through the Configuration Control Board (CCB) prior to implementation in production.\n\n"
            "Customer Responsibility: Not applicable - configuration management is fully implemented and owned by the system provider.",
        ),
        _stmt(
            "Write a control implementation statement for IR-6 (Incident Reporting) for a DoD system.",
            "[System Name] reports security incidents in accordance with the organization's Incident Response Plan v2.0 and applicable DoD incident reporting timelines.\n\n"
            "Detection and Initial Reporting: Security-relevant events detected through Splunk SIEM alerting are triaged by the Security Operations Engineer within 1 hour of alert generation. Confirmed incidents are reported to the ISSO immediately upon confirmation.\n\n"
            "Formal Reporting Timeline: Confirmed incidents are reported to US-CERT (or the appropriate DoD reporting channel) within the timeframe required by applicable DoD Continuous Monitoring guidance, with initial notification followed by a full incident report within the required follow-up window.\n\n"
            "Internal Escalation: The ISSO notifies the ISSM and System Owner of any confirmed incident within 4 hours of confirmation, regardless of severity, to ensure appropriate visibility up the chain.\n\n"
            "Documentation: All incident details, timeline, and remediation actions are logged and retained per the Records Retention Schedule, and referenced in the POA&M if the incident reveals a previously undocumented control gap.",
        ),
        _stmt(
            "Write a control implementation statement for RA-5 (Vulnerability Monitoring and Scanning) for a DoD system using ACAS.",
            "[System Name] undergoes vulnerability scanning using the DoD-mandated ACAS (Assured Compliance Assessment Solution) suite, built on Tenable Nessus, in accordance with DoD scanning requirements.\n\n"
            "Scan Frequency: Credentialed ACAS scans are conducted monthly against all in-scope hosts, with results aggregated in Tenable.sc for centralized review.\n\n"
            "Finding Triage: The ISSO reviews new scan results within 5 business days of each scan cycle, validates findings against known false positives, and creates or updates POA&M entries in eMASS for any new confirmed High or Moderate findings.\n\n"
            "Remediation Tracking: Remediation timelines follow common severity-based windows (30/90/180 days for High/Moderate/Low respectively), tracked via the POA&M until closure is validated by a follow-up scan.\n\n"
            "Customer Responsibility: Not applicable - vulnerability scanning is fully implemented and owned by the system provider.",
        ),
        _stmt(
            "Write a control implementation statement for CP-9 (System Backup) for a DoD system.",
            "[System Name] performs system backups using [backup solution] in accordance with the organization's Contingency Plan v1.2.\n\n"
            "Backup Schedule: Full system backups are performed weekly, with incremental backups performed daily, capturing user-level and system-level information required to restore full system functionality.\n\n"
            "Backup Storage: Backups are encrypted at rest and stored in a geographically separate location from the primary system to ensure availability in the event of a site-level failure.\n\n"
            "Testing: Backup restoration is tested quarterly by the System Administrator to validate recoverability, with results documented and retained as evidence for Continuous Monitoring review.\n\n"
            "Customer Responsibility: Not applicable - backup operations are fully implemented and owned by the system provider.",
        ),
        _stmt(
            "Write an SSP implementation statement for AC-2 Account Management for a FedRAMP Moderate SaaS app using a named IdP.",
            "[System Name] manages user accounts through [IdP name] as the authoritative identity store.\n\n"
            "Provisioning: Account requests are submitted via [ticketing system], approved by the user's supervisor and the ISSO, and created with role-based groups that map to application entitlements. Shared generic logins are not used for human users.\n\n"
            "Review: The ISSO and system owner recertify accounts quarterly; disabled or unused accounts (no successful logon in [organization-defined period]) are disabled automatically by the IdP policy.\n\n"
            "Termination: HR or contracting offboarding tickets trigger same-day IdP disablement. Privileged group membership is reviewed monthly.\n\n"
            "Customer Responsibility: Customer tenant admins must submit joiner/mover/leaver tickets and must not create local bypass accounts except the documented break-glass procedure.",
        ),
        _stmt(
            "Write a control implementation statement for AC-3 Access Enforcement for a DoD web application with role-based access.",
            "[System Name] enforces authorization in the application layer using role-based access control mapped to [IdP] groups.\n\n"
            "Roles: Named roles (for example read-only analyst, application administrator) are listed in the role matrix [document name]. Object-level checks occur on every request; hiding a menu is not the only control.\n\n"
            "Service accounts: Non-person accounts are assigned the minimum API scopes required and cannot use interactive user roles.\n\n"
            "Evidence: An assessor can create a test user in each role (or review existing test IDs), attempt a cross-role URL, and see a deny plus an audit event (AU-2).\n\n"
            "Customer Responsibility: Customers assign personnel to the correct group; they do not receive a 'superuser' tenant role unless documented.",
        ),
        _stmt(
            "Write an implementation statement for AC-6 Least Privilege on a Windows/AD privileged access model.",
            "[System Name] separates standard user and privileged directory roles.\n\n"
            "Implementation: Day-to-day work uses non-privileged accounts. Privileged actions require a separate named admin account or a just-in-time elevation through [PAM/vault product] lasting [organization-defined period]. Domain-wide privileged groups are limited to [count] standing members plus break-glass.\n\n"
            "Review: Privileged group membership is exported monthly and signed by the ISSO.\n\n"
            "Customer Responsibility: Not applicable if the system provider owns the directory; customer organizations still must not share privileged passwords.",
        ),
        _stmt(
            "Write a control implementation statement for AC-7 Unsuccessful Logon Attempts.",
            "[System Name] locks a user authenticator after [organization-defined number] consecutive failed attempts within [organization-defined period], enforced at [IdP or OS].\n\n"
            "Unlock: Automatic unlock after [period], or administrator unlock after identity verification. Privileged accounts follow the same threshold unless a stricter IdP policy is documented.\n\n"
            "Monitoring: Lockout events forward to [SIEM] and are reviewed with other authentication anomalies.\n\n"
            "Customer Responsibility: Customers must not disable tenant lockout policies. If a number is not provided in the package, keep the placeholder rather than inventing a count.",
        ),
        _stmt(
            "Write an SSP statement for AC-8 System Use Notification on a public-facing login page and SSH jump hosts.",
            "[System Name] displays an approved use notification before authentication on the web login page and on SSH/RDP jump hosts.\n\n"
            "Content: The banner uses the organization's approved legal text (classification reminder, consent to monitoring, no expectation of privacy). Operators do not invent banner wording.\n\n"
            "Enforcement: Web users must acknowledge the banner to continue. SSH uses the approved Banner/legal file. Assessors can screenshot both without a privileged account.\n\n"
            "Customer Responsibility: Not applicable for provider-owned login surfaces; customer-branded portals must still show the approved notice if they are in the boundary.",
        ),
        _stmt(
            "Write a control implementation statement for AC-11 Device Lock for government laptops that access the system.",
            "[System Name] requires endpoints that store or access the system to lock after [organization-defined idle time] via the approved GPO/MDM profile.\n\n"
            "Unlock: CAC/PIN or the approved OS authenticator. Local inactivity lock is in addition to application session timeout (AC-12) where both apply.\n\n"
            "Exceptions: Kiosk or lab devices that cannot lock are listed in the SRTM with compensating physical controls.\n\n"
            "Customer Responsibility: Agencies that allow BYOD must enroll devices in MDM; unmanaged devices are blocked from the resource by conditional access.",
        ),
        _stmt(
            "Write an implementation statement for AC-17 Remote Access for a DoD hybrid system.",
            "[System Name] allows remote access only through [DoD-approved VPN product] with CAC/MFA, terminating in a management or user services segment - not directly onto database hosts.\n\n"
            "Split tunneling: Disabled per the baseline. Split-tunnel exceptions are POA&M/deviation items.\n\n"
            "Contractor access: Same technical path as employees; time-limited accounts (AC-2).\n\n"
            "Monitoring: VPN join/leave and failed MFA events go to [SIEM].\n\n"
            "Customer Responsibility: Users must use government-furnished or MDM-enrolled devices if that is the organization's remote-access policy.",
        ),
        _stmt(
            "Write a control implementation statement for AC-18 Wireless Access.",
            "[System Name] does not operate an organizational WLAN inside the authorization boundary. Endpoints that leave the facility use only the approved enterprise WLAN profile or cellular/VPN as described in AC-17.\n\n"
            "If a site WLAN exists: It uses [EAP-TLS / approved standard], forbids ad-hoc/peer modes via MDM, and is segmented from the system VLAN.\n\n"
            "Guest wireless: Not connected to the authorization boundary.\n\n"
            "Customer Responsibility: Personnel must not create unauthorized hotspots to reach [System Name].",
        ),
        _stmt(
            "Write an SSP statement for AC-19 Access Control for Mobile Devices.",
            "[System Name] mail and application access from mobile devices requires enrollment in [MDM name] with encryption, PIN/biometric, remote wipe, and managed application store policies.\n\n"
            "Unmanaged access: Blocked by conditional access at [IdP]. Jailbroken/rooted devices fail compliance and lose access.\n\n"
            "Customer Responsibility: Users enroll their issued or approved personal devices and report loss to [help desk] within the incident timeline.",
        ),
        _stmt(
            "Write a control implementation statement for AC-20 Use of External Systems.",
            "[System Name] does not permit processing of system data on unmanaged personal computers. External system use is limited to approved partner connections covered by ISA/MOU (CA-3) or government cloud services listed in the inventory.\n\n"
            "Bring-your-own-device browsers: Blocked unless MDM/conditional access says otherwise in this package.\n\n"
            "Customer Responsibility: Customers must not export production data to a commercial file-share tenant that is outside the authorization boundary.",
        ),
        _stmt(
            "Write an implementation statement for AC-22 Publicly Accessible Content.",
            "[System Name] publishes only [describe public pages] outside authentication. Content owners review public pages [frequency] for non-public data (PII, markings, internal host names).\n\n"
            "Release: Public posting follows [review workflow]. The public origin is on a segmented site, not the same origin as authenticated APIs where feasible.\n\n"
            "Customer Responsibility: Customer-provided content is reviewed before it is published if the customer can upload to a public surface.",
        ),
        _stmt(
            "Write a control implementation statement for AU-3 Content of Audit Records.",
            "[System Name] audit records include timestamp (synchronized time), user or service identity, event type, success/failure, and source identifier (IP or host) for the events listed in AU-2.\n\n"
            "Format: Records are generated in [format] and parsed by [SIEM] with a documented field map so an assessor can show those fields on a sample authentication event.\n\n"
            "Gaps: If a COTS component cannot emit a field, that component is listed here and tracked if it creates residual risk.\n\n"
            "Customer Responsibility: Not applicable for provider-owned logs; customers retain any tenant-side audit exports they generate.",
        ),
        _stmt(
            "Write an SSP statement for AU-4 Audit Log Storage Capacity.",
            "[System Name] sizes [SIEM / log store] to retain the AU-11 period with [percent] headroom. Capacity alarms fire at [threshold] and page [role].\n\n"
            "Overflow: Logging fails closed or pages immediately; operators do not silently drop security events to keep an application up without ISSO notification.\n\n"
            "Customer Responsibility: Customer-owned log destinations, if any, must meet the same retention math.",
        ),
        _stmt(
            "Write a control implementation statement for AU-6 Audit Record Review, Analysis, and Reporting.",
            "[System Name] uses [SIEM] correlation rules for authentication anomalies, privileged use, and malware alerts. The SOC reviews rule output [daily]; the ISSO reviews a weekly summary and samples [number] raw events.\n\n"
            "Tuning: Disabled or silenced rules are recorded so an assessor can see they were not quietly turned off.\n\n"
            "Reporting: Confirmed incidents follow IR-6. Recurring technical gaps become POA&M items.\n\n"
            "Customer Responsibility: Customer SOC, if used, must share reportable events with the provider ISSO within [period].",
        ),
        _stmt(
            "Write an implementation statement for AU-9 Protection of Audit Information.",
            "[System Name] stores audit records in [SIEM/index] with write-once or tightly controlled admin roles. Application administrators do not have delete rights on the SIEM index. Access to audit data is itself audited (AU-2).\n\n"
            "Integrity: Hashing or vendor index protection [as implemented] prevents silent edits. Local logs on hosts are forwarded quickly so host-level tampering has a short window.\n\n"
            "Customer Responsibility: Customer users are not granted SIEM delete roles.",
        ),
        _stmt(
            "Write a control implementation statement for AU-11 Audit Record Retention.",
            "[System Name] retains security audit records for [organization-defined time] online and [additional time] in archive, matching the Records Retention Schedule [version].\n\n"
            "Legal holds: Extends retention when Counsel issues a hold; the ISSO does not invent a shorter period to save license cost.\n\n"
            "Customer Responsibility: If the customer exports logs, the customer retains them per their schedule; the provider retains the primary copy as stated.",
        ),
        _stmt(
            "Write an SSP statement for AU-12 Audit Record Generation covering both OS and application.",
            "[System Name] generates audit events at the OS (via [agent or native audit]) and at the application (via [app logging]). Generation is enabled in production baselines (CM-6); debug-only logging is not the production path.\n\n"
            "Failure: If the agent stops, [SIEM] alerts within [period]. Hosts that cannot run the agent are listed and compensated.\n\n"
            "Customer Responsibility: Not applicable unless the customer runs additional components inside the boundary.",
        ),
        _stmt(
            "Write a control implementation statement for IA-4 Identifier Management.",
            "[System Name] issues unique identifiers through [IdP]. Identifiers are not reused for a different person within [period]. Service accounts use a distinct naming convention [pattern] and cannot be ordinary user IDs.\n\n"
            "Shared identifiers: Forbidden for humans. Emergency shared IDs, if any, are break-glass, vaulted, and inventoried.\n\n"
            "Customer Responsibility: Customers must not recycle a departed user's ID for a new person without the cooling period.",
        ),
        _stmt(
            "Write an implementation statement for IA-5 Authenticator Management (passwords, certs, keys).",
            "[System Name] authenticators are issued and stored as follows: human users use CAC/PIV or [IdP MFA]; passwords, when still required, meet IA-5 policy [version]; application secrets live in [vault], not in source code or tickets.\n\n"
            "Rotation: Vault-managed secrets rotate on [period] or on personnel change. Certificates are tracked to expiration (SC-17).\n\n"
            "Initial authenticator: Temporary passwords are one-time and expire in [period].\n\n"
            "Customer Responsibility: Customers protect issued authenticators and report suspected disclosure immediately.",
        ),
        _stmt(
            "Write a control implementation statement for IA-8 Identification and Authentication (Non-Organizational Users).",
            "[System Name] authenticates non-organizational users (contractors, partner agency users) through the same [IdP] with sponsorship by an organizational approver. External IdPs are allowed only if listed and federated under an approved trust.\n\n"
            "Assurance: External users receive only the roles in the partner matrix; they do not receive standing privileged roles.\n\n"
            "Customer Responsibility: Partner agencies vouch for their users and notify [System Name] on departure.",
        ),
        _stmt(
            "Write an SSP statement for CM-2 Baseline Configuration.",
            "[System Name] maintains versioned baseline images/playbooks for [Windows / RHEL / container] in [repository]. Production hosts are built from those baselines, not hand-configured snowflakes.\n\n"
            "Review: Baselines are reviewed [frequency] and after significant STIG updates. Drift is detected by [SCAP/CM tool] and treated as a finding if unexplained.\n\n"
            "Customer Responsibility: Customer-provided images must be rebuilt from the approved pipeline before production use.",
        ),
        _stmt(
            "Write a control implementation statement for CM-3 Configuration Change Control.",
            "[System Name] applies production changes only through [change system] with CCB or designated approvers. Emergency changes are allowed with after-the-fact review within [period].\n\n"
            "Security-relevant changes (identity, boundary, crypto, logging) require ISSO review. Significant changes follow the authorization significant-change process, not only a standard ticket.\n\n"
            "Customer Responsibility: Customer tenant configuration changes that affect security follow the customer's documented change process and notify the provider when shared controls are affected.",
        ),
        _stmt(
            "Write an implementation statement for CM-7 Least Functionality.",
            "[System Name] installs only packages and roles required for the documented function. Hardening playbooks disable unused services, accounts, and protocols (for example leftover SMBv1 or unused HTTP management ports).\n\n"
            "Allowlists: Where the STIG or overlay requires an application allowlist, [tool] is used; otherwise unused software is removed from the gold image.\n\n"
            "Customer Responsibility: Customers must not install extra software on managed endpoints that are in the boundary.",
        ),
        _stmt(
            "Write a control implementation statement for CM-8 System Component Inventory.",
            "[System Name] inventory is maintained in [CMDB/tool] and includes hostname, IP, owner, location/VPC, OS, and whether the asset is production. New hosts must appear in inventory before they are scanned and before they handle production data.\n\n"
            "Reconciliation: Monthly compare of [cloud inventory / AD / scan repo] to the CMDB. Orphans become POA&M or operations tickets.\n\n"
            "Customer Responsibility: Customers report tenant-side components they add that the provider cannot see.",
        ),
        _stmt(
            "Write an SSP statement for CM-10 Software Usage Restrictions.",
            "[System Name] uses only licensed, approved software listed in the baseline. Peer-to-peer and unapproved remote-admin tools are blocked by policy and by technical controls where available.\n\n"
            "Proof: License records and the software inventory (CM-8) are available to assessors. Shadow IT discovered in scans is removed or authorized.\n\n"
            "Customer Responsibility: Customers may not load unlicensed software into the tenant.",
        ),
        _stmt(
            "Write a control implementation statement for RA-2 Security Categorization.",
            "[System Name] is categorized as [FIPS 199 High/Moderate/Low] for confidentiality, integrity, and availability using the high-water mark, documented in [categorization memo] signed [date].\n\n"
            "Overlay: [DoD/FedRAMP/privacy] overlays applied are listed. Recategorization is triggered by a significant change in data types or user population.\n\n"
            "Customer Responsibility: Customers must notify the provider if they begin storing a higher-impact data type than the categorization assumed.",
        ),
        _stmt(
            "Write an implementation statement for RA-3 Risk Assessment.",
            "[System Name] risk assessments are performed at least [annually] and when significant changes occur. The ISSO updates the risk register / eMASS residual-risk view using scan results, SAR findings, and operational incidents.\n\n"
            "Method: Qualitative likelihood/impact per organizational policy [version]. Results feed the AO authorization decision and ConMon reporting.\n\n"
            "Customer Responsibility: Customer-owned residual risks in a shared SaaS model are reported into the customer authorization package.",
        ),
        _stmt(
            "Write a control implementation statement for IR-4 Incident Handling.",
            "[System Name] follows Incident Response Plan [version]. The SOC performs initial handling; the ISSO coordinates system-owner actions; legal/HR are called per the plan's severity table.\n\n"
            "Containment: Playbooks exist for malware, account takeover, and data exposure. Lessons learned are scheduled after major incidents and may create POA&M items.\n\n"
            "Customer Responsibility: Customer tenant admins must not wipe evidence before the provider IR team images or exports logs, except to contain active destructive malware per the plan.",
        ),
        _stmt(
            "Write an SSP statement for IR-8 Incident Response Plan.",
            "[System Name] maintains Incident Response Plan [version], reviewed [annually], stored in [location], and available to SOC, ISSO, ISSM, and the system owner.\n\n"
            "Content: Roles, contact tree, evidence handling, external reporting (IR-6), and restoration handoff to CP procedures.\n\n"
            "Customer Responsibility: Customers keep their after-hours contacts current in [ticket/portal].",
        ),
        _stmt(
            "Write a control implementation statement for SC-8 Transmission Confidentiality and Integrity.",
            "[System Name] requires TLS 1.2 or higher for all user and admin HTTP(S) and TLS or equivalent for data-in-transit between application and data tiers inside the boundary where technically supported.\n\n"
            "Cipher baselines: Weak suites are disabled per the STIG/crypto overlay. Internal exceptions are SRTM items.\n\n"
            "Customer Responsibility: Customers must configure their browsers/clients to support the approved TLS versions; the provider does not re-enable TLS 1.0 for a single customer.",
        ),
        _stmt(
            "Write an implementation statement for SC-12 Cryptographic Key Establishment and Management.",
            "[System Name] keys are generated and stored in [HSM / cloud KMS / approved vault]. Application servers receive keys via IAM roles or short-lived credentials, not long-lived keys in repos.\n\n"
            "Rotation: [period] or on suspected compromise. Destruction of retired keys follows [procedure].\n\n"
            "Customer Responsibility: Customer-managed keys, if the tenant uses BYOK, remain in the customer's KMS with documented rotation.",
        ),
        _stmt(
            "Write a control implementation statement for SC-13 Cryptographic Protection.",
            "[System Name] uses FIPS-validated or organizationally approved cryptographic modules for [TLS, disk encryption, VPN] as listed in the crypto inventory. Algorithms and key lengths follow [policy/CNSS/FedRAMP] attachments - this statement does not invent a module certificate number.\n\n"
            "Customer Responsibility: Customers must not force weaker crypto via custom cipher flags on integrations.",
        ),
        _stmt(
            "Write an SSP statement for SC-17 Public Key Infrastructure Certificates.",
            "[System Name] server certificates are issued by [internal CA or approved public CA], inventoried, and alarmed [days] before expiry. Clients that use mutual TLS have certificates bound to the service identity.\n\n"
            "Revocation: CRL/OCSP as implemented by the CA is enabled on relying parties where supported.\n\n"
            "Customer Responsibility: Customers install only the documented trust anchors for integrations.",
        ),
        _stmt(
            "Write a control implementation statement for SC-28 Protection of Information at Rest.",
            "[System Name] encrypts data at rest using [volume encryption / database TDE / object-storage SSE] with keys in [KMS]. Endpoints that store residual data use approved full-disk encryption (see AC-19/SC-28 endpoint note).\n\n"
            "Backups: Encrypted as described in CP-9.\n\n"
            "Customer Responsibility: Customer-uploaded objects remain in encrypted stores; customers must not copy them to unencrypted personal media.",
        ),
        _stmt(
            "Write an implementation statement for SI-2 Flaw Remediation.",
            "[System Name] applies security updates through [patch tool / WSUS / satellite] on the schedule in the patch policy [version], aligned to POA&M clocks for scan findings (RA-5).\n\n"
            "Emergency patches: Critical/High internet-facing findings can use an emergency CCB path (CM-3).\n\n"
            "Customer Responsibility: Customer-managed images or agents in the tenant must be patched by the customer on the same clocks.",
        ),
        _stmt(
            "Write a control implementation statement for SI-3 Malicious Code Protection.",
            "[System Name] runs [approved EDR/AV] on supported Windows/Linux hosts with signature or cloud-reputation updates at least [frequency]. Quarantine and alert events go to [SIEM].\n\n"
            "Exclusions: Documented in [list] and reviewed [frequency]; unexplained exclusions are findings.\n\n"
            "Customer Responsibility: Customer endpoints used for admin must run the agency-approved EDR.",
        ),
        _stmt(
            "Write an SSP statement for SI-4 System Monitoring.",
            "[System Name] monitoring includes host EDR, [SIEM] use-cases, and boundary logs (SC-7). The SOC is staffed [hours]. Use-cases cover malware callbacks, privilege abuse, and large outbound transfers as implemented - this statement only names detections that actually exist.\n\n"
            "Customer Responsibility: Customers share tenant-side alerts that affect the shared system.",
        ),
        _stmt(
            "Write a control implementation statement for SI-7 Software, Firmware, and Information Integrity.",
            "[System Name] verifies integrity of [gold images / critical binaries] using [signing, hashes, or measured boot as implemented]. Unauthorized change alerts go to [SIEM].\n\n"
            "Firmware: Appliance firmware is applied only from vendor-signed packages (see also SR/MA).\n\n"
            "Customer Responsibility: Customers must not sideload unsigned firmware onto in-boundary appliances they manage.",
        ),
        _stmt(
            "Write an implementation statement for SI-10 Information Input Validation.",
            "[System Name] validates input at the application API using [framework validation] and rejects unexpected types/lengths. The WAF provides additional protocol checks but is not the only validator.\n\n"
            "Error handling: Users receive generic errors (SI-11); detailed faults stay in logs.\n\n"
            "Customer Responsibility: Customer integrations must use the published API schema and not send raw SQL or OS commands in fields.",
        ),
        _stmt(
            "Write a control implementation statement for CP-2 Contingency Plan.",
            "[System Name] Contingency Plan [version] defines RTO/RPO, roles, alternate processing, and communication trees. It is reviewed [annually] and after significant architecture change.\n\n"
            "Alignment: CP-2 names the same backup method as CP-9 and the same restore test cadence as CP-4.\n\n"
            "Customer Responsibility: Customers maintain their own business-continuity actions for processes they own outside the boundary.",
        ),
        _stmt(
            "Write an SSP statement for CP-3 Contingency Training.",
            "[System Name] personnel with CP roles complete contingency training [frequency], recorded in [LMS]. Training covers who declares an outage, how to reach the alternate site, and how to restore from backup.\n\n"
            "Customer Responsibility: Customer points of contact listed in the plan take the provider's tabletop invitation or an equivalent internal exercise.",
        ),
        _stmt(
            "Write a control implementation statement for CP-4 Contingency Plan Testing.",
            "[System Name] tests the Contingency Plan at least [annually] via [tabletop and/or restore exercise]. Results, including failures, are retained and create POA&M items when recoverability is not shown.\n\n"
            "Scope: Tests include a sample restore from CP-9 media, not only a meeting.\n\n"
            "Customer Responsibility: Customer-owned alternate processes are tested by the customer; results are shared when they affect the combined mission.",
        ),
        _stmt(
            "Write an implementation statement for CP-10 System Recovery and Reconstitution.",
            "[System Name] reconstitution uses the gold image / IaC in [repository] plus CP-9 backups. After recovery, operators re-join hosts to monitoring, scanning, and identity before declaring production restored.\n\n"
            "Integrity: Restored systems are scanned (RA-5) before general user access when the outage involved compromise.\n\n"
            "Customer Responsibility: Customers re-establish their tenant integrations using the published runbook.",
        ),
        _stmt(
            "Write a control implementation statement for AT-2 Literacy Training and Awareness.",
            "[System Name] users complete initial security awareness before access and annual refresher training recorded in [LMS]. Content includes phishing, data handling, and how to report incidents.\n\n"
            "Privileged users: Complete additional AT-3 role-based training before receiving admin roles.\n\n"
            "Customer Responsibility: Customer organizations must enroll their users in the required training before sponsoring accounts.",
        ),
        _stmt(
            "Write an SSP statement for AT-3 Role-Based Training for ISSO and administrators.",
            "[System Name] ISSO, system administrators, and SOC analysts complete role-based training covering RMF artifacts, privileged-account use, and IR escalation, recorded in [LMS] at [frequency].\n\n"
            "Evidence: Certificates or LMS exports are available for assessors. New administrators do not receive standing privilege until training is recorded, except supervised break-glass.\n\n"
            "Customer Responsibility: Customer admins in a shared tenant complete the provider's admin training module or an approved equivalent.",
        ),
        _stmt(
            "Write a control implementation statement for CA-2 Control Assessments.",
            "[System Name] is assessed per the Security Assessment Plan [version] by [SCA or 3PAO]. Annual or ConMon assessments sample controls using 800-53A-style examine/interview/test methods.\n\n"
            "Results: Documented in the SAR and mapped to POA&M items. The ISSO does not grade the system's own authorization assessment.\n\n"
            "Customer Responsibility: Customers make tenant evidence available when the assessor requests customer-responsibility controls.",
        ),
        _stmt(
            "Write an implementation statement for CA-5 Plan of Action and Milestones.",
            "[System Name] tracks residual weaknesses in eMASS (or [GRC tool]) as POA&M items with weakness, POC, dates, severity, and status. The ISSO updates items when scans, SAR results, or incidents change the picture.\n\n"
            "Closure: Requires validation evidence, not only an engineer email.\n\n"
            "Customer Responsibility: Customer-owned findings appear in the customer POA&M; they are not hidden inside the provider's Closed list.",
        ),
        _stmt(
            "Write a control implementation statement for CA-7 Continuous Monitoring.",
            "[System Name] ConMon includes monthly credentialed vulnerability scans (RA-5), POA&M currency, inventory reconciliation (CM-8), and periodic control sampling per the ConMon strategy [version]. Reports go to the ISSM/AO on [cadence].\n\n"
            "Triggers: Significant changes and High overdue items escalate outside the routine cadence.\n\n"
            "Customer Responsibility: Customers submit their tenant scan/POA&M extracts when the authorization model requires it.",
        ),
        _stmt(
            "Write an SSP statement for MA-2 Controlled Maintenance.",
            "[System Name] maintenance is performed by authorized personnel using approved tools, recorded in [ticket system], and done in defined windows. Remote maintenance follows MA-4 and AC-17.\n\n"
            "Post-maintenance: Configuration is compared to baseline; unexpected changes are tickets.\n\n"
            "Customer Responsibility: Customer-directed maintenance on their tenant follows the same ticket discipline.",
        ),
        _stmt(
            "Write a control implementation statement for MA-4 Nonlocal Maintenance.",
            "[System Name] vendor nonlocal maintenance uses a time-limited account, MFA/VPN, and session logging/recording as implemented. The session is observed or retrospectively reviewed by [role]. Accounts are disabled at session end.\n\n"
            "Customer Responsibility: Customers must not give vendors standing global-admin without the MA-4 process.",
        ),
        _stmt(
            "Write an implementation statement for MP-2 Media Access.",
            "[System Name] restricts removable media on production servers via baseline (USB storage disabled except documented exceptions). Media that stores system data is encrypted and tracked.\n\n"
            "Customer Responsibility: Customers must not copy production data to personal USB drives.",
        ),
        _stmt(
            "Write a control implementation statement for MP-6 Media Sanitization.",
            "[System Name] sanitizes or destroys media using [approved method] before reuse or disposal. Serial numbers and certificates are retained. Cloud volumes are cryptographically erased / deleted per [CSP process] and recorded.\n\n"
            "Failed disks: Sanitization is evidenced even when under warranty return (chain of custody).\n\n"
            "Customer Responsibility: Customers sanitize any media they attach to the tenant.",
        ),
        _stmt(
            "Write an SSP statement for PE-2 Physical Access Authorizations.",
            "[System Name] production hardware lives in [facility/data center] with an access authorization list managed by [facility security]. The system owner reviews the list [frequency].\n\n"
            "Cloud: Physical PE controls are inherited from [CSP FedRAMP package] as documented in the inheritance table.\n\n"
            "Customer Responsibility: Customer-owned facilities holding components must provide PE evidence.",
        ),
        _stmt(
            "Write a control implementation statement for PE-3 Physical Access Control.",
            "[System Name] enforces badge/two-factor physical entry to the server cage as implemented by [facility]. Visitor escorts are required. Physical access logs are retained [period].\n\n"
            "Cloud inheritance: Documented if the system has no provider-owned cage.\n\n"
            "Customer Responsibility: Not applicable when fully inherited; otherwise the customer facility implements PE-3.",
        ),
        _stmt(
            "Write an implementation statement for PL-2 System Security and Privacy Plans.",
            "[System Name] SSP is maintained in [eMASS/repository], versioned, and reviewed [annually] and after significant change. The plan includes the boundary, roles, inherited controls, and implementation statements a tester can use.\n\n"
            "Customer Responsibility: Customer addenda describe tenant-side implementations the provider cannot see.",
        ),
        _stmt(
            "Write a control implementation statement for PL-4 Rules of Behavior.",
            "[System Name] users accept Rules of Behavior [version] at account issuance and annually, recorded in [LMS or IdP acknowledgment]. Privileged users accept an addendum covering admin tools and data export.\n\n"
            "Customer Responsibility: Customer users accept either the provider RoB or the customer's equivalent before access.",
        ),
        _stmt(
            "Write an SSP statement for PS-2 Position Risk Designation.",
            "[System Name] maps roles to position-risk levels per [organizational policy]. Privileged and ISSO roles are [tier]. Designations are reviewed when duties change.\n\n"
            "Customer Responsibility: Customer organizations designate and screen their own privileged users.",
        ),
        _stmt(
            "Write a control implementation statement for PS-3 Personnel Screening.",
            "[System Name] requires [clearance or background investigation type] before privileged access, verified by [security office]. Access is not granted on a promise that the investigation will finish later, except a documented limited exception.\n\n"
            "Customer Responsibility: Customers attest screening for their users per the access agreement.",
        ),
        _stmt(
            "Write an implementation statement for PS-4 Personnel Termination.",
            "[System Name] disables IdP and local accounts on the termination effective date, recovers tokens/CAC, and reviews the user's data holdings. The offboarding checklist is stored with the ticket.\n\n"
            "Customer Responsibility: Customers notify [help desk] on or before the last day; late notice is an incident if access remained.",
        ),
        _stmt(
            "Write a control implementation statement for SA-4 Acquisition Process.",
            "[System Name] acquisitions include security requirements (identity, logging, crypto, support windows) in the statement of work. Vendors must disclose known inherited FedRAMP/DoD authorizations and residual POA&Ms that affect this system.\n\n"
            "Customer Responsibility: Customers that bring their own COTS into the tenant must provide the same security requirements to their vendors.",
        ),
        _stmt(
            "Write an SSP statement for SA-9 External System Services.",
            "[System Name] uses [CSP / shared service names] under written agreements that assign control inheritance. The inheritance table in the SSP lists provider versus customer versus hybrid.\n\n"
            "Monitoring: Provider ConMon/status pages are reviewed [frequency] for inherited control degradation.\n\n"
            "Customer Responsibility: Customers must not add an undocumented subprocessors that process system data.",
        ),
        _stmt(
            "Write a control implementation statement for SA-11 Developer Testing and Evaluation.",
            "[System Name] development includes [SAST/DAST/dependency scan] in the pipeline before production deploy. Failed high-severity pipeline gates block release unless a named exception is approved.\n\n"
            "Evidence: Pipeline reports are retained [period] for assessors.\n\n"
            "Customer Responsibility: Customer-developed plugins, if allowed, must pass the same pipeline or an approved equivalent.",
        ),
        _stmt(
            "Write an implementation statement for PM-9 Risk Management Strategy as it applies to this system (system-level view).",
            "[System Name] follows the organizational risk management strategy [document]. Residual risks are accepted only by the AO. The ISSO escalates High overdue items and significant changes rather than locally 'accepting' them.\n\n"
            "Customer Responsibility: Customer AOs accept customer residual risk; they cannot silently accept provider Highs.",
        ),
        _stmt(
            "Write a control implementation statement for SR-3 Supply Chain Controls and Processes.",
            "[System Name] acquires critical components from [approved suppliers list] and tracks provenance for [OS images, libraries, appliances]. Unapproved marketplace images are not used in production.\n\n"
            "Incident: Compromised-supplier notices trigger SI-2/IR handling and possible component replacement.\n\n"
            "Customer Responsibility: Customers must not introduce unvetted marketplace images into the shared cluster.",
        ),
        _stmt(
            "Write an SSP statement for SR-6 Supplier Assessments and Reviews.",
            "[System Name] reviews critical suppliers [frequency] for support status, known incidents, and authorization/POA&M posture when the supplier is a CSP or CSO.\n\n"
            "Disqualification: A supplier that can no longer meet crypto or support requirements is scheduled for replacement via CM-3/SA-4.\n\n"
            "Customer Responsibility: Customers share supplier incidents that affect their tenant integrations.",
        ),
        _stmt(
            "Write a control implementation statement for PT-2 Authority to Process Personally Identifiable Information.",
            "[System Name] processes only PII elements listed in [privacy plan / SORN / PT documentation] for [legal authority]. Elements not listed are not collected (see POA&M process if a form field is extra).\n\n"
            "Customer Responsibility: Customers must not upload extra PII categories the system is not authorized to hold.",
        ),
        _stmt(
            "Write an implementation statement for IA-11 Re-authentication for a privileged admin portal.",
            "[System Name] requires re-authentication for privileged actions such as role changes and secret export, enforced by [IdP step-up / session policy] after [period] or at the action, as implemented.\n\n"
            "Customer Responsibility: Customers must not disable step-up MFA on tenant admin consoles.",
        ),
        _stmt(
            "Write a control implementation statement for AC-4 Information Flow Enforcement for a system with a data diode or documented one-way flow.",
            "[System Name] enforces information flow between [Zone A] and [Zone B] using [firewall policy / API gateway / diode]. The permitted flows are exactly those on the data-flow diagram [version]; implicit any/any rules are not used.\n\n"
            "Customer Responsibility: Customers must not add a parallel unmanaged integration that bypasses the documented flow.",
        ),
        _stmt(
            "Write an SSP statement for SC-39 Process Isolation for a multi-tenant application.",
            "[System Name] isolates customer tenants using [account/VPC/namespace] boundaries so one tenant's administrators cannot read another tenant's data. Shared infrastructure components are listed as inherited/common.\n\n"
            "Test: Assessors are given two tenant test accounts and attempt cross-tenant reads.\n\n"
            "Customer Responsibility: Customers must not share tenant admin credentials across organizations.",
        ),
        _stmt(
            "Write a control implementation statement for SI-12 Information Management and Retention for application records (not only logs).",
            "[System Name] retains operational records per [retention schedule] and deletes or archives them when the period ends, using [job name]. Privacy-sensitive records follow the PT/privacy plan, which may be shorter than security log retention.\n\n"
            "Customer Responsibility: Customers configure tenant-side retention only within the allowed range.",
        ),
        _stmt(
            "Write an implementation statement for CM-9 Configuration Management Plan.",
            "[System Name] Configuration Management Plan [version] names baselines, CCB membership, deviation process, and tools ([Git], [CMDB], SCAP). The SSP implementation statements for CM-2/3/6/8 point to this plan instead of inventing a second process.\n\n"
            "Customer Responsibility: Customer CM plans must not contradict shared baseline ownership.",
        ),
        _stmt(
            "Write a control implementation statement for RA-7 Risk Response for how POA&M, OR, and acceptance are chosen.",
            "[System Name] responds to identified risk by remediating, mitigating with compensating controls (Risk Adjustment), transferring (inheritance), or accepting via AO decision. The ISSO proposes; the AO accepts residual risk.\n\n"
            "Customer Responsibility: Customer risk response on tenant findings follows the customer AO, documented in the customer POA&M.",
        ),
        _stmt(
            "Write an SSP statement for IR-5 Incident Monitoring.",
            "[System Name] tracks incidents in [ticket/IR tool] with status, timeline, and evidence links. Metrics (time-to-detect, time-to-contain) are reviewed [frequency] by the ISSM.\n\n"
            "Customer Responsibility: Customers open tickets in the same system or a bridged queue when they first see the event.",
        ),
        _stmt(
            "Write a control implementation statement for AU-5 Response to Audit Logging Process Failures.",
            "[System Name] alerts [SOC/on-call] when the log agent or SIEM ingest fails for [period]. Privileged administrators are notified; if logging cannot be restored within [period], the ISSO considers operational limitation for high-risk components.\n\n"
            "Customer Responsibility: Customer-owned forwarders must alert on failure, not fail silently.",
        ),
        _stmt(
            "Write an implementation statement for IA-3 Device Identification and Authentication for management-plane devices.",
            "[System Name] management-plane access from jump hosts uses device certificates or hardware-backed identity [as implemented] in addition to user CAC. Unknown devices cannot reach SSH/RDP VIPs.\n\n"
            "Customer Responsibility: Customer admin workstations must meet the same device-health standard if they reach the tenant admin API.",
        ),
        _stmt(
            "Write a control implementation statement for SC-5 Denial-of-Service Protection.",
            "[System Name] uses [CSP DDoS / WAF rate limits / perimeter filtering] to absorb or shed abusive traffic. Capacity planning is documented in [ops doc]. Application-layer rate limits exist on login and export APIs.\n\n"
            "Customer Responsibility: Customers must not run uncoordinated load tests that look like attacks without a scheduled exception.",
        ),
        _stmt(
            "Write an SSP statement for SI-5 Security Alerts, Advisories, and Directives.",
            "[System Name] ISSO subscribes to [CISA, vendor, DoD IAVM/channel as applicable] and reviews incoming advisories [frequency]. Applicable items become RA-5 scan checks or SI-2 patch tasks and, if needed, POA&M rows.\n\n"
            "Customer Responsibility: Customers act on advisories that apply only to their tenant software.",
        ),
        _stmt(
            "Write a control implementation statement for CP-7 Alternate Processing Site (including cloud multi-region if that is the model).",
            "[System Name] alternate processing is [second facility / second region / warm standby], with data replication described in CP-9. Failover roles are in the Contingency Plan. Inheritance from the CSP regional capability is listed if used.\n\n"
            "Customer Responsibility: Customers update DNS/allowlists they own during failover per the runbook.",
        ),
        _stmt(
            "Write an implementation statement for CA-3 Information Exchange for an ISA-covered connection.",
            "[System Name] exchanges [data type] with [External System] under ISA/MOU [identifier], reviewed [frequency]. Technical enforcement is the firewall/API allowlist in SC-7/AC-4 matching the ISA ports and crypto.\n\n"
            "Customer Responsibility: Customers must not add a second connection to the same partner outside the ISA.",
        ),
        _stmt(
            "Write a control implementation statement for PM-1 Information Security Program Plan as inherited, from the system ISSO's point of view.",
            "[System Name] inherits the organizational Information Security Program Plan [document] for organization-level policy. System-specific procedures (this SSP, IRP, CMP) implement that program for this boundary. Conflicts are raised to the ISSM, not solved by silently rewriting policy in the SSP.\n\n"
            "Customer Responsibility: Customer programs remain responsible for their own program plan when this system is only a service they consume.",
        ),
        _stmt(
            "Write an SSP implementation statement for AC-1 policy-and-procedure style control without inventing a fake policy title the user did not name.",
            "[System Name] implements Access Control in accordance with the organization's Access Control policy [version or placeholder]. Procedures for account management, remote access, and least privilege are the operational statements in AC-2, AC-6, and AC-17 of this SSP.\n\n"
            "Review: Policy review cadence is organizational (often annual). The system owner ensures this SSP still matches the current policy version.\n\n"
            "Customer Responsibility: Customers follow their agency access-control policy when it is stricter than the provider baseline, and they document that delta.",
        ),
        _stmt(
            "Write a control implementation statement for IA-2(1) or MFA enhancement without claiming a specific hardware token the user did not name.",
            "[System Name] implements multi-factor authentication for network access to privileged accounts using [MFA method: CAC, FIDO, or approved app] as implemented in [IdP]. Password-only privileged network access is disabled.\n\n"
            "Evidence: An assessor can show the IdP policy and a failed password-only admin login.\n\n"
            "Customer Responsibility: Privileged customer users must enroll the approved second factor before admin group membership is granted.",
        ),
        _stmt(
            "Write an implementation statement for SC-7(4) external telecommunications using a documented DMZ pattern.",
            "[System Name] places internet-facing proxies/load balancers in a DMZ/public subnet that cannot initiate connections into data tiers except through defined application ports. Admin interfaces are not published on the DMZ VIP.\n\n"
            "Customer Responsibility: Customers must not publish extra public load balancers in the shared account.",
        ),
        _stmt(
            "Write a FedRAMP-oriented SSP statement for RA-5 with monthly scans and a 3PAO annual test.",
            "[System Name] performs authenticated vulnerability scans at least monthly and after significant change, using [scanner]. Annual independent testing is performed by [3PAO] per the FedRAMP assessment plan.\n\n"
            "POA&M: Unique IDs, vendor dependencies, and operational requirements follow FedRAMP POA&M templates. Customer-responsibility findings are reported to the customer official.\n\n"
            "Customer Responsibility: Customers run or review tenant-side scans where the CSP cannot authenticate into the customer configuration.",
        ),
        _stmt(
            "Write a control implementation statement for AU-2 on a Kubernetes workload where logs go to a cluster log stack.",
            "[System Name] container and control-plane audit logs are shipped to [log stack] via [agent]. Application logs include authentication and authorization decisions from the ingress/API. Node SSH, if enabled, is logged and rare.\n\n"
            "Retention: [period] in hot storage plus archive per AU-11.\n\n"
            "Customer Responsibility: Customer-deployed sidecars must not disable the logging daemonset.",
        ),
        _stmt(
            "Write an SSP statement for CM-6 on network devices using a DISA Network STIG, not a Windows GPO.",
            "[System Name] routers/firewalls are built from the approved Network STIG baseline [STIG version] using [config management / NMS]. Deviations are recorded per device in the SRTM.\n\n"
            "Validation: Configuration compliance checks run [frequency]. ACAS may still find CVEs on the same device; those are separate RA-5 rows.\n\n"
            "Customer Responsibility: Not applicable if the provider owns the devices.",
        ),
        _stmt(
            "Write a control implementation statement for IA-5 for SSH keys on Linux, not passwords.",
            "[System Name] Linux administrators authenticate with SSH keys stored on CAC-backed or vault-issued credentials as implemented; password SSH is disabled in the baseline. Authorized_keys is managed by [config tool], not hand-edited on production.\n\n"
            "Revocation: Key removal is part of PS-4 offboarding the same day.\n\n"
            "Customer Responsibility: Customers must not install personal unofficial keys on provider-managed hosts.",
        ),
        _stmt(
            "Write an implementation statement for CP-9 when backups are cloud snapshots plus a second region.",
            "[System Name] uses [CSP snapshot/backup service] daily for data volumes and replicates snapshots to [second region] with encryption keys in [KMS]. Snapshot success is alarmed.\n\n"
            "Restore tests: Quarterly restore of a sample volume (CP-4).\n\n"
            "Customer Responsibility: Customer-managed buckets outside the backup policy must be enrolled or declared out of recoverability scope.",
        ),
        _stmt(
            "Write a control implementation statement for IR-6 that uses CISA reporting language for a civilian FISMA system (not DoD US-CERT-only wording).",
            "[System Name] reports confirmed incidents per the organization's Incident Response Plan and applicable CISA/FISMA reporting timelines (and any agency SOC directive).\n\n"
            "Internal: SOC to ISSO immediately on confirmation; ISSO to system owner and ISSM within [period].\n\n"
            "External: Submit through the agency-required channel; do not invent a DoD-only reporting path if this is a civilian system.\n\n"
            "Customer Responsibility: Multi-tenant customers report tenant-side incidents that may affect shared infrastructure.",
        ),
        _stmt(
            "Write an SSP statement for RA-5 that only uncredentialed scans are currently possible, and say that honestly.",
            "[System Name] currently performs uncredentialed vulnerability scans with [scanner] on [cadence] because a credentialed service account is not yet approved. Results are treated as incomplete (false negatives likely).\n\n"
            "Gap: Credentialed scanning is tracked as a POA&M against RA-5. This statement does not claim credentialed coverage.\n\n"
            "Customer Responsibility: Customers must not assume a clean uncredentialed scan means hosts are fully patched.",
        ),
        _stmt(
            "Write a control implementation statement for AC-2 for service accounts only (non-person entities).",
            "[System Name] service accounts are requested with a named human owner, a purpose, a secret-storage location, and an expiration or review date. Interactive logon is denied. Secrets are vaulted (IA-5).\n\n"
            "Review: Owners recertify service accounts [frequency]; unused accounts are disabled.\n\n"
            "Customer Responsibility: Customer automations must use tenant service principals, not borrowed human accounts.",
        ),
        _stmt(
            "Write an implementation statement for SI-4 covering outbound traffic anomalies (without claiming a specific commercial NDR unless named).",
            "[System Name] forwards firewall/VPC flow logs to [SIEM] and alerts on new external destinations and large egress from data-tier hosts. The SOC triage procedure for outbound spikes is in the IR playbook.\n\n"
            "Customer Responsibility: Customers should not disable flow logs on subnets they control inside the boundary.",
        ),
        _stmt(
            "Write a control implementation statement for PL-8 Information Security Architecture without drawing a fake diagram in text.",
            "[System Name] security architecture is described in [architecture document / boundary diagram version]. It shows user, app, and data tiers, management paths, and external connections. SSP control statements reference that diagram rather than restating every firewall rule.\n\n"
            "Updates: Architecture updates are significant changes when they add a trust boundary or data type.\n\n"
            "Customer Responsibility: Customer-added components must appear on the combined diagram.",
        ),
        _stmt(
            "Write an SSP statement for MA-5 Maintenance Personnel (escorted vendor on site).",
            "[System Name] on-site vendor maintainers are escorted, signed in, and given access only to the assets on the work order. They do not receive standing badges. Remote vendor access is MA-4 instead.\n\n"
            "Customer Responsibility: Customer sites hosting components apply the same escort rule.",
        ),
        _stmt(
            "Write a control implementation statement for PE-6 Monitoring Physical Access as inherited from a colocation cage.",
            "[System Name] inherits camera/badge monitoring from [facility]. The ISSO obtains evidence [frequency] that monitoring is operational. System-specific server-room alerts, if any, are listed here.\n\n"
            "Customer Responsibility: Not applicable when fully inherited.",
        ),
        _stmt(
            "Write an implementation statement for SA-8 Security and Privacy Engineering Principles as applied to this app (practical, testable).",
            "[System Name] applies least privilege, fail-safe defaults (deny by default at APIs), and complete mediation (authorization on each request) as implemented in the application framework. Privacy minimization is described under PT controls.\n\n"
            "Evidence: Design review notes and sample deny tests, not slogans.\n\n"
            "Customer Responsibility: Customer customizations must not disable server-side authorization.",
        ),
        _stmt(
            "Write a control implementation statement for SI-8 Spam Protection for a system that handles email.",
            "[System Name] inbound mail is filtered by [email security gateway] for spam and malicious content before delivery. Admin consoles are not exposed to raw internet SMTP.\n\n"
            "If the system does not handle mail: state that SI-8 is not applicable and why, rather than inventing a gateway.\n\n"
            "Customer Responsibility: Customers must not create an unfiltered MX that bypasses the gateway.",
        ),
        _stmt(
            "Write an SSP statement for CP-8 Telecommunications Services (alternate communications).",
            "[System Name] uses [primary circuit/provider] and [alternate path] as documented in the Contingency Plan. Outage contacts are in the IR/CP call tree.\n\n"
            "Cloud: Alternate region connectivity is the analog of dual circuits when that is the actual design.\n\n"
            "Customer Responsibility: Customers maintain their own last-mile paths to the service.",
        ),
        _stmt(
            "Write a control implementation statement for AU-10 Non-repudiation if the system uses signed admin actions; otherwise say how far it actually goes.",
            "[System Name] privileged administrative actions in [admin API] are attributable to a unique user ID in immutable logs (AU-9). If cryptographic non-repudiation (signed actions) is not implemented, this statement says so and relies on unique IDs plus protected logs rather than claiming digital signatures.\n\n"
            "Customer Responsibility: Customers must not share admin identities, which would break attribution.",
        ),
        _stmt(
            "Write an implementation statement for IA-12 Identity Proofing for users who are not CAC-issued (FedRAMP civilian example).",
            "[System Name] proofs new non-CAC users per [IAL level / organizational process] before issuing credentials, using [proofing vendor or in-person process]. Failed proofing does not create an account.\n\n"
            "Customer Responsibility: Agencies that sponsor users must complete agency proofing before asking for a tenant account if that is the agreed model.",
        ),
        _stmt(
            "Write a control implementation statement for SC-20 Secure Name/Address Resolution (authoritative DNS) for the system zone.",
            "[System Name] authoritative DNS is provided by [DNS service] with DNSSEC [enabled/not enabled - be honest]. Zone changes follow CM-3. Recursive resolvers used by hosts are the approved internal resolvers, not the open internet.\n\n"
            "Customer Responsibility: Customers must not point production integrations at unofficial DNS zones.",
        ),
        _stmt(
            "Write an SSP statement for CM-11 User-Installed Software on endpoints in the boundary.",
            "[System Name] endpoints block user-installed software via [AppLocker/MDM allowlist] except a documented self-service catalog. Violations generate EDR/SIEM events.\n\n"
            "Customer Responsibility: Customers apply equivalent controls on customer-managed admin workstations.",
        ),
        _stmt(
            "Write a control implementation statement for RA-5(2) update of vulnerabilities scanned / plugin feed currency.",
            "[System Name] ACAS/Tenable plugin feed is configured to update [frequency] before scan jobs run. The ISSO records plugin-set currency in the scan report header. Stale plugin sets are a ConMon defect even if the scan ran.\n\n"
            "Customer Responsibility: Customer scanners used for tenant-only assets must also keep plugin feeds current.",
        ),
        _stmt(
            "Write an implementation statement for IR-4(1) automated incident tracking if a ticketing integration exists.",
            "[System Name] creates or updates IR tickets automatically from [SIEM] alerts that meet [severity] using [integration]. Analysts still confirm incidents; automation does not close High alerts without a human.\n\n"
            "If no automation exists: say incidents are opened manually within [period] rather than inventing a SOAR product.\n\n"
            "Customer Responsibility: Customers must not auto-close shared-system alerts in a downstream tool without SOC agreement.",
        ),
        _stmt(
            "Write a control implementation statement for SC-28(1) cryptographic protection of data at rest at the field or database column level only if that is the design.",
            "[System Name] protects [specific sensitive fields] with application-level encryption using keys in [KMS], in addition to volume encryption. If only volume encryption exists, this enhancement is not implemented - the base SC-28 statement should say that instead of implying column encryption.\n\n"
            "Customer Responsibility: Customers must not store the same fields in plaintext sidecar databases.",
        ),
        _stmt(
            "Write an SSP statement for AT-4 Training Records.",
            "[System Name] retains awareness and role-based training completion records in [LMS] for [period]. The ISSO can export a roster of users with access versus training complete for assessors.\n\n"
            "Customer Responsibility: Customer LMS records are provided on request for customer users.",
        ),
        _stmt(
            "Write a control implementation statement for PS-5 Personnel Transfer (mover, not joiner/leaver).",
            "[System Name] treats role changes as access-relevant: the gaining and losing supervisors recertify entitlements within [period], and groups not required for the new role are removed. Transfer is not 'keep all old access plus new.'\n\n"
            "Customer Responsibility: Customer movers must open a mover ticket; HR-only notifications are not enough if groups are not reviewed.",
        ),
        _stmt(
            "Write an implementation statement for CA-6 Authorization for the AO decision record (system-level).",
            "[System Name] operates only under an authorization decision issued by [AO title] recorded in [eMASS/letter] with an authorization termination date. The ISSO tracks that date and ConMon obligations in the authorization conditions.\n\n"
            "Customer Responsibility: A customer ATO does not automatically authorize a different agency's use without reciprocity review.",
        ),
        _stmt(
            "Write a control implementation statement for SI-11 Error Handling.",
            "[System Name] returns generic user-visible errors and logs detailed diagnostics server-side. Verbose debug is disabled in production (CM-6). Assessors can trigger a controlled error and show the user-visible page versus the log line.\n\n"
            "Customer Responsibility: Customer-branded error pages must not embed stack traces.",
        ),
        _stmt(
            "Write an SSP statement for MP-7 Media Use (prohibiting unauthorized types).",
            "[System Name] prohibits personally owned removable media in the server environment via policy and technical USB controls. Allowed backup/media types are listed in MP-2/CP-9.\n\n"
            "Customer Responsibility: Customers apply the same prohibition in spaces where they handle exported data.",
        ),
        _stmt(
            "Write a control implementation statement for PE-12 Emergency Lighting as inherited, in one honest paragraph.",
            "[System Name] inherits emergency lighting from [facility/CSP site] as a common/inherited PE control. The system ISSO does not operate lighting. Evidence is the facility authorization package or a facility letter, reviewed [frequency].\n\n"
            "Customer Responsibility: Not applicable when inherited; customer-owned computer rooms must implement PE-12 locally.",
        ),
        _stmt(
            "Write an implementation statement for SA-5 System Documentation (admin + user docs).",
            "[System Name] maintains administrator runbooks (patch, restore, account) and user instructions in [repository]. Docs are updated with significant changes (CM-3). Assessors can follow a runbook step without tribal knowledge.\n\n"
            "Customer Responsibility: Customer-facing help text must match actual tenant settings.",
        ),
        _stmt(
            "Write a control implementation statement for SR-5 Acquisition Strategies, Tools, and Methods for the build pipeline.",
            "[System Name] acquires and builds software using [source control + CI] with signed artifacts and a dependency allow/review process. Developers cannot push unsigned production images.\n\n"
            "Customer Responsibility: Customer-contributed code follows the published contribution and signing rules.",
        ),
        _stmt(
            "Write an SSP statement for PT-3 Personally Identifiable Information Processing Purposes.",
            "[System Name] uses PII only for [stated purposes] in the privacy plan. Secondary use requires a documented purpose update and, where required, notice. Purpose limitation is enforced by role design (AC-3) and export reviews.\n\n"
            "Customer Responsibility: Customers must not instruct the system to process PII for a new purpose without a plan update.",
        ),
        _stmt(
            "Write a control implementation statement for AC-14 Permitted Actions without Identification or Authentication (if any).",
            "[System Name] permits unauthenticated actions only for [public health page / JWKS / login page]. All other actions require authentication (IA-2). If no unauthenticated actions exist except the login page, say that - do not invent a guest API.\n\n"
            "Customer Responsibility: Customers must not expose additional unauthenticated tenant routes.",
        ),
        _stmt(
            "Write an implementation statement for CM-4 Impact Analyses of changes.",
            "[System Name] change tickets for security-relevant items include an impact analysis (who is affected, control impact, rollback). The ISSO reviews analyses for boundary, identity, and logging changes.\n\n"
            "Customer Responsibility: Customer significant tenant changes include a short impact note shared with the provider when inherited controls could break.",
        ),
        _stmt(
            "Write a control implementation statement for IR-2 Incident Response Training.",
            "[System Name] IR-role personnel complete IR training [frequency] and participate in [tabletop cadence]. Completion is in [LMS]. Training is separate from general AT-2 awareness.\n\n"
            "Customer Responsibility: Customer IR points of contact attend the joint tabletop or an equivalent exercise.",
        ),
        _stmt(
            "Write an SSP statement for SC-10 Network Disconnect for idle VPN or admin sessions.",
            "[System Name] terminates idle VPN and privileged admin sessions after [organization-defined time] at [VPN concentrator / IdP]. This complements AC-11 device lock and AC-12 application timeout.\n\n"
            "Customer Responsibility: Customers must not run unofficial always-on tunnels that bypass disconnect.",
        ),
        _stmt(
            "Write a control implementation statement for SI-16 Memory Protection for servers that support it.",
            "[System Name] production OS baselines enable DEP/NX, ASLR, and similar memory protections required by the STIG. Exceptions for legacy binaries are SRTM deviations.\n\n"
            "Customer Responsibility: Customer-supplied binaries that disable these protections are not approved for production.",
        ),
        _stmt(
            "Write an implementation statement for CA-8 Penetration Testing at the program cadence.",
            "[System Name] undergoes penetration testing [frequency / on significant change] by [independent team], scoped to the authorization boundary. Findings enter the SAR/POA&M. Internal red-team notes are not a substitute if policy requires independence.\n\n"
            "Customer Responsibility: Customers authorize testing of their tenant data in writing when tests could touch it.",
        ),
        _stmt(
            "Write a control implementation statement for AU-7 Audit Record Reduction and Report Generation.",
            "[System Name] [SIEM] provides filtered reports for authentication failures, privileged activity, and incident timeboxes. The ISSO can generate a report for a given host and window without raw-index access if roles are split that way.\n\n"
            "Customer Responsibility: Customer-generated reports remain customer-controlled; provider reports do not include other tenants' data.",
        ),
        _stmt(
            "Write an SSP statement for IA-6 Authentication Feedback (masking PINs/passwords).",
            "[System Name] login forms and OS logon mask authenticator feedback (dots/asterisks). Error messages do not reveal whether the user ID or the password was wrong beyond organizational UX policy, and they do not echo the secret.\n\n"
            "Customer Responsibility: Customer-branded login skins must keep masking.",
        ),
        _stmt(
            "Write a control implementation statement for CP-6 Alternate Storage Site.",
            "[System Name] stores backup replicas at [geographically separate site/region] as described with CP-9. The alternate storage site meets the same encryption and access-control expectations as primary backup storage.\n\n"
            "Customer Responsibility: Customers who keep their own extra copies must protect them equivalently.",
        ),
        _stmt(
            "Write an implementation statement for PE-16 Delivery and Removal for hardware entering the cage.",
            "[System Name] logs delivery and removal of servers/media at [facility] with asset tags. Unexpected devices are not placed on the production network until inventory (CM-8) and scanning (RA-5) are complete.\n\n"
            "Customer Responsibility: Customer-owned hardware colocated in the same cage follows the same delivery log.",
        ),
        _stmt(
            "Write a control implementation statement for SA-22 Unsupported System Components.",
            "[System Name] tracks vendor support end dates in the inventory. Unsupported OS/runtime is a High POA&M (migration or isolation), not a silent exception. Extended-support contracts are recorded if they are the temporary justification.\n\n"
            "Customer Responsibility: Customer-added runtimes must be supported or isolated.",
        ),
        _stmt(
            "Write an SSP statement for PM-16 Threat Awareness Program from the system vantage point.",
            "[System Name] consumes organizational threat-awareness products (SOC intel, IAVM/CISA notes) via SI-5 and SI-4 use-case updates. The system ISSO does not run a separate intel team.\n\n"
            "Customer Responsibility: Customers consume their agency intel for tenant-specific threats.",
        ),
        _stmt(
            "Write a control implementation statement for AC-5 Separation of Duties for who can develop versus promote to production.",
            "[System Name] separates developers from production deployers: pipeline promotion requires [approver role] that is not the code author for production releases. Privileged production credentials are not issued to the entire development group.\n\n"
            "Customer Responsibility: Customer developers in a shared repo follow the same promotion separation.",
        ),
        _stmt(
            "Write an implementation statement for SC-2 Application Partitioning (user vs management functions).",
            "[System Name] serves user application functions on [user VIP] and administrative functions on [admin VIP or jump path] with separate authentication policies. User roles cannot reach admin routes.\n\n"
            "Customer Responsibility: Customers must not expose the admin VIP to the internet.",
        ),
        _stmt(
            "Write a control implementation statement for AU-1 (policy) that points to real procedures instead of a hollow sentence.",
            "[System Name] implements Audit and Accountability under organizational policy [version]. The testable implementations are AU-2 through AU-12 in this SSP (what is logged, who reviews, how long it is kept, how it is protected).\n\n"
            "Customer Responsibility: Customers with their own SIEM still follow the provider event list for shared components.",
        ),
        _stmt(
            "Write an SSP statement for IA-1 that does the same pointer pattern for identification and authentication policy.",
            "[System Name] implements Identification and Authentication under organizational policy [version]. Operational detail lives in IA-2, IA-4, IA-5, and IA-8 statements (MFA, identifiers, authenticators, external users).\n\n"
            "Customer Responsibility: Customer IdP tenant policies must meet or exceed those statements.",
        ),
        _stmt(
            "Write a control implementation statement for CM-1 configuration-management policy pointer plus where the assessor should actually look.",
            "[System Name] implements Configuration Management under organizational policy [version]. Assessors should test CM-2, CM-3, CM-6, and CM-8 (baseline, change, settings, inventory) rather than a policy PDF alone.\n\n"
            "Customer Responsibility: Customer-owned configuration in the tenant is still in scope for those technical controls.",
        ),
    ]
