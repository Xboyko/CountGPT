"""STIG vs vulnerability-scan distinction examples for CountGPT SFT."""

from __future__ import annotations


def examples() -> list[dict]:
    return [
        {
            "instruction": "Explain the difference between a credentialed and uncredentialed ACAS scan, and why it matters for POA&M accuracy.",
            "output": (
                "A credentialed scan logs into the target system using valid credentials and inspects it from the inside - checking installed software versions, configuration settings, and patch levels directly, similar to how an administrator would review the system locally.\n\n"
                "An uncredentialed scan only sees what's visible from the network itself - open ports and responding services - without logging in, similar to how an outside attacker without valid access would see the system.\n\n"
                "Why it matters for POA&M accuracy: a credentialed scan generally produces more accurate and complete results, since it can see the actual patch level and configuration rather than guessing based on network responses. An ISSO relying only on uncredentialed scan results risks missing real findings (false negatives) or documenting findings that don't actually reflect the system's true configuration. When documenting a POA&M item, it's good practice to note which scan type identified the finding, since this affects how much confidence an assessor should place in it."
            ),
        },
        {
            "instruction": "How do STIG findings differ from ACAS vulnerability scan findings, and how should an ISSO track both without treating them as duplicates?",
            "output": (
                "Vulnerability scans (via ACAS/Nessus) tend to catch 'this specific known flaw exists' - a documented, catalogued vulnerability (often tied to a CVE) that a scanner's plugin library can specifically identify.\n\n"
                "STIG checks tend to catch a different kind of problem: 'this system isn't configured the way DoD requires it to be' - even when no specific known flaw has been identified. For example, a STIG check might flag that password complexity requirements aren't set to the DoD-required minimum, which isn't a 'vulnerability' in the CVE sense, but is a configuration non-compliance issue.\n\n"
                "Tracking both: an ISSO should maintain separate but linked POA&M entries for scan-based findings and STIG-based findings, even when they affect the same system or component, since remediation plans and responsible parties may differ. Both ultimately feed the same POA&M and both affect the system's overall risk posture and ability to receive an ATO, but treating a STIG finding as 'covered' simply because a vulnerability scan came back clean (or vice versa) is a mistake - they are checking different things."
            ),
        },
        {
            "instruction": "What do STIG CAT I, CAT II, and CAT III mean, and how do people map them to High/Moderate/Low POA&M severity?",
            "output": (
                "DISA STIG categories describe configuration severity: CAT I is the most serious misconfiguration (often treated like a High), CAT II is important (often Moderate), CAT III is the least severe (often Low). Exact mapping is organizational - quote your local policy if it differs.\n\n"
                "These are not CVE scores. A CAT I failed check can exist with a clean ACAS CVE scan, and an ACAS High can exist on a host whose STIG CKL is mostly green.\n\n"
                "Do not relabel a CAT I as Low because the host is 'internal only' without a documented Risk Adjustment. Do not invent a plugin ID on a STIG-only row."
            ),
        },
        {
            "instruction": "What is a CKL file, and how is it different from an ACAS .nessus export?",
            "output": (
                "A CKL (checklist) is the STIG Viewer / Evaluate-STIG style record of each STIG rule: not a finding, not reviewed, open (failed), or not applicable, plus comments.\n\n"
                "An ACAS/Nessus export is a list of plugin hits about vulnerabilities/patches/banners. Importing a CKL into the POA&M as if each row were a CVE plugin confuses assessors.\n\n"
                "Closure evidence follows the detector: updated CKL/SCAP for STIG, credentialed rescan for ACAS."
            ),
        },
        {
            "instruction": "What does SCAP do in a STIG program versus a raw Nessus plugin scan?",
            "output": (
                "SCAP is a standardized way to express and automate configuration benchmarks (OVAL/XCCDF and related). DoD programs use SCAP-content to evaluate many STIG settings automatically.\n\n"
                "Nessus/ACAS can run vulnerability plugins and, in some deployments, configuration audits - but a vulnerability plugin hit is still not automatically a STIG CAT result.\n\n"
                "If you only ran CVE plugins, you did not complete a STIG assessment. If you only ran SCAP, you may have missed unpatched software that no STIG rule names."
            ),
        },
        {
            "instruction": "Why can't an uncredentialed scan reliably check GPO-enforced STIG settings?",
            "output": (
                "Most STIG settings live in the registry, policy, or file permissions. Without a login (or an agent), the scanner cannot read those. It can only infer a little from service banners.\n\n"
                "So 'the external scan was clean' does not mean the Windows STIG passed. Credentialed SCAP/Evaluate-STIG or a managed-agent compliance job is the appropriate detector.\n\n"
                "RA-5 statements that claim STIG coverage should name the credentialed config audit, not only perimeter ACAS."
            ),
        },
        {
            "instruction": "What is the difference between 'Open,' 'Not a Finding,' 'Not Applicable,' and 'Not Reviewed' on a STIG check?",
            "output": (
                "Open means the setting failed the check - it is a finding unless you document a valid deviation.\n\n"
                "Not a Finding means the required state is met.\n\n"
                "Not Applicable means the check does not apply (feature not installed); you still write why, or an assessor will reopen it.\n\n"
                "Not Reviewed means nobody looked - it is not a pass. Shipping a CKL full of Not Reviewed is an incomplete assessment, not a clean host."
            ),
        },
        {
            "instruction": "How should an ISSO treat a STIG 'Not a Finding' that was marked that way with no comment?",
            "output": (
                "Automated passes can be comment-light. Manual checks marked Not a Finding with no evidence are weak; assessors may re-fail them.\n\n"
                "If a human overrode an automated Open to Not a Finding, that needs a comment and often SRTM/deviation text. Silent overrides are a integrity problem in the CKL."
            ),
        },
        {
            "instruction": "What is Evaluate-STIG versus STIG Viewer for a beginner ISSO?",
            "output": (
                "STIG Viewer is the classic GUI for opening STIGs and CKLs, recording status and comments. Evaluate-STIG (and similar PowerShell tools) automate many Windows checks and produce CKLs.\n\n"
                "Automation reduces Not Reviewed rows but can still be wrong (false Open or false pass) when a site uses an unsupported configuration. Someone still has to review exceptions.\n\n"
                "Neither tool replaces ACAS for CVE patch detection."
            ),
        },
        {
            "instruction": "Explain SCC (SCAP Compliance Checker) at a teaching level.",
            "output": (
                "SCC is a DoD-oriented SCAP scanner used to evaluate configuration benchmarks on a host and produce results you can turn into CKL/compliance evidence.\n\n"
                "It answers 'does this host match the selected benchmark?' It does not replace a full vulnerability plugin scan, and it does not grant an ATO by itself.\n\n"
                "Keep the benchmark version in the evidence (which STIG/SRG release you ran)."
            ),
        },
        {
            "instruction": "How do OpenSCAP or other non-DISA SCAP tools fit a FedRAMP or civilian RHEL host?",
            "output": (
                "Civilian/FedRAMP systems may use vendor or CIS/USGCB-style SCAP content rather than a DISA STIG. The idea is the same: automated config assessment plus documented deviations.\n\n"
                "Do not write 'we STIGed it' in a civilian SSP if you actually ran a CIS benchmark. Name the real benchmark. Do not invent DISA CAT I language for a CIS fail unless your policy maps them."
            ),
        },
        {
            "instruction": "What is a STIG overlay or SRG versus a product STIG?",
            "output": (
                "A Security Requirements Guide (SRG) is a technology-class requirement set (for example Application, Network). A product STIG is the product-specific checklist derived from that class (Windows, RHEL, a specific appliance).\n\n"
                "If no product STIG exists, programs often assess the SRG manually. That still produces findings. 'No STIG exists' is not 'no configuration requirements exist.'"
            ),
        },
        {
            "instruction": "Should a container STIG finding be closed because the host OS ACAS scan is clean?",
            "output": (
                "No. Container images and runtimes have their own hardening and their own CVEs. A clean hypervisor or node OS scan does not prove the image is patched or that the container STIG/SRG passed.\n\n"
                "Track image scan IDs and container benchmark results separately, and make sure running pods match the scanned tag (CM-2/RA-5)."
            ),
        },
        {
            "instruction": "How do database STIGs differ from OS ACAS findings on the same server?",
            "output": (
                "The OS scan/STIG covers the Windows/Linux host. The database STIG covers listeners, roles, auditing, and engine configuration inside the DBMS.\n\n"
                "A patched OS with a default-sa-style database account is still a finding. Assign the DBA a STIG row and the sysadmin an OS row; do not merge them because they share an IP."
            ),
        },
        {
            "instruction": "How should network-device STIG checks be evidenced if ACAS cannot log in to the appliance?",
            "output": (
                "If ACAS lacks credentials, you get a weak uncredentialed CVE picture and almost no STIG coverage. Use the vendor/NMS config extract, a credentialed audit if supported, or a documented manual CKL.\n\n"
                "The RA-5 statement should admit the gap if appliance credentials are not in the scan job. Do not claim monthly STIG validation you cannot show."
            ),
        },
        {
            "instruction": "What is the difference between a Cloud SRG and a guest-OS STIG in a DoD IL-hosted system?",
            "output": (
                "The Cloud SRG speaks to how the cloud offering and tenant are organized (isolation, admin paths, shared responsibility). Guest-OS STIGs still apply to the VMs you operate.\n\n"
                "Inheriting a CSP package does not STIG your Windows images. Putting STIGed images in an unapproved cloud construct does not satisfy the SRG. Both layers can have POA&Ms at once."
            ),
        },
        {
            "instruction": "Why must the STIG version be recorded on a CM-6 statement and on findings?",
            "output": (
                "STIG rules change. A pass against an outdated benchmark can be a fail against the current required version. Assessors ask which version you claimed.\n\n"
                "Use [STIG version] if you do not have it. Do not invent a release number. When the benchmark updates, schedule a delta review rather than assuming last year's CKL is still valid."
            ),
        },
        {
            "instruction": "How do you document a STIG deviation that is operationally required?",
            "output": (
                "In the CKL, the check is often still Open or a documented exception per local process; in the SRTM/SSP, write the operational reason, the compensating control, and the approver (ISSO/ISSM, and AO if residual risk is High).\n\n"
                "A deviation is not 'Not a Finding' without that story. It is not an ACAS false positive. Track it until the architecture changes or the AO acceptance expires."
            ),
        },
        {
            "instruction": "What is the difference between a local policy STIG fail and a domain GPO that should have set the value?",
            "output": (
                "If the domain GPO is correct but the host still fails, you have enforcement/drift (blocked inheritance, local override, or the host is not in the right OU). Fix targeting, then rescan.\n\n"
                "If the GPO itself is wrong, one GPO change remediates many hosts - write the POA&M at the baseline, and list affected hosts or a representative sample as evidence, not 400 copy-paste rows with no GPO story."
            ),
        },
        {
            "instruction": "Can a clean credentialed ACAS scan close a STIG CAT II that is still Open in the CKL?",
            "output": (
                "No. Different detectors. The CAT II remains Open until the CKL/SCAP pass or an approved deviation exists.\n\n"
                "You may mention the clean CVE scan in comments as context (the host is patched) without using it as closure evidence for the STIG row."
            ),
        },
        {
            "instruction": "Can a green CKL close an ACAS High plugin on the same host?",
            "output": (
                "No. Configuration compliance does not mean a missing patch is gone. Close the ACAS row with a follow-up credentialed scan (or documented FP/adjustment).\n\n"
                "Green STIGs plus red ACAS is a common honest state right after a STIG blitz that forgot patching, or the reverse."
            ),
        },
        {
            "instruction": "What does 'severity override' mean on a scan finding, and how is it different from eMASS Risk Adjustment?",
            "output": (
                "Some scanners let an operator override plugin severity locally. That is an operational opinion unless your process requires assessor/AO concurrence.\n\n"
                "eMASS Risk Adjustment is the authorization-facing record with justification and validation status. Overriding severity only in Tenable.sc and leaving eMASS at High (or the reverse) creates two truths.\n\n"
                "Prefer one official adjustment path and attach evidence."
            ),
        },
        {
            "instruction": "How should recurring CAT II findings after image rebuild be explained?",
            "output": (
                "If a gold image is not STIG-aligned, every rebuild reopens the same CAT IIs. The durable fix is CM-2 baseline repair, not weekly firefighter CKL edits on live hosts.\n\n"
                "Write the POA&M against the image pipeline. Closing 50 host rows without touching the image guarantees recurrence."
            ),
        },
        {
            "instruction": "What is a false 'Not a Finding' risk when a STIG check is skipped because a feature 'is not used' but the software is installed?",
            "output": (
                "If the software is installed, many checks still apply even if you 'do not use' it. Uninstall or disable the feature, then mark N/A with evidence.\n\n"
                "N/A because 'we don't use IIS' while IIS is installed is a common assessor fail. CM-7 (least functionality) is the better control story."
            ),
        },
        {
            "instruction": "How do CCIs help an ISSO map STIG rows to NIST 800-53 without over-claiming a whole control is passed?",
            "output": (
                "A CCI maps a granular check to a control/enhancement. Fifty passed CCIs under CM-6 help evidence CM-6; they do not automatically pass AC-2 or the entire assessment objective set in 800-53A.\n\n"
                "Use CCI mappings for traceability in the SRTM. Do not tell the AO 'all of 800-53 is green because the Windows STIG is 99%.' Other families still need interviews and tests."
            ),
        },
        {
            "instruction": "What is the teaching difference between IAVM compliance, STIG compliance, and ACAS plugin compliance?",
            "output": (
                "IAVM-style directives set DoD timelines for specific issues. ACAS plugins detect many (not all) of those issues on hosts. STIGs set configuration state.\n\n"
                "You can be IAVM-late with a plugin that never ran (bad credentialed coverage), STIG-red with no IAVM, or ACAS-green while IAVM still applies to a product the plugins missed.\n\n"
                "ISSOs should know which list a deadline came from when they brief the AO."
            ),
        },
        {
            "instruction": "Why does a credentialed scan still miss some vulnerabilities?",
            "output": (
                "Plugins can be stale, the account may lack rights to read a product's version, containers/sidecars may be invisible, and some flaws need authenticated application tests, not OS scans.\n\n"
                "Credentialed is better than uncredentialed, not omniscient. That is why SAR manual testing and pipeline SAST/DAST still exist (RA-5, CA-8, SA-11)."
            ),
        },
        {
            "instruction": "Why do uncredentialed scans create false positives, in one teaching paragraph?",
            "output": (
                "Without login, the scanner often guesses product and version from a banner. Banners lie, sit behind proxies, or share a string with a different product. The plugin then fires as if the CVE were confirmed.\n\n"
                "Triage with a credentialed scan or local version evidence before you schedule an emergency change window - but do not discard the hit with no follow-up."
            ),
        },
        {
            "instruction": "What should the Detector Source field say for SCAP versus ACAS versus a 3PAO manual test?",
            "output": (
                "Use honest detector names: ACAS/Nessus credentialed (plugin [plugin id]); STIG/SCAP (STIG ID [STIG ID]); SAR/manual (assessment objective). Do not put an ACAS plugin number on a SAR documentation fail.\n\n"
                "Wrong detector source makes the wrong closure evidence look valid and annoys assessors."
            ),
        },
        {
            "instruction": "How do Tenable.sc repositories relate to POA&M import quality?",
            "output": (
                "Tenable.sc (or similar) aggregates scan jobs. If the repository still contains decommissioned hosts, old uncredentialed jobs, or the wrong credentials, the ISSO will import junk.\n\n"
                "Hygiene: current asset list, credentialed jobs for in-scope OS, stale asset removal. Repository noise is an RA-5 process problem, not proof the mission is doomed."
            ),
        },
        {
            "instruction": "Is a web-application scan the same as an ACAS host scan for SSP RA-5 claims?",
            "output": (
                "No. Host/ACAS scans see OS and many installed products. Dynamic web scans see application routes, headers, and auth flaws. You usually need both for a web system.\n\n"
                "An SSP that claims RA-5 with only monthly host scans has a gap for the application layer unless another tool is named honestly."
            ),
        },
        {
            "instruction": "How should an ISSO describe authenticated versus unauthenticated web scans?",
            "output": (
                "Unauthenticated web scans see the public surface. Authenticated scans log in as a test role and can find IDOR-style and role-bypass issues that a public scan will miss.\n\n"
                "Same lesson as ACAS credentials: say which you actually run. Do not claim authenticated coverage if the job has no test account."
            ),
        },
        {
            "instruction": "What is a benchmark 'profile' in SCAP, and why can two scans of the same host disagree?",
            "output": (
                "Profiles select which rules in a benchmark apply (for example a 'MAC-3' or 'typical server' profile). Two profiles produce two scores.\n\n"
                "If the SSP claims one profile and the lab ran another, findings will not match. Record the profile name with the STIG/benchmark version."
            ),
        },
        {
            "instruction": "Should every ACAS informational/Low plugin become a POA&M row?",
            "output": (
                "Follow local policy. Many programs track High/Moderate always, and Low if they age out or cluster into a real weakness. Importing every informational plugin can bury real Highs.\n\n"
                "What you must not do is drop Highs because the dashboard is noisy, or silently delete Lows that are a year overdue without OR/acceptance."
            ),
        },
        {
            "instruction": "How do you explain 'plugin output' versus 'synopsis' when writing a weakness line?",
            "output": (
                "Synopsis is the short title. Plugin output has the host-specific evidence (version found, file path). Weakness text should be understandable without the raw output, but the evidence attachment should include the output.\n\n"
                "Do not invent versions or paths that the output did not show. If output is empty, say so and get a better credentialed job."
            ),
        },
        {
            "instruction": "What is 'unsupported OS' in ACAS versus a STIG that no longer exists for that version?",
            "output": (
                "ACAS will keep reporting missing patches and an unsupported-product risk. STIG content may stop applying to dead versions, which is not a free pass - it often makes residual risk worse because you cannot show current hardening content.\n\n"
                "The POA&M is usually migrate or isolate (SA-22), not 'N/A no STIG.'"
            ),
        },
        {
            "instruction": "How should an ISSO use a vendor advisories feed together with ACAS?",
            "output": (
                "ACAS plugins lag or miss some products. SI-5 (advisories) is the process to catch those and still open a POA&M with detector 'vendor advisory' and placeholder identifiers.\n\n"
                "Do not wait for a plugin ID before tracking a vendor-confirmed flaw in software you know you run. Also do not invent a fake plugin number to make eMASS happy."
            ),
        },
        {
            "instruction": "Why is 'we SCAP'd the jump host' not evidence for the whole enclave?",
            "output": (
                "STIG/SCAP results are host- and product-specific. A perfect jump host does not STIG the database, the k8s nodes, or the firewall.\n\n"
                "CM-6 evidence should match the inventory: each major product class has a benchmark or a documented manual SRG review."
            ),
        },
        {
            "instruction": "What does 'credentialed scan account' hygiene have to do with RA-5 and IA-5?",
            "output": (
                "The scan account needs enough rights to be accurate, must not be a domain-admin if a lesser role works, must be vaulted, and must not be used interactively by humans.\n\n"
                "A shared scan password in a ticket is an IA-5 incident waiting to happen. A too-weak account produces false negatives that make the POA&M look better than reality."
            ),
        },
        {
            "instruction": "How do you talk about CVSS scores versus CAT ratings versus eMASS High/Moderate/Low?",
            "output": (
                "CVSS is a vulnerability scoring system on many plugins. CAT is STIG configuration severity. eMASS High/Moderate/Low is the authorization POA&M severity, often mapped from those sources by local rule (and sometimes by 30/90/180-day clocks).\n\n"
                "They are related but not identical. Do not tell a beginner that CVSS 7.5 'is' a STIG CAT I. Record which scale a number came from."
            ),
        },
        {
            "instruction": "What is a 'configuration audit' policy in Tenable/ACAS versus a 'vulnerability' policy?",
            "output": (
                "A vulnerability policy runs CVE/plugin detection. A configuration-audit policy evaluates compliance plugins/benchmarks (STIG/CIS-like).\n\n"
                "Running only one and claiming both in the SSP is a common RA-5/CM-6 miss. Name both jobs if both exist; name the gap if one does not."
            ),
        },
        {
            "instruction": "How should offline or air-gapped hosts get STIG and scan evidence?",
            "output": (
                "They still need a story: local Evaluate-STIG/SCC, a controlled credentialed scan from a tap, or manual CKL, plus a way to update plugins/content (sneakernet) so evidence is not years stale.\n\n"
                "Air-gap is not 'scans N/A.' It is a different logistics path. Document it in RA-5/CM-6 rather than copying the connected-enclave paragraph."
            ),
        },
        {
            "instruction": "Why might two credentialed scans on the same day disagree on a plugin?",
            "output": (
                "Different plugin sets, different privileges, host in the middle of a patch reboot, clustered nodes behind one VIP, or one job hitting a different interface/container.\n\n"
                "Triage before opening two POA&Ms or closing the worse result. Attach both reports if you claim FP."
            ),
        },
        {
            "instruction": "What is 'authenticated scanning' of a cloud control plane versus guest OS scanning?",
            "output": (
                "Guest OS scanning uses an account on the VM. Cloud control-plane assessment uses cloud APIs (mis-open buckets, public SGs) with a cloud-auditor role.\n\n"
                "Both matter. A STIGed VM with a public 3389 security group is still a High exposure. Put API-posture findings on their own rows (SC-7/CM-8), not as OS plugins."
            ),
        },
        {
            "instruction": "How do you explain 'patch Tuesday' versus STIG release cadence to an engineer?",
            "output": (
                "Vendor patches (and ACAS detections) move on vulnerability timelines. STIG/benchmark releases move on configuration-guidance timelines. You can be fully patched and STIG-behind, or STIG-aligned on an EOL OS that still has unpatchable risk.\n\n"
                "Engineers need both queues. ISSOs should not use a new STIG drop as an excuse to ignore this week's High CVE."
            ),
        },
        {
            "instruction": "What belongs in a POA&M comment when ACAS says 'version unverified'?",
            "output": (
                "It means the plugin could not confirm the installed version - often a credential or path problem. Do not close as FP and do not treat as confirmed High without follow-up.\n\n"
                "Write: pending credentialed verification; scheduled [date]; do not invent a version. Fix the scan account if that is the root cause (RA-5)."
            ),
        },
        {
            "instruction": "Is a passed Windows STIG enough evidence for IA-2 MFA?",
            "output": (
                "No. Some STIG settings support authenticators on the OS, but MFA for the application/IdP is tested at the IdP and the app, not only by a Windows CKL.\n\n"
                "A green OS STIG with password-only cloud admin is still an IA-2 fail. Keep family-level tests in the SAP, not only STIG percentages."
            ),
        },
        {
            "instruction": "How should an ISSO handle a STIG that requires a setting which breaks a mission application?",
            "output": (
                "Do not silently set Not a Finding. Open or exception the check, write the deviation, add compensating controls, and get the right approval (often ISSM/AO if residual risk is material).\n\n"
                "Meanwhile engineer a real fix (app upgrade, architecture change). Permanent silent non-compliance is how SAR interviews go badly."
            ),
        },
        {
            "instruction": "What is 'benchmark drift' when SCAP content is a year old on the scanner?",
            "output": (
                "Old content means you are scoring against old expectations and missing new checks. ConMon should record content/plugin currency (RA-5 enhancements about update frequency).\n\n"
                "A 100% score on year-old content is not current compliance. Update content, then accept that the score may drop honestly."
            ),
        },
        {
            "instruction": "How do IAVM 'acknowledge / implement / report' style steps differ from writing a STIG CKL?",
            "output": (
                "IAVM-style process is a directed vulnerability-management workflow with official statuses and clocks. CKL writing is configuration assessment evidence.\n\n"
                "You may need both records for the same host. Closing the CKL does not automatically satisfy an IAVM reporting step in organizations that still use that process."
            ),
        },
        {
            "instruction": "Why should scan exclusions be listed in the SSP or scan procedure?",
            "output": (
                "Exclusions hide hosts or plugins from results. Hidden production hosts are a CM-8/RA-5 integrity issue. Hidden plugins can hide real Highs.\n\n"
                "Document why an exclusion exists, who approved it, and when it expires. A permanent undocumented exclusion is how packages lie."
            ),
        },
        {
            "instruction": "What is the difference between a host discovery scan and a vulnerability scan?",
            "output": (
                "Discovery asks what is alive and what ports answer - useful for inventory (CM-8). A vulnerability scan then assesses known flaws on those targets.\n\n"
                "Discovery-only jobs do not satisfy RA-5. But skipping discovery is how new cloud nodes never get vulnerability scanned."
            ),
        },
        {
            "instruction": "How do you explain 'safe checks' versus intrusive scan policies at a teaching level?",
            "output": (
                "Safer policies avoid some plugins that can crash fragile devices. Intrusive/higher-impact policies may find more but can outage old OT or printers.\n\n"
                "ISSOs should know which policy ran. A clean result from a tiny safe policy is not the same as a full credentialed policy. Document the tradeoff; do not silently use safe-only on a High-impact enclave without AO-visible residual risk."
            ),
        },
        {
            "instruction": "When a STIG check is manual, what does good CKL comment text look like?",
            "output": (
                "A good comment says what was examined (policy object, screenshot location, command output summary), when, and by whom. 'Looks good' is not evidence.\n\n"
                "Do not paste classified or unnecessary secrets into comments. Do not claim a GPO setting without the GPO name."
            ),
        },
        {
            "instruction": "How should an ISSO treat ACAS results for a host that is only a network VIP, not a real OS?",
            "output": (
                "Scanning a load-balancer VIP can produce banner findings that belong to backends or to the balancer OS, mixed together. Identify the real asset in CM-8.\n\n"
                "Write POA&Ms against the real host/component. A VIP-only row with a guessed OS is how FP and duplicate rows multiply. Prefer scanning backends with credentials and the balancer via its management STIG."
            ),
        },
        {
            "instruction": "What is 'compliance percentage' theater, and what should the AO see instead?",
            "output": (
                "A 92% STIG score can hide three CAT I opens. AOs should see open CAT I/II counts, overdue items, and credentialed scan Highs - not only a pie chart.\n\n"
                "ISSOs can use percentages internally to find drift, but authorization briefings need the residual-risk list."
            ),
        },
        {
            "instruction": "How do agent-based vulnerability assessments differ from network-based ACAS jobs?",
            "output": (
                "Agents report from the host continuously or on a schedule and can see local state even when the host is off the scan VLAN. Network ACAS jobs need reachability and often credentials.\n\n"
                "Neither automatically runs DISA STIG content unless configured. Name the actual product. Do not claim ACAS if you only have a third-party EDR vulnerability module, or the reverse."
            ),
        },
        {
            "instruction": "Why might a Linux STIG require audit rules that ACAS does not mention?",
            "output": (
                "Audit-rule STIG checks are configuration (AU family / CM-6). ACAS may not care until a CVE exists in auditd. The ISSO still needs the rules for the SSP AU-2/AU-12 story.\n\n"
                "Closing Linux ACAS Highs and ignoring audit-rule CAT IIs leaves a logging hole assessors will test."
            ),
        },
        {
            "instruction": "What should you tell a system admin who wants to disable the scan account because 'ACAS is noisy'?",
            "output": (
                "Disabling the account makes results worse (uncredentialed guesses) and is an RA-5 control regression. Tune false positives with evidence, fix plugin/credential issues, and keep Highs visible.\n\n"
                "If the scan account is actually causing outages, narrow its rights or change the policy - with ISSO involvement - do not ghost the detector."
            ),
        },
        {
            "instruction": "How do you keep STIG and ACAS rows linked without merging them into one eMASS weakness?",
            "output": (
                "Use comments/cross-references: 'Related ACAS [plugin id] on same host' and 'Related STIG [STIG ID].' Separate identifiers, separate evidence, separate closure.\n\n"
                "Related is useful for the implementer. Merged is how the wrong evidence closes the wrong thing."
            ),
        },
        {
            "instruction": "What is a 'credential failure' in scan operations, and is it a finding?",
            "output": (
                "If the scanner could not authenticate, that host's vulnerability results are incomplete. Many programs track credential failures as an RA-5/operations metric and do not treat a quiet host as clean.\n\n"
                "Repeated credential failures on production inventory should become a POA&M or an operations ticket with ISSO visibility - the control is not implemented for those hosts."
            ),
        },
        {
            "instruction": "Explain why TLS cipher STIG/SCAP fails and an ACAS 'weak cipher' plugin might still both be valid on one VIP.",
            "output": (
                "They can describe the same underlying misconfiguration from two detectors, or they can differ (one checks OS crypto policy, one probes the live TLS handshake).\n\n"
                "If both fire, you may cross-link, but close each with its own evidence (CKL pass and a rescan/handshake test). Do not assume one fix automatically satisfies both until both detectors are rerun."
            ),
        },
        {
            "instruction": "What is 'offline CKL' review after a classified processing week, at a process level?",
            "output": (
                "Some environments generate checklists on isolated machines and move evidence via approved media. The ISSO still needs versioned CKLs and a way to open POA&Ms on the official GRC system without copying prohibited data.\n\n"
                "The teaching point is logistics and integrity, not skipping STIG work because the enclave is isolated."
            ),
        },
        {
            "instruction": "How should FedRAMP monthly scan evidence differ from a DoD STIG CKL drop?",
            "output": (
                "FedRAMP emphasizes authenticated vulnerability scanning and POA&M unique IDs on a monthly rhythm for the cloud service. DoD programs often add STIG/CKL cycles for guest OS and appliances.\n\n"
                "A FedRAMP CSP package may not include your tenant Windows STIG. A DoD guest ATO may still inherit FedRAMP for the CSP. Do not submit a CKL when the reviewer asked for the monthly vuln scan export, or the reverse, unless they asked for both."
            ),
        },
        {
            "instruction": "What does 'plugin ID [plugin id]' mean in a POA&M, and what if the export left it blank?",
            "output": (
                "It is the scanner's detector identifier so an assessor can rerun the same check. If the export has no number, leave a placeholder and attach the raw report - do not invent a five-digit ID.\n\n"
                "STIG rows should use STIG IDs, not a made-up plugin number, even if eMASS has a plugin-looking field."
            ),
        },
        {
            "instruction": "Why is 'Nessus is ACAS' almost true in conversation but still worth being careful?",
            "output": (
                "ACAS is the DoD program/solution; Tenable Nessus is the common engine inside it. Civilian teams may run Nessus without ACAS. FedRAMP teams may run a different scanner entirely.\n\n"
                "In a DoD SSP, saying ACAS (Nessus) is fine if that is what you run. In a civilian SSP, say the real product. Do not claim ACAS if you do not have it."
            ),
        },
        {
            "instruction": "How do you teach 'configuration as code' as STIG evidence without skipping the CKL?",
            "output": (
                "If hardening lives in Ansible/GPO/IaC, that is a strong CM-2/CM-6 story. Assessors still want a result: SCAP/CKL, or a documented mapping from the playbook to each required setting.\n\n"
                "A repo link alone is examine-only. Show a recent apply and a recent compliance export. Deviations still need SRTM text."
            ),
        },
        {
            "instruction": "What is the risk of scanning through a jump host or NAT so many hosts share one reported IP?",
            "output": (
                "Findings can attach to the wrong asset, and credentialed results may only reflect the jump host. That breaks CM-8 mapping and POA&M ownership.\n\n"
                "Prefer unique management IPs or agent-based IDs. If you cannot, document the limitation and do not auto-close 'duplicate IPs' as FP without an engineer."
            ),
        },
        {
            "instruction": "When is a STIG CAT III still worth a POA&M if the AO only asks about Highs?",
            "output": (
                "CAT IIIs still show configuration discipline and can become assessor documentation fails if the CKL is ignored. They also age into ConMon sloppiness if dates go stale.\n\n"
                "You can brief Highs first, but do not delete CAT IIIs from the system of record. Batch similar CAT IIIs into a baseline fix when that is honest."
            ),
        },
        {
            "instruction": "How does a pipeline software-composition scan relate to ACAS on the running host?",
            "output": (
                "SCA/dependency scans catch libraries in the build. ACAS catches what is installed on the running OS/image. A fixed build that was never deployed still leaves ACAS red. A patched OS with a fat container of old jars can be ACAS-quiet on the node and dirty in the image scan.\n\n"
                "Track both detectors. Closure needs the running workload updated, not only a green pipeline on a branch that is not in production."
            ),
        },
        {
            "instruction": "What should an ISSO verify before accepting an ACAS 'fixed' status that auto-aged out?",
            "output": (
                "Some consoles mark issues fixed if they disappear from a later scan. Confirm the later scan was credentialed, targeted the same host, and used a current plugin set - not that the host was simply unreachable.\n\n"
                "Unreachable is not remediated. Move those to a credential-failure or inventory ticket."
            ),
        },
        {
            "instruction": "Explain 'manual STIG review' for an application SRG when no automation exists.",
            "output": (
                "Someone answers each SRG requirement with implementer evidence (design, config, test). Results still become findings/POA&Ms.\n\n"
                "It is slower than SCAP and easier to rubber-stamp. The ISSO should sample the evidence, not accept a spreadsheet of 'Compliant' with no artifacts."
            ),
        },
        {
            "instruction": "How do wireless or mobile STIGs show up if the system is 'server only' but admins use laptops?",
            "output": (
                "If those laptops are in the boundary or are required endpoints (AC-19), their STIGs/MDM baselines are in scope. A server-only CKL does not cover the admin laptop that holds the vault token.\n\n"
                "If endpoints are truly out of boundary, say what inherited endpoint program covers them. Do not ignore the admin path."
            ),
        },
        {
            "instruction": "What is a good one-sentence rule for when to open one POA&M versus many for the same plugin across 80 hosts?",
            "output": (
                "If one change (one GPO, one gold image, one load-balancer profile) remediates the class, one well-written item with a host count and a representative evidence sample is often clearer - if local eMASS rules allow rolling up.\n\n"
                "If hosts have different owners, different vendor dependencies, or different exposure (internet vs isolated), split them. Never roll up a High internet-facing host into a Low internal average."
            ),
        },
    ]
