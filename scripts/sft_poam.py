"""POA&M drafting and documentation examples for CountGPT SFT."""

from __future__ import annotations

CAVEAT = "This is a draft, not assessor-validated."


def examples() -> list[dict]:
    return [
        {
            "instruction": "A vulnerability scan identified a Moderate-severity finding (weak cipher suite enabled) on a DoD system on August 1st. Draft a POA&M entry for eMASS.",
            "output": (
                "Weakness: Deprecated/weak cipher suite enabled on [System Name], identified via vulnerability scan on August 1st. Severity: Moderate.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No - remediation is a configuration change within the organization's control.\n\n"
                "Required Action: Per common DoD-style remediation windows, Moderate-severity findings are often targeted for closure within 90 days of discovery. The ISSE will disable the deprecated cipher suite and enforce TLS 1.2 or higher during the next scheduled configuration change window.\n\n"
                "Milestones: Configuration change tested in staging within 30 days; deployed to production within 60 days; remediation validated via follow-up scan within 90 days.\n\n"
                "Status: Open - tracked in eMASS, scheduled for closure within the 90-day window.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "A vulnerability scanner flagged a finding, but upon investigation the ISSO determined the vulnerable service was never actually running on the host. How should this be documented in a POA&M?",
            "output": (
                "This should be documented as a False Positive (FP), not an open weakness.\n\n"
                "Weakness: Scanner reported [vulnerability/CVE] on [System Name]; investigation confirmed the associated service/component is not installed or running on the host.\n\n"
                "Determination: False Positive - the reported condition does not reflect the actual state of the system.\n\n"
                "Validation: This determination should be reviewed and validated by the assessor (3PAO or Security Control Assessor) before being accepted. Until validated, it should be marked Pending in the False Positive field rather than closed outright.\n\n"
                "Status: Once validated by the assessor, this item is moved to the Closed status rather than remaining on the open risk list, since a confirmed false positive is not an actual open risk.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "A DoD system has a High-severity POA&M item that has passed its remediation deadline without being fixed. What happens next?",
            "output": (
                "This is considered a past-due or overdue POA&M item, and it carries real consequences rather than just remaining open indefinitely.\n\n"
                "Immediate Impact: A past-due High-severity item commonly blocks the Authorizing Official from granting or maintaining a full ATO, because many AOs will not accept an open High residual risk without a formal, time-bounded decision.\n\n"
                "Required Action: The ISSO must update the POA&M in eMASS with a revised milestone date and a documented justification for the delay (e.g., resource constraints, vendor delay). This is not optional - eMASS-style business rules expect severity values and current status on every open item.\n\n"
                "Escalation: Depending on organizational policy, a past-due High item may require escalation to the ISSM and, in some cases, formal risk acceptance review by the AO, who may issue a time-limited conditional authorization while remediation continues, or suspend authorization if the risk is deemed unacceptable.\n\n"
                "Documentation: All communications regarding the delay and revised plan should be retained as evidence for the next Continuous Monitoring review.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "A POA&M item was mitigated using compensating controls rather than a direct fix. How should the 'Risk Adjustment' be documented?",
            "output": (
                "Weakness: [Original finding], mitigated through compensating controls rather than direct remediation of the underlying issue.\n\n"
                "Risk Adjustment: Yes - the residual risk level has been reduced through documented compensating controls (e.g., network segmentation, enhanced monitoring, restricted access) rather than elimination of the underlying weakness.\n\n"
                "Justification: The specific compensating controls in place must be described in enough detail for an assessor to independently verify they reduce likelihood or impact of exploitation. Vague statements such as 'additional monitoring is in place' are insufficient; the narrative should name the specific tool, control, or process.\n\n"
                "Validation Status: This Risk Adjustment should be marked Pending until validated by the assessor during testing. Once validated, it can be marked Yes; if it is not validated, it must be approved directly by the Authorizing Official prior to authorization.\n\n"
                "Status: Remains Open and tracked, since a risk adjustment reduces risk level but does not close the underlying item until it is fully remediated.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "A contractor needs temporary remote access to a DoD system to complete a specific project. What POA&M or documentation considerations apply?",
            "output": (
                "This scenario is generally handled through the account management and remote access controls rather than a POA&M, unless the access itself creates a documented gap in existing controls.\n\n"
                "Access Authorization: The request should follow the same formal approval process as any account request - a signed access request approved by both the contractor's supervisor and the system's ISSO, specifying the exact scope, systems, and duration of access needed.\n\n"
                "Remote Access Requirements: Per AC-17, the contractor's remote connection must meet the same security requirements as any remote access (e.g., DoD-approved VPN, MFA), regardless of employment status.\n\n"
                "Time Limitation: Access should be explicitly time-limited to the duration of the project, with an automatic expiration date set at provisioning rather than relying on manual follow-up to disable the account later.\n\n"
                "Documentation Note: If the contractor's access requires a temporary exception to standard controls (e.g., access from an unmanaged device), that exception itself should be documented as a POA&M item or formal risk acceptance, since it represents a deviation from the standard control implementation.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "A system's POA&M shows a Low-severity item that has remained open for over a year without action. Is this acceptable?",
            "output": (
                "Not automatically - even though Low-severity items often have a longer remediation window (commonly 180 days in DoD-style practice), remaining open significantly past that deadline without documented justification is a compliance concern, not a passive non-issue.\n\n"
                "Review Needed: The ISSO should review whether this item is genuinely still Low severity, since risk levels can change over time (e.g., if a vulnerability becomes more widely exploited, or if the affected component's exposure has increased).\n\n"
                "Documentation Requirement: If remediation is genuinely still in progress, the milestone dates in eMASS should be updated with current, realistic target dates and a justification for the delay - simply leaving stale dates in the system is a finding in itself during Continuous Monitoring review.\n\n"
                "Risk Acceptance Option: If the organization has decided not to remediate (for example, due to cost or operational constraints), this should be formally documented as an Operational Requirement or risk acceptance, reviewed and approved by the AO, rather than left as a silently stale open item.\n\n"
                "Status: Should not remain in limbo - it needs either updated milestones, formal risk acceptance, or actual remediation, all visible and current in eMASS.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "An ACAS scan identified a High-severity finding on a DoD server. Draft a POA&M entry, naming the actual scanning tool used.",
            "output": (
                "Weakness: [Vulnerability description], identified via ACAS (Nessus) credentialed scan on [System Name] on [date]. Severity: High. Detector Source: ACAS/Nessus, Plugin ID [plugin id].\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Required Action: Per common remediation timelines, High-severity findings are targeted for remediation within 30 days of discovery. The System Administrator will apply the vendor patch during the next scheduled maintenance window, or implement compensating controls if the patch cannot be applied within the required timeframe.\n\n"
                "Validation: Remediation will be validated via a follow-up credentialed ACAS scan confirming the finding no longer appears.\n\n"
                "Status: Open - tracked in eMASS until validated closed.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a High-severity POA&M for missing vendor patches on an internet-facing login host when the patch is already available.",
            "output": (
                "Weakness: Missing security patches on the internet-facing login host for [System Name], identified via credentialed ACAS scan on [date]. Severity: High. Detector Source: ACAS/Nessus, Plugin ID [plugin id].\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No - the vendor patch is already published; delay is an internal change-window issue, not a missing vendor fix.\n\n"
                "Required Action: Apply the vendor security update in the next emergency or scheduled maintenance window. If the full patch cannot be installed within the common 30-day High window, document compensating controls (restrict management to the jump host, disable unused listeners) and a revised milestone rather than leaving the date stale.\n\n"
                "Milestones: Patch tested in staging within 7 days; production applied within 21 days; follow-up credentialed scan within 30 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a High finding that the host still accepts default or well-known administrative credentials.",
            "output": (
                "Weakness: Default or well-known administrative credentials remain usable on [System Name], identified during [assessment or scan type] on [date]. Severity: High.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No - credential rotation and default-account disablement are local configuration actions.\n\n"
                "Required Action: Disable built-in default accounts or force a unique password/key on first use; rotate any credential that may have been exposed; confirm interactive and service logons no longer succeed with the default value. Privileged access should then follow the system's IA-2 / IA-5 implementation (CAC/MFA or approved vaulted secrets).\n\n"
                "Milestones: Default accounts disabled within 3 days; credential rotation completed within 7 days; validation via login test and configuration review within 14 days.\n\n"
                "Status: Open - High residual risk until defaults are proven unusable.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write an eMASS POA&M row for SMBv1 or Telnet still enabled on an internal file server (High).",
            "output": (
                "Weakness: Insecure cleartext or obsolete protocol (SMBv1 and/or Telnet) enabled on [System Name] file server, identified via credentialed scan / configuration review on [date]. Severity: High. Detector Source: [ACAS or STIG check], Plugin ID or STIG ID [plugin id].\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No - protocol disablement is a configuration change. Confirm no legacy client still requires SMBv1 before the change window; if one does, that client is a separate dependency and must be named.\n\n"
                "Required Action: Disable SMBv1/Telnet, require SMB 2.x+/SSH, and verify no listener remains on the obsolete ports. Document any temporary exception with compensating isolation.\n\n"
                "Milestones: Inventory of dependent clients within 7 days; protocol disabled in production within 21 days; rescan and port check within 30 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a High POA&M for Remote Desktop exposed to the public internet on a DoD workstation enclave host.",
            "output": (
                "Weakness: RDP (TCP/3389) reachable from the public internet on [host] in [System Name], identified via external scan on [date]. Severity: High.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No.\n\n"
                "Required Action: Remove public exposure immediately. Administrative remote access should occur only through the approved VPN and jump host (AC-17), with MFA. If RDP must remain on the host, bind it to the management VLAN and confirm the perimeter firewall default-deny still blocks 3389 from untrusted networks.\n\n"
                "Milestones: Perimeter block the same day; host firewall confirmed within 2 days; follow-up external scan within 7 days.\n\n"
                "Status: Open until the external path is gone and a rescan is attached as evidence.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a High finding that the operating system is vendor end-of-life and will not receive patches.",
            "output": (
                "Weakness: [OS name/version] on [System Name] is vendor end-of-life and no longer receives security updates, identified on [date]. Severity: High.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: Yes - continued security updates require a vendor-supported upgrade path or extended-support contract. Name the vendor product and the target supported version; do not claim a patch exists if the vendor has ended support.\n\n"
                "Required Action: Migrate the workload to a supported OS, or isolate the host (no inbound from general users, management via jump host only) while the migration completes. Isolation is a compensating control, not closure.\n\n"
                "Milestones: Isolation/compensating controls within 7 days; migration plan approved within 30 days; cutover by [milestone date]; rescan after cutover.\n\n"
                "Status: Open. Risk Adjustment only if isolation is assessor-validated and the AO accepts residual risk for a defined period.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a High POA&M for an unauthenticated device management interface reachable from the user VLAN.",
            "output": (
                "Weakness: Device management interface on [appliance/host] for [System Name] accepts unauthenticated or password-only access from the user VLAN, identified on [date]. Severity: High.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: Maybe - if the vendor image cannot enforce MFA or management-plane ACLs, document the vendor limitation and the upgrade or replacement path.\n\n"
                "Required Action: Move management to a dedicated management network; require MFA or CAC-backed jump-host access; disable the user-VLAN path. Treat any remaining local emergency account as break-glass, vaulted, and logged.\n\n"
                "Milestones: User-VLAN path blocked within 3 days; management ACL/MFA enforced within 14 days; validation via scan and login test within 30 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a High POA&M for a kernel or privilege-escalation plugin hit. Use placeholders, not a real CVE number.",
            "output": (
                "Weakness: Local privilege-escalation condition reported on [System Name] host [hostname], identified via credentialed ACAS scan on [date]. Severity: High. Detector Source: ACAS/Nessus, Plugin ID [plugin id], mapped vulnerability [CVE].\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No if a vendor patch is listed in the plugin output; Yes if the vendor has not yet published a fix.\n\n"
                "Required Action: Apply the vendor kernel/security update, reboot if required, and confirm the plugin no longer fires on a credentialed rescan. Until patched, restrict local logon to administrators and confirm the host is not a multi-user jump box.\n\n"
                "Milestones: Change ticket opened within 2 days; patch in production within 21 days; credentialed rescan within 30 days.\n\n"
                "Status: Open. Do not invent a CVE or plugin number in eMASS if the scan export did not provide one.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a High POA&M because privileged accounts can still authenticate with password-only (no MFA) on a FedRAMP Moderate SaaS admin portal.",
            "output": (
                "Weakness: Privileged users of [System Name] can authenticate to the admin portal with password-only, identified during control assessment on [date]. Severity: High. Related controls: IA-2, IA-2(1)/IA-2(2) as tailored for the baseline.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: Yes if the SaaS IdP cannot enforce MFA on those roles until a vendor change; No if MFA is a tenant setting the customer can enable.\n\n"
                "Required Action: Enforce MFA for all privileged roles at the identity provider. Disable password-only IdP policy exceptions. Temporary break-glass accounts, if required, are time-limited, vaulted, alerted, and listed in the SSP exception table.\n\n"
                "Milestones: IdP policy change in staging within 7 days; production enforcement within 14 days; access recertification of admin roles within 30 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a High POA&M for an exposed database listener (no TLS, reachable beyond the app tier).",
            "output": (
                "Weakness: Database listener for [System Name] accepts connections from outside the application tier and/or without TLS, identified on [date]. Severity: High. Related controls: SC-8, SC-7, AC-3.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No for network ACL and TLS enablement unless the engine version cannot do TLS.\n\n"
                "Required Action: Restrict the listener to the application subnet/security group; require TLS; disable test accounts. Confirm backups and replicas use the same restriction.\n\n"
                "Milestones: Network restriction the same day if internet-reachable, otherwise within 3 days; TLS required within 14 days; rescan and connection test within 30 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for missing HTTP security headers on a public web application.",
            "output": (
                "Weakness: Public web application for [System Name] does not send required HTTP security headers (for example HSTS, frame-denial, or content-type sniffing protections), identified via web scan / manual review on [date]. Severity: Moderate.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No if headers are a reverse-proxy or application setting; Yes if a COTS portal cannot set them until a vendor release.\n\n"
                "Required Action: Implement the missing headers at the approved edge (WAF, load balancer, or application). Document the exact header set in the SSP SC-8 / SI-10 discussion so an assessor can curl the URL and compare.\n\n"
                "Milestones: Staging change within 30 days; production within 60 days; assessor-style header check within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for a self-signed or expired TLS certificate on an internal admin site.",
            "output": (
                "Weakness: TLS certificate on the [System Name] admin site is self-signed or expired as of [date]. Severity: Moderate. Related control: SC-17.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No - certificate issuance is an internal PKI or approved public CA process.\n\n"
                "Required Action: Replace with a certificate from the approved internal CA (or approved public CA if that is the system's model). Turn on expiration monitoring so the next expiry is a ticket, not a scan surprise.\n\n"
                "Milestones: New certificate issued within 14 days; installed and old cert removed within 30 days; monitoring alert tested within 45 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Moderate POA&M for an unnecessary service listening on a domain-joined Windows server.",
            "output": (
                "Weakness: Unnecessary service [service name] is running and listening on [System Name] host [hostname], identified via credentialed scan / STIG review on [date]. Severity: Moderate. Related control: CM-7.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No unless the service is bundled and cannot be disabled without breaking a vendor-supported appliance role.\n\n"
                "Required Action: Disable the service via GPO or approved configuration baseline if it is not required for the documented system function. If it is required, the SSP CM-6/CM-7 statement must say why and the STIG check should be an approved deviation, not a silent exception.\n\n"
                "Milestones: Function confirmation within 14 days; service disabled or deviation approved within 45 days; rescan within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for an SNMP community string that is default or too simple.",
            "output": (
                "Weakness: SNMP on [System Name] network device [device name] uses a default or weak community string, identified on [date]. Severity: Moderate. Related controls: IA-5, AC-3.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No for string rotation; Yes if the device only supports SNMPv1/v2c and SNMPv3 is a firmware upgrade.\n\n"
                "Required Action: Disable SNMP if unused. If monitoring requires it, move to SNMPv3 with unique credentials stored in the approved vault, and restrict SNMP to the NMS subnet.\n\n"
                "Milestones: SNMP disabled or restricted within 14 days; SNMPv3 cutover within 45 days; validation from a non-NMS host (should fail) within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for a missing host-based firewall on a Linux application server.",
            "output": (
                "Weakness: Host-based firewall is disabled or absent on [System Name] Linux host [hostname], identified on [date]. Severity: Moderate. Related controls: SC-7, CM-6.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No.\n\n"
                "Required Action: Enable the approved host firewall (for example firewalld or nftables per the baseline) with default-deny inbound and only the ports listed in the SSP. Perimeter controls remain necessary; they do not replace the host control if the baseline requires both.\n\n"
                "Milestones: Ruleset drafted within 14 days; enabled in production within 45 days; port-scan validation within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "A Moderate library finding cannot be patched because the COTS vendor has not released a build. Draft the POA&M with vendor dependency filled in.",
            "output": (
                "Weakness: Vulnerable application library on [System Name], identified via ACAS on [date]. Severity: Moderate. Detector Source: ACAS/Nessus, Plugin ID [plugin id], [CVE].\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: Yes - the COTS vendor has not published a patched build as of [date]. Ticket/case [vendor ticket] is open. The ISSO will not mark this closed on a configuration workaround alone unless an assessor accepts a Risk Adjustment.\n\n"
                "Required Action: Track the vendor release; apply it in the next change window after it ships. While waiting, reduce exposure (no internet path to the component, WAF rules if web-facing, least-privilege service account).\n\n"
                "Milestones: Monthly vendor status update; patch applied within 30 days of vendor release; credentialed rescan after install.\n\n"
                "Status: Open - vendor dependent. Milestone dates must move forward when the vendor slips; do not leave the original 90-day date stale.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for a password policy that does not meet the organization's stated complexity and rotation baseline.",
            "output": (
                "Weakness: Password policy on [System Name] identity store does not meet the documented baseline (length/complexity/rotation or lockout), identified on [date]. Severity: Moderate. Related control: IA-5.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No if the IdP or AD can enforce the policy; Yes only if a legacy directory cannot.\n\n"
                "Required Action: Align GPO/IdP policy with the SSP IA-5 statement. Prefer longer passphrases and MFA over frequent rotation theater if that is what the current organizational policy actually says - quote the policy version, do not invent a rotation period.\n\n"
                "Milestones: Policy object updated within 30 days; users notified; compliance report within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Moderate POA&M for missing session timeout on a web app used from shared kiosks.",
            "output": (
                "Weakness: Application sessions on [System Name] do not expire after the organization's defined idle period, identified on [date]. Severity: Moderate. Related controls: AC-11, AC-12.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No if the app or reverse proxy can set idle timeout; Yes if the COTS product has no timeout setting.\n\n"
                "Required Action: Enforce idle session termination at the application or SSO layer. Shared-kiosk use makes this more than cosmetic: an abandoned session is an access-control miss.\n\n"
                "Milestones: Timeout configured in staging within 30 days; production within 60 days; test evidence (idle then replay cookie) within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for verbose error messages that disclose stack traces to end users.",
            "output": (
                "Weakness: [System Name] returns detailed exception or stack-trace content to end-user browsers, identified on [date]. Severity: Moderate. Related controls: SI-11, SC-8.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No for application configuration (debug off, generic errors); Yes if a vendor portal has no way to hide diagnostics.\n\n"
                "Required Action: Disable debug modes in production, return generic errors to users, and keep detailed errors in server logs only. Confirm staging is not accidentally serving production users.\n\n"
                "Milestones: Production debug disabled within 14 days; code/config review within 45 days; retest of a forced error path within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for leftover TLS 1.0/1.1 on a load balancer that still offers them 'for compatibility.'",
            "output": (
                "Weakness: Load balancer for [System Name] still offers TLS 1.0 and/or TLS 1.1, identified via scan on [date]. Severity: Moderate (raise to High if the same VIP is internet-facing and no stronger suite is required).\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No for protocol disablement; inventory any client that still cannot do TLS 1.2+ before the change.\n\n"
                "Required Action: Disable TLS 1.0/1.1; require TLS 1.2 or higher. If a legacy client remains, isolate that client path instead of leaving weak TLS on the general VIP.\n\n"
                "Milestones: Client inventory within 21 days; protocol change within 60 days; rescan within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Moderate POA&M because application logs are not forwarded to the SIEM named in the SSP.",
            "output": (
                "Weakness: [System Name] application hosts are not forwarding security-relevant logs to [SIEM name] as claimed in the SSP AU-2/AU-6 statements, identified on [date]. Severity: Moderate.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No unless the SIEM license or connector is a procurement blocker - if so, say that explicitly.\n\n"
                "Required Action: Restore forwarding, prove events arrive (authentication failures, admin actions), and update the SSP if the real SIEM differs from what was written. A POA&M that 'fixes' forwarding while the SSP still names the wrong tool will fail the next assessment.\n\n"
                "Milestones: Forwarding restored within 14 days; sample events evidenced within 30 days; SSP alignment within 60 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for a shared local administrator password reused across several Windows servers.",
            "output": (
                "Weakness: Shared local administrator password reused across multiple [System Name] Windows hosts, identified on [date]. Severity: Moderate (High if those hosts are internet-facing or hold privileged credentials). Related controls: IA-5, AC-2.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No.\n\n"
                "Required Action: Randomize local admin passwords with the approved LAPS-style or vaulted unique-secret process; disable unused local admins; confirm domain privileged access uses named accounts plus MFA.\n\n"
                "Milestones: Unique secrets deployed within 30 days; reuse test (hash/compare) within 45 days; account recertification within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Moderate POA&M for unsigned PowerShell or configuration scripts running as a scheduled task.",
            "output": (
                "Weakness: Unsigned administrative scripts run as scheduled tasks on [System Name], identified on [date]. Severity: Moderate. Related controls: CM-7, SI-7, CM-3.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No for execution policy and signing with the organizational code-signing cert.\n\n"
                "Required Action: Move scripts into the approved repository, sign them, restrict who can change the scheduled task, and enable transcript/logging for the account that runs them.\n\n"
                "Milestones: Inventory of tasks within 14 days; signing and policy within 45 days; sample log evidence within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Low POA&M for missing antivirus definition updates that are only a few days behind the vendor baseline.",
            "output": (
                "Weakness: Host-based malware signatures on [System Name] host [hostname] are older than the organization's stated freshness window, identified on [date]. Severity: Low (escalate if definitions are weeks stale or the host is high-exposure). Related control: SI-3.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No if the update service is reachable; Yes if the vendor feed is blocked pending a network change.\n\n"
                "Required Action: Restore definition updates, confirm the update path, and keep the item open until a subsequent scan or console report shows current signatures.\n\n"
                "Milestones: Update path restored within 7 days; compliance report within 30 days.\n\n"
                "Status: Open. Low severity does not mean 'ignore until the next ATO.'\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Low POA&M for a missing DoD-style logon banner on an internal jump host.",
            "output": (
                "Weakness: Logon banner / use-notification is missing on [System Name] jump host, identified on [date]. Severity: Low. Related control: AC-8.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No.\n\n"
                "Required Action: Deploy the approved banner text via GPO or the equivalent SSH/legal-banner setting. Do not invent legal text; paste the organization's approved notice.\n\n"
                "Milestones: Banner applied within 30 days; screenshot/SSH evidence within 60 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Low POA&M for NTP/clock skew that is large enough to worry audit correlation but not service availability.",
            "output": (
                "Weakness: [System Name] host [hostname] clock differs from the approved time source by more than the organization's tolerance, identified on [date]. Severity: Low. Related controls: AU-8, SC-45 if used in the overlay.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No.\n\n"
                "Required Action: Point the host at the approved NTP/PTP sources, confirm drift alarms, and note that skewed time weakens incident timelines even when the finding looks cosmetic.\n\n"
                "Milestones: NTP configuration within 14 days; week of stable sync evidence within 45 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Low POA&M for application version disclosure in an HTTP Server header on an internal site.",
            "output": (
                "Weakness: [System Name] discloses product/version in HTTP headers on an internal site, identified on [date]. Severity: Low. Related control: CM-6 / SI-10 as implemented.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No if the header can be suppressed at the proxy.\n\n"
                "Required Action: Remove or genericize the Server/version header. This is not a substitute for patching; it is only information reduction.\n\n"
                "Milestones: Header change within 30 days; header check evidence within 60 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Low POA&M for a STIG CAT III item that is cosmetic but still open on the CKL.",
            "output": (
                "Weakness: STIG CAT III configuration miss [STIG ID] on [System Name], identified on [date]. Severity: Low. Detector Source: STIG / SCAP, not an ACAS CVE plugin.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No unless the setting breaks a vendor-supported function - then write a deviation, do not silently ignore the CKL.\n\n"
                "Required Action: Apply the STIG setting or record an approved deviation in the SRTM with operational justification. Do not close an ACAS item as if it covered this STIG row.\n\n"
                "Milestones: Fix or deviation within 60 days; updated CKL attached within 90 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Low POA&M for an unused internal port that is open but not required by the SSP data flow.",
            "output": (
                "Weakness: Host [hostname] in [System Name] listens on [port/protocol] with no documented data flow, identified on [date]. Severity: Low. Related control: CM-7.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No.\n\n"
                "Required Action: Disable the listener or add the flow to the SSP/boundary diagram if it is actually required. Assessors compare listening ports to the diagram; leftover ports become findings even when no CVE is present.\n\n"
                "Milestones: Confirm purpose within 14 days; close port or update SSP within 45 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How should a false positive be written when the plugin matched the wrong product (similar banner, different software)?",
            "output": (
                "Weakness: Scanner reported [plugin id] / [CVE] on [System Name] host [hostname] on [date].\n\n"
                "Determination: False Positive - fingerprint matched a similar product banner; the installed product/version is [actual product], which is not affected. Attach the evidence an assessor can replay (package list, vendor version command, or software inventory export). Do not use 'we think it is a false positive' with no artifact.\n\n"
                "Validation: Mark False Positive as Pending until the SCA/3PAO agrees. Keep the row visible; do not delete the scan evidence.\n\n"
                "Status: Closed only after assessor validation. If the assessor disagrees, the item returns to Open at the scanner severity.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Document a POA&M false positive where the patch was installed after the scan snapshot but before the ISSO review.",
            "output": (
                "This is usually not a false positive - it is a finding that was remediated after discovery.\n\n"
                "Weakness: [plugin id] on [System Name] on scan date [date]. Severity: [scan severity].\n\n"
                "Required Action: Record the original discovery date as the scan date, not the review date. Attach the change ticket and a follow-up credentialed scan that no longer reports the plugin.\n\n"
                "Status: Completed / Pending Validation until the rescan is attached, then Closed. Labeling this FP hides the fact that the weakness existed at scan time and makes metrics dishonest.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How do you document a false positive when the scanned host was out of the authorization boundary?",
            "output": (
                "Weakness: Scan of [hostname] on [date] reported [plugin id], but the host is not in the [System Name] authorization boundary.\n\n"
                "Determination: Not a system finding for this ATO package - out-of-scope asset. This is not the same as 'the vulnerability is fake.' The owning system, if any, still needs its own tracking.\n\n"
                "Required Action: Correct the scan target list / exclusions so the next cycle does not keep importing foreign hosts into this POA&M. Attach the boundary diagram excerpt showing the host is outside.\n\n"
                "Status: Closed for this system with the out-of-scope justification; do not use False Positive unless the condition also does not exist on that host.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a false-positive POA&M note for an uncredentialed scan that guessed a vulnerable version from a banner.",
            "output": (
                "Weakness: Uncredentialed scan on [date] reported [plugin id] on [System Name] based on a service banner.\n\n"
                "Determination: Pending False Positive - a credentialed scan or local version check shows [actual version], which is not affected. Banner-only plugins are hypotheses until authenticated evidence exists.\n\n"
                "Required Action: Keep the item open/pending until a credentialed scan (or assessor-accepted local evidence) confirms. Then mark FP Pending for SCA review.\n\n"
                "Status: Do not close from the uncredentialed result alone, and do not ignore it without the credentialed follow-up.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Document a false positive for a decommissioned host that still appeared in last month's ACAS repository.",
            "output": (
                "Weakness: [plugin id] reported for [hostname] on [date].\n\n"
                "Determination: Not an active-system weakness - host was decommissioned on [decommission date]. Attach the change record and show the host is absent from the current asset inventory (CM-8).\n\n"
                "Required Action: Remove the stale asset from the scan repository so it stops generating POA&M imports. If the decommission is not finished (disk not wiped, still powered), this is still an open finding, not an FP.\n\n"
                "Status: Closed for this package only after inventory and scan-repo cleanup; otherwise Open as an orphaned asset.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How should a Risk Adjustment be written when the only extra protection is a WAF in front of a vulnerable web library?",
            "output": (
                "Weakness: [CVE] / [plugin id] in a web library on [System Name], still present on [date].\n\n"
                "Risk Adjustment: Requested - residual risk proposed as [lower severity] because a WAF virtual patch / signature [rule id placeholder] blocks the known exploit path from untrusted networks.\n\n"
                "Justification: Name the WAF, the rule, whether it is in blocking mode (not detect-only), and what the rule does not cover (authenticated app-layer abuse, bypass, internal users). Attach a test that the unauthenticated exploit path is blocked.\n\n"
                "Validation Status: Pending until the assessor reproduces or reviews the WAF evidence. The library upgrade remains the closure path.\n\n"
                "Status: Open. A WAF rule is compensating control, not remediation.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a Risk Adjustment POA&M for a finding that is only reachable from an isolated management enclave.",
            "output": (
                "Weakness: [finding] on [System Name] management host, identified on [date].\n\n"
                "Risk Adjustment: Requested based on reduced exposure - the service is reachable only from the management enclave / jump host, not from general users or the internet. Attach the firewall/security-group evidence and a scan from an out-of-enclave address showing the port is closed.\n\n"
                "Justification: Exposure reduction lowers likelihood; it does not remove impact if a jump-host admin session is compromised. Say that honestly.\n\n"
                "Status: Open until patched or the AO accepts residual risk. Isolation evidence must stay current after network changes.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Risk Adjustment narrative for enhanced monitoring used while a vendor patch is pending.",
            "output": (
                "Weakness: [finding] on [System Name], vendor patch not yet available as of [date].\n\n"
                "Risk Adjustment: Pending - compensating control is targeted detection, not removal of the weakness. Name the SIEM detections, the log source, who is on-call, and the expected alert-to-triage time. 'We have Splunk' is not enough.\n\n"
                "Vendor Dependency: Yes.\n\n"
                "Status: Open, vendor dependent. Monitoring may support AO acceptance of temporary residual risk; it does not justify Closed.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How do you document a time-limited operational requirement (OR) instead of pretending a High finding is Low?",
            "output": (
                "Weakness: [finding] on [System Name]. Severity remains High - an Operational Requirement does not relabel scanner severity by itself.\n\n"
                "Risk Adjustment / OR: The program requests continued operation until [end date] because [mission function] cannot be interrupted before [event]. Compensating controls: [list].\n\n"
                "Approval: This is an AO decision, not an ISSO preference. Attach the AO/ISSM endorsement and the drop-dead date. When the date arrives, the item is overdue unless remediated or re-approved.\n\n"
                "Status: Open with an explicit acceptance horizon. Do not convert High to Low to make the dashboard green.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a firmware finding on a hardware appliance the ISSO cannot OS-patch.",
            "output": (
                "Weakness: Firmware security defect on [appliance model] used by [System Name], identified on [date]. Severity: [High or Moderate per scan]. Detector Source: [ACAS or vendor advisory], [plugin id] if present.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: Yes - only the vendor firmware image remediates the issue. OS-style package managers will not.\n\n"
                "Required Action: Apply the vendor firmware in a maintenance window after the vendor-supported upgrade path is confirmed. Until then, restrict management-plane access and disable unused services on the appliance.\n\n"
                "Milestones: Vendor image identified within 14 days; lab install within 30 days; production firmware within the severity window or a slipped milestone with justification.\n\n"
                "Status: Open, vendor dependent.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for a cloud shared-responsibility gap: the CSP patched the hypervisor, but the customer OS image is still vulnerable.",
            "output": (
                "Weakness: Guest OS / customer image for [System Name] remains vulnerable to [CVE], identified on [date]. The cloud provider's inherited hypervisor control does not cover this guest.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No for the guest patch (customer responsibility). Do not mark this Inherited/Closed because the CSP FedRAMP package is current.\n\n"
                "Required Action: Patch or rebuild the customer image; update the SSP customer-responsibility matrix if it incorrectly claimed the CSP owned OS patching.\n\n"
                "Milestones: Image patch within the High/Moderate window; new instances launched from the patched image; old instances terminated; rescan.\n\n"
                "Status: Open - customer-owned.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a vendor-dependent POA&M for a license that blocks an upgrade that contains the security fix.",
            "output": (
                "Weakness: [finding] on [System Name]. The fix ships only in version [target version], which requires a license or support contract not yet purchased, identified on [date].\n\n"
                "Vendor Dependency: Yes - procurement/license is on the critical path. Name the contract action and owner, not just 'waiting on vendor.'\n\n"
                "Required Action: Track procurement; apply the upgrade after license activation. Meanwhile document compensating controls and whether the AO will accept delay.\n\n"
                "Milestones: Procurement package [date]; license active [date]; upgrade [date]; rescan [date]. Slip all four together when procurement slips.\n\n"
                "Status: Open, vendor/procurement dependent.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "A Moderate POA&M is 30 days past its 90-day window. Draft the overdue update, not a brand-new finding.",
            "output": (
                "Weakness: [existing weakness text] on [System Name]. Severity: Moderate. Original discovery: [original date]. Original milestone: [old date] (now past due).\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Required Action: This is an overdue update. Record why the original plan failed (change freeze, failed staging test, vendor slip), the compensating controls still in place, and a new realistic date. Do not clone a second POA&M for the same plugin/host.\n\n"
                "Milestones: Revised production date [new date]; validation scan [new date + buffer].\n\n"
                "Status: Ongoing / past due until closed. Continuous Monitoring reviewers look for honest date movement, not silent overdue rows.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Multiple High items are overdue at ATO renewal. What should the ISSO put in the POA&M package narrative?",
            "output": (
                "Package narrative (not a substitute for per-item rows):\n\n"
                "Open High residual risk: [count] items, all past their documented milestones as of [date]. List each by identifier, host, and days overdue. The AO cannot be given a green summary that hides this list.\n\n"
                "Per item: current compensating controls, true blocker (patch, vendor, architecture), and requested decision (remediate before authorization, time-limited conditional ATO, or denial/suspension).\n\n"
                "Process miss: explain why Continuous Monitoring did not escalate earlier. Renewal is the wrong first time the AO sees a year-old High.\n\n"
                "Status: Each High remains Open on its own row. The narrative is orientation, not closure.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a milestone that has slipped twice already. How do you avoid a third fictional date?",
            "output": (
                "Weakness: [finding] on [System Name]. Severity: [level]. Discovery: [date]. Milestone history: [date-1] missed ([reason]); [date-2] missed ([reason]).\n\n"
                "Required Action: The next date must be resource-loaded (named implementer, change window already reserved, or vendor commit in writing). If those do not exist, ask for AO risk acceptance or a formal pause - do not enter another hopeful date.\n\n"
                "Status: Ongoing, past due. Repeated slips without a new control story are themselves a ConMon finding.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a STIG-worded POA&M for a CAT I Windows GPO miss (not an ACAS CVE).",
            "output": (
                "Weakness: DISA Windows STIG CAT I check [STIG ID] failed on [System Name] domain-joined host [hostname] on [date]. The setting [setting name] is not at the required value. This is configuration non-compliance, not a CVE plugin.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Detector Source: STIG / SCAP (or Evaluate-STIG / CKL), not ACAS plugin [plugin id].\n\n"
                "Required Action: Set the GPO/baseline to the STIG value, or file an SRTM deviation with mission justification. Validate with a new CKL/SCAP run, not only an ACAS credentialed scan.\n\n"
                "Milestones: GPO change in staging within 7 days; production within 21 days; updated CKL within 30 days (CAT I follows the High-style clock in most DoD programs).\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for a STIG CAT II failed check on RHEL that the team keeps calling an ACAS Moderate.",
            "output": (
                "Weakness: RHEL STIG CAT II check [STIG ID] failed on [System Name] host [hostname] on [date] (example class: audit rules, umask, or kernel parameter not aligned to the guide).\n\n"
                "Detector Source: STIG/SCAP. Do not reuse an ACAS plugin number for this row.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Required Action: Apply the STIG-aligned configuration via the approved hardening role/playbook. If a required application breaks, document the deviation; do not 'accept' by ignoring the CKL.\n\n"
                "Milestones: Follow the program's Moderate-style window (commonly 90 days) unless local policy maps CAT II differently - quote that policy if you use a different clock.\n\n"
                "Status: Open. A clean ACAS scan does not close this row.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "The same host has both an ACAS High and a STIG CAT I. Draft how the POA&M rows should be split.",
            "output": (
                "Row 1 (scan): Weakness [CVE]/[plugin id] on [hostname], ACAS credentialed scan [date], Severity High. Closure evidence: plugin absent on follow-up credentialed scan.\n\n"
                "Row 2 (config): Weakness STIG [STIG ID] CAT I on the same [hostname], CKL [date]. Closure evidence: updated CKL/SCAP pass or approved deviation.\n\n"
                "Do not merge the rows because they share a host. Remediation owners, evidence, and reopen conditions differ. Cross-reference the other identifier in comments so reviewers see they are related but not duplicates.\n\n"
                "Status: Both Open until their own evidence exists.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M that honestly says only an uncredentialed ACAS scan exists so far.",
            "output": (
                "Weakness: [plugin synopsis] on [System Name] host [hostname], identified via uncredentialed ACAS scan on [date]. Severity: [reported]. Detector Source: ACAS/Nessus uncredentialed, Plugin ID [plugin id].\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Required Action: Treat severity as provisional. Schedule a credentialed scan or local verification before spending a High-urgency change window on a banner guess. If credentialed scanning is blocked (missing service account), that access gap is its own RA-5 / CM-8 issue.\n\n"
                "Status: Open / pending authentication of the finding. Do not mark Closed because 'uncredentialed scans are noisy.'\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for a recurring finding that came back after the team marked it Closed last quarter.",
            "output": (
                "Weakness: [plugin id] / [STIG ID] reappeared on [System Name] host [hostname] on [new date] after closure on [old date]. Severity: [level].\n\n"
                "Required Action: Reopen the existing identifier if the GRC tool allows, rather than creating a disconnected new row. Investigate whether the fix drifted (GPO overwritten, image rebuilt from an old gold disk, change undocumented).\n\n"
                "Milestones: Root-cause note within 7 days; durable fix (baseline/image) within the severity window; rescan plus configuration-as-code or GPO evidence so it does not recur a third time.\n\n"
                "Status: Open. Recurrence is a configuration-management failure as well as the original weakness.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a FedRAMP-style POA&M for a monthly Moderate scan finding in a SaaS tenant the CSP does not inherit away.",
            "output": (
                "Weakness: [finding] in the customer-configured tenant of [System Name], identified on the [monthly] vulnerability scan [date]. Severity: Moderate. This is customer responsibility, not an inherited CSP control.\n\n"
                "Point of Contact: [ISSO Name] / customer official.\n\n"
                "Vendor Dependency: No if a tenant setting remediates it; Yes if the CSP must change shared infrastructure - then the CSP POA&M identifier should be referenced instead of opening a fake local 'fix.'\n\n"
                "Required Action: Remediate in the tenant, record FedRAMP-style unique ID, and attach scan evidence to the customer authorization package.\n\n"
                "Status: Open until the next monthly scan is clean for this ID.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How should an inherited common-control POA&M appear in a child system package?",
            "output": (
                "Weakness: [common control gap], owned by [common control provider], identifier [provider POA&M ID].\n\n"
                "System [System Name] inherits this control and therefore inherits the residual risk. The child ISSO does not invent a second remediation plan that the child cannot execute.\n\n"
                "Required Action: Reference the provider status, the provider milestone, and any customer-side compensating control the child actually owns. If the inherited item is High and overdue, the child's AO still sees that residual risk.\n\n"
                "Status: Inherited / monitoring - not Closed by the child. Update when the provider's ConMon report changes.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a significant-change finding introduced by a new internet-facing API that was not in the last ATO boundary.",
            "output": (
                "Weakness: New internet-facing API on [System Name] was promoted without an updated boundary diagram, scan target, or control assessment, identified on [date]. Severity: High as a process/exposure issue even if no CVE plugin exists yet.\n\n"
                "Required Action: Halt or restrict the new endpoint if policy requires significant-change approval first. Add the endpoint to the inventory (CM-8), scan it (RA-5), update SSP data flows (AC-4/SC-7), and record any new gaps as separate technical rows.\n\n"
                "Milestones: Change-control review immediately; inventory and scans within 7 days; SSP update before the next AO/ConMon checkpoint.\n\n"
                "Status: Open. Shipping the API is not authorization to ignore the package.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Completed-pending-validation POA&M after a patch, before the assessor or rescan agrees.",
            "output": (
                "Weakness: [finding] on [System Name], originally [date], Severity [level].\n\n"
                "Required Action: Vendor patch [patch id] installed on [install date] per change [ticket]. Closure is not complete until validation evidence exists.\n\n"
                "Validation: Credentialed ACAS rescan (or STIG CKL, as appropriate) dated after the change, showing the detector no longer fails. If only a screenshot of 'installed' exists, keep Pending Validation.\n\n"
                "Status: Completed / Pending Validation - not Closed.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for risk accepted by the AO with no plan to patch a Low item on a soon-to-be-retired host.",
            "output": (
                "Weakness: [finding] on [System Name] host [hostname] scheduled for retirement on [retire date]. Severity: Low.\n\n"
                "Risk Acceptance: AO accepts residual risk until retirement, documented on [acceptance date], expires on [retire date]. No patch will be installed unless retirement slips.\n\n"
                "Required Action: If the host is still alive after [retire date], this acceptance is void and the item is overdue. Compensating controls until retirement: [isolation/monitoring].\n\n"
                "Status: Open with accepted risk and a hard expiration. Acceptance is not Closed.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How do you write a POA&M when the scanner severity is High but the ISSO believes exposure is Low?",
            "output": (
                "Keep the detector severity visible. Do not silently overwrite High to Low in the severity field.\n\n"
                "Weakness: [plugin id] High on [System Name] per ACAS [date].\n\n"
                "Risk Adjustment: Requested to Moderate/Low because [not internet-reachable / not installed feature / compensating control]. Attach evidence. Mark adjustment Pending for the assessor/AO.\n\n"
                "If the adjustment is denied, the item remains High with the original clock. ISSO opinion without evidence is not a risk adjustment.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for missing disk encryption on a laptop that stores [System Name] data.",
            "output": (
                "Weakness: Full-disk encryption is not enabled on endpoint [asset id] that stores [System Name] data, identified on [date]. Severity: High if the laptop leaves the facility; otherwise follow local policy. Related control: SC-28.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Vendor Dependency: No if the approved encryption tool is already licensed.\n\n"
                "Required Action: Enable the approved FDE tool, escrow recovery keys as required, and confirm the host reports encrypted in the management console. Until then, restrict the device from leaving the facility if that is organizational policy.\n\n"
                "Status: Open until console evidence shows encrypted.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for an open network share that allows Authenticated Users write access.",
            "output": (
                "Weakness: File share [share name] on [System Name] grants write to a broad group (for example Authenticated Users), identified on [date]. Severity: High if sensitive data is present; Moderate if only non-sensitive utilities. Related controls: AC-3, AC-6.\n\n"
                "Point of Contact: [ISSO Name], Information System Security Officer.\n\n"
                "Required Action: Inventory what is on the share, tighten ACL to named groups, enable access auditing, and check whether data was exposed (that may be an incident, not only a POA&M).\n\n"
                "Milestones: ACL change immediately if sensitive; access review within 7 days; monitoring for 30 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a container image that includes an outdated base layer found by a pipeline scan.",
            "output": (
                "Weakness: Container image [image:tag] used by [System Name] includes vulnerable OS/packages, identified by the pipeline scanner on [date]. Severity: [level]. Detector Source: [pipeline scanner], finding ID [plugin id].\n\n"
                "Vendor Dependency: No if a newer base image exists; Yes if the parent image is vendor-pinned and unpatched.\n\n"
                "Required Action: Rebuild from a patched base, redeploy, and delete old tags from the registry that the runtime can still pull. Scanning the repo without rebuilding running pods does not close the item.\n\n"
                "Status: Open until running workloads and the registry tag are both updated.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for Kubernetes API access that is not restricted to the management network.",
            "output": (
                "Weakness: Kubernetes API for [System Name] is reachable from [too-wide network], identified on [date]. Severity: High. Related controls: AC-3, SC-7, IA-2.\n\n"
                "Required Action: Bind the API to the management path, require SSO/MFA, disable anonymous access, and confirm kubeconfig distribution is limited. Attach both network ACL and authentication-policy evidence.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a service account with domain-admin equivalent rights used for a nightly backup job.",
            "output": (
                "Weakness: Backup service account [account name] on [System Name] has excessive privilege (domain-admin equivalent), identified on [date]. Severity: High. Related controls: AC-6, AC-2.\n\n"
                "Required Action: Replace with least privilege required for backup APIs; vault the secret; alert on interactive logon; remove the account from privileged groups. A password rotation without privilege reduction is incomplete.\n\n"
                "Milestones: Privilege reduction in staging within 14 days; production within 30 days; recertification evidence within 45 days.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How should a POA&M record a 3PAO SAR finding that is not in ACAS at all?",
            "output": (
                "Weakness: [SAR finding title] on [System Name], source Security Assessment Report dated [date], assessor [3PAO/SCA]. Severity: [SAR severity]. Detector Source: SAR / manual test, not ACAS.\n\n"
                "Required Action: Every SAR fail that remains open needs a POA&M row, even when no plugin exists. Map to the failed NIST control ID from the SAR. Closure evidence is whatever the assessor said would pass (interview, examine, test), not a green ACAS dashboard.\n\n"
                "Status: Open until the assessor (or agreed validator) accepts the retest.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for missing audit logging on a privileged jump host that the SSP claimed was covered by AU-2.",
            "output": (
                "Weakness: Privileged jump host for [System Name] is not generating or forwarding the events the SSP AU-2 statement claims, identified on [date]. Severity: High if privileged sessions are invisible; otherwise Moderate.\n\n"
                "Required Action: Enable the required events, forward to the SIEM, and amend the SSP if the real implementation differs. This is both a technical fix and a documentation honesty fix.\n\n"
                "Status: Open until a sample privileged session is visible in [SIEM] and the SSP matches.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for an interconnection that has production traffic but no current ISA/MOU.",
            "output": (
                "Weakness: [System Name] exchanges production data with [External System] without a current Interconnection Security Agreement / MOU, identified on [date]. Severity: Moderate to High depending on data type. Related controls: CA-3, AC-20.\n\n"
                "Required Action: Execute or renew the agreement, update the boundary diagram, and list residual risks if the other system has open Highs that affect this connection.\n\n"
                "Status: Open. Turning up the circuit before the paperwork is a package defect, not a formality.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a privacy finding: more PII is collected than the PT overlay / privacy plan describes.",
            "output": (
                "Weakness: [System Name] collects [PII element] not described in the privacy plan / PT control implementation, identified on [date]. Severity: follows data sensitivity and whether collection is unnecessary.\n\n"
                "Required Action: Stop the extra collection or update the privacy plan, notices, retention, and minimization controls together. A POA&M that only edits the SSP sentence without changing the form still leaves the operational gap.\n\n"
                "Status: Open until the live system and the privacy artifacts match.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for a supply-chain / SR-family gap: a critical library has no documented provenance.",
            "output": (
                "Weakness: Critical component [component name] used by [System Name] lacks documented provenance / integrity verification, identified on [date]. Severity: Moderate typical; High if it is in the trusted build path. Related controls: SR-3, SI-7.\n\n"
                "Required Action: Record the supplier, hash/signature verification in the pipeline, and a response path if the component is later flagged. Do not invent a SBOM tool name unless it is actually used.\n\n"
                "Status: Open until the build pipeline evidence exists.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for delayed media sanitization after a disk was replaced.",
            "output": (
                "Weakness: Failed disk from [System Name] was replaced on [date] but sanitization/destruction per MP-6 is not evidenced.\n\n"
                "Required Action: Sanitize or destroy using the approved method, record serial numbers, and keep the certificate. If the disk already left with the vendor under a documented chain of custody, attach that instead of claiming local wipe.\n\n"
                "Status: Open until the sanitization record exists.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How do you document a POA&M when the only blocker is a change freeze that lasts past the High 30-day clock?",
            "output": (
                "Weakness: [finding] on [System Name], Severity High, discovered [date].\n\n"
                "Required Action: The change freeze is a justification for a slipped milestone, not a closure. Record freeze start/end, the freeze authority, compensating controls during the freeze, and the first reserved window after lift.\n\n"
                "Escalation: High residual risk during a freeze still goes to the ISSM/AO if the clock expires. Freeze policy does not override authorization risk tolerance unless the AO says so in writing.\n\n"
                "Status: Open, milestone revised, freeze documented.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for missing mobile-device management on phones that access [System Name] email.",
            "output": (
                "Weakness: Personnel access [System Name] mail/data from mobile devices that are not enrolled in the approved MDM, identified on [date]. Severity: Moderate to High depending on data. Related controls: AC-19, MP-5.\n\n"
                "Required Action: Enforce MDM enrollment or block ActiveSync/modern-auth from unmanaged devices. Update the SSP if the system claimed MDM was already mandatory.\n\n"
                "Status: Open until the conditional-access or MDM report shows unmanaged clients are blocked.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M for an assessment objective that failed because evidence was stale, not because the control was absent.",
            "output": (
                "Weakness: [Control ID] assessment objective failed for [System Name] because evidence was older than the assessor-accepted window, SAR date [date]. The operational control may still exist.\n\n"
                "Required Action: Produce current evidence (screenshots, exports, tickets dated inside the window) and schedule retest. Optionally tighten the ConMon evidence calendar so this does not recur.\n\n"
                "Status: Open as a documentation/evidence finding. Do not pretend it is a scanner High, and do not mark Closed with the same stale PDF.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a backup restore test that failed during CP-4 testing.",
            "output": (
                "Weakness: Contingency restore test for [System Name] failed on [date] (backup would not restore / RTO missed / checksum mismatch). Severity: High if production recoverability is unproven; Moderate if a workaround restore succeeded with delay. Related controls: CP-4, CP-9.\n\n"
                "Required Action: Fix the backup job or restore procedure, rerun the test, and keep the failed test in the record. A successful later test closes the item; deleting the failed test does not.\n\n"
                "Status: Open until a documented successful restore exists.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How should an ISSO write a POA&M comment when a finding is disputed with the scanner team but not yet overturned?",
            "output": (
                "Weakness: [plugin id] on [System Name] [date], Severity [level]. Dispute status: ISSO requested scanner review on [date]; not yet overturned.\n\n"
                "Required Action: Leave the item Open. Record the technical argument and the evidence submitted to the scan owners. Until they withdraw the plugin result or an assessor accepts FP, the authorization package still carries the finding.\n\n"
                "Status: Open / dispute in progress. Disagreement is not False Positive.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for an IPv6 listener that was never included in the IPv4-only hardening baseline.",
            "output": (
                "Weakness: [System Name] host [hostname] has an IPv6 service enabled that is not covered by the documented IPv4-only baseline, identified on [date]. Severity: Moderate typical. Related controls: CM-6, SC-7.\n\n"
                "Required Action: Either disable IPv6 if unsupported, or extend STIGs/ACLs/scans to IPv6 and update the SSP. An IPv4 clean scan does not close an IPv6 exposure.\n\n"
                "Status: Open.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a Low POA&M for missing redundant NTP peers (single time source).",
            "output": (
                "Weakness: [System Name] uses a single NTP source with no approved peer/backup, identified on [date]. Severity: Low. Related control: AU-8.\n\n"
                "Required Action: Add the secondary approved time source and document both in the SSP. This is resilience of audit timestamps, not a CVE.\n\n"
                "Status: Open until config and a sync screenshot show two sources.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for a FedRAMP High customer responsibility: customer admins still share one break-glass password in a spreadsheet.",
            "output": (
                "Weakness: Shared break-glass password for [System Name] stored in an unapproved spreadsheet, identified on [date]. Severity: High. Related controls: IA-5, AC-2.\n\n"
                "Vendor Dependency: No - customer secret-handling.\n\n"
                "Required Action: Move to the approved vault, unique secrets, dual control if required, rotate the exposed password, and review access logs for the period the spreadsheet existed (possible incident).\n\n"
                "Status: Open until vault evidence and rotation are complete.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "How do you close a POA&M in eMASS after a follow-up credentialed scan is clean?",
            "output": (
                "Closure package for [POA&M ID] on [System Name]:\n\n"
                "1. Restate the weakness and original detector (ACAS plugin [plugin id] or STIG [STIG ID]) and original date.\n"
                "2. Describe the change (patch, config, or removal) and the change ticket.\n"
                "3. Attach the follow-up credentialed scan or CKL dated after the change, showing the detector passed.\n"
                "4. Confirm status Closed (or Completed) only after that evidence is uploaded - not when the engineer says it is done.\n"
                "5. If a Risk Adjustment or FP was used instead of a fix, attach assessor/AO approval; a clean scan is the wrong evidence type for those closures.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Draft a POA&M for missing wireless hardening on an approved government laptop that still has ad-hoc Wi-Fi allowed.",
            "output": (
                "Weakness: Endpoint [asset id] used with [System Name] allows ad-hoc / unapproved wireless modes, identified on [date]. Severity: Moderate. Related controls: AC-18, CM-6.\n\n"
                "Required Action: Enforce the approved wireless profile via MDM/GPO; disable ad-hoc; require EAP-TLS or the organizational WLAN standard. Home-router exceptions are not automatic - document them if policy allows.\n\n"
                "Status: Open until the device compliance report shows the policy applied.\n\n"
                f"{CAVEAT}"
            ),
        },
        {
            "instruction": "Write a POA&M when physical-key inventory for a server cage is missing (PE control), not a scan plugin.",
            "output": (
                "Weakness: Physical key/badge inventory for the [System Name] server cage is incomplete as of [date]. Severity: Moderate typical. Related control: PE-3. Detector Source: facility walkthrough / SAR, not ACAS.\n\n"
                "Required Action: Reconcile keys, recover or re-core as needed, update the access list, and set a recurring inventory. Do not invent a plugin ID for a physical finding.\n\n"
                "Status: Open until the inventory record is current.\n\n"
                f"{CAVEAT}"
            ),
        },
    ]
