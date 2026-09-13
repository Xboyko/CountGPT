"""SOC triage examples for CountGPT SFT (defensive / educational)."""

from __future__ import annotations

CAVEAT = (
    "This is an educational triage walkthrough, not an incident decision "
    "or assessor-validated finding."
)


def _triage(instruction: str, body: str) -> dict:
    return {"instruction": instruction, "output": body.rstrip() + "\n\n" + CAVEAT}


def examples() -> list[dict]:
    return [
        _triage(
            "A SOC analyst sees a Splunk alert: a service account logged in from an internal IP at 3 AM and accessed a file share it has never accessed before. Walk through the triage.",
            "1. Establish baseline expectations: service accounts typically perform the same automated tasks on a predictable schedule. A 3 AM login by itself may be normal for a scheduled job, but accessing a *new* file share it has never touched before is the more significant anomaly here.\n\n"
            "2. Check what the service account is supposed to do: review the account's documented purpose (tied to its account request/approval record) to determine if this file share access falls outside its intended function.\n\n"
            "3. Review what happened during the session: check whether files were read, copied, modified, or deleted, and how many - a large or bulk file access pattern is a stronger indicator of compromise or misuse than a single file touch.\n\n"
            "4. Check for credential exposure: service account credentials are a common target because they are often over-privileged and under-monitored. Check if this account's credentials appear in any recent phishing reports, and whether the login source IP matches where this service normally runs from.\n\n"
            "5. Escalate appropriately: because this involves unusual behavior on a privileged/service account rather than a standard user account, this should be escalated for deeper investigation rather than closed as routine, even if no clear malicious indicator has been confirmed yet.\n\n"
            "6. Document: record the account, timestamp, file share accessed, and volume of activity for the incident record, regardless of the eventual conclusion.",
        ),
        _triage(
            "A SOC analyst receives an alert for a single failed login attempt on a standard user account. How should this be triaged compared to a burst of failed logins on a privileged account?",
            "A single failed login on a standard user account is low-priority and, in most environments, expected background noise - people mistype passwords regularly, and one failed attempt with no follow-up pattern rarely indicates an attack.\n\n"
            "Appropriate response: log the event per standard audit requirements, but this typically does not require active investigation or escalation on its own. It should only be treated as significant if it's part of a pattern - for example, the same account showing repeated failures across multiple days, or failures occurring alongside other suspicious activity from the same source.\n\n"
            "Contrast with a privileged account burst: a rapid burst of many failed logins followed by a success on a privileged or administrative account is a much higher-priority signal, since it suggests a possible brute-force or credential-stuffing attempt against a high-value target, and warrants immediate investigation rather than passive logging.\n\n"
            "The key triage principle: severity depends on both the pattern (single event vs. burst) and the account's privilege level, not just the raw fact that a login failed.",
        ),
        _triage(
            "A SOC analyst notices a spike in outbound traffic from an internal server to an external IP address never seen before, occurring outside business hours. Walk through the triage.",
            "1. Assess the scale and destination: determine how much data is being transferred and to where. A large volume of outbound traffic to an unfamiliar external IP, especially one in an unexpected geographic location, is a stronger indicator of possible data exfiltration than a small, brief connection.\n\n"
            "2. Check the server's normal role: determine what this server is supposed to do. A web server communicating outbound to serve normal traffic is different from a database server - which should rarely if ever initiate large outbound connections - showing this pattern.\n\n"
            "3. Check the destination IP against threat intelligence: determine if the external IP is a known malicious host, a legitimate cloud service, or entirely unknown.\n\n"
            "4. Correlate with other activity: check if this server has any other recent anomalies - unexpected process execution, new scheduled tasks, or unusual login activity - which would strengthen the case that this is a compromise rather than a benign explanation like a misconfigured backup job.\n\n"
            "5. Contain if warranted: given the combination of unfamiliar destination, off-hours timing, and potential data exposure, this generally warrants isolating the host from the network while investigation continues, rather than waiting for full confirmation, given the potential impact of an active exfiltration event.\n\n"
            "6. Document and escalate: this should be treated as a suspected incident and escalated to IR rather than closed at initial triage, given the potential severity.",
        ),
        _triage(
            "A SOC analyst sees an alert for a user account attempting to access a file share they don't have permission to view, and the attempt was automatically blocked by access controls. Does this need escalation?",
            "This is generally lower priority than a successful unauthorized access, but it shouldn't be dismissed outright - a single blocked attempt could be an honest mistake (e.g., clicking a stale bookmark to a share they used to have access to), but a pattern of attempts is a different story.\n\n"
            "Initial Assessment: check whether this is a one-time event or part of a repeated pattern from the same user across multiple resources - repeated attempts to access resources outside one's role suggests either a misunderstanding of access boundaries or a deliberate attempt to find something accessible, both worth understanding.\n\n"
            "Check the account context: consider whether the user's role recently changed (e.g., a transfer) and their access simply hasn't been reflected yet, which is a common benign explanation worth ruling out before assuming malicious intent.\n\n"
            "Recommended Action: log the event per standard audit practice; escalate for follow-up investigation only if this is a repeated pattern, involves an unusually sensitive resource, or coincides with other suspicious activity from the same account.\n\n"
            "This is also a good moment to reinforce that access controls are working as intended - the block succeeded - which is worth noting distinctly from a case where access controls failed.",
        ),
        _triage(
            "Walk through SOC triage for a user who authenticates successfully from two distant countries within an hour (impossible travel), both with valid MFA.",
            "1. Confirm timestamps and VPN/proxy: some 'impossible travel' alerts are a VPN egress in country A plus a split-tunnel or mobile IP in country B. Check the VPN concentrator and device inventory before calling it a compromise.\n\n"
            "2. Compare device fingerprints: same managed laptop versus a new unmanaged browser. New device plus new geo is more serious than one MDM-enrolled laptop with a flaky geo-IP.\n\n"
            "3. Check the second session's actions: mailbox rules, consent grants, download volume. Successful MFA means the authenticator was used - phishing/MFA-fatigue or token theft are still on the table.\n\n"
            "4. Contain while unsure: if policy allows, disable the session/refresh tokens and require re-enrollment rather than sending email and waiting.\n\n"
            "5. Escalate if either session touched privileged apps or exported data. Document both source IPs and the MFA method (push vs. number matching vs. CAC).",
        ),
        _triage(
            "A new domain-admin equivalent account was created outside the change window. Walk through the triage.",
            "1. Treat this as high priority even if it might be a late change ticket. Privileged group additions are a classic persistence step.\n\n"
            "2. Identify who created it (admin ID, source host, time) and whether that admin's own session looks normal.\n\n"
            "3. Check whether the new account is in the PAM/vault workflow or is an undocumented standing admin.\n\n"
            "4. If not an approved change, disable the new account, remove group membership, and hunt for other group-policy or GPO changes in the same window.\n\n"
            "5. Notify IR/ISSO. This may become both an incident and a CM-3/AC-2 package discussion later - triage first, paperwork second.",
        ),
        _triage(
            "SOC sees a burst of MFA push denials followed by one approval on a privileged user. How do you triage MFA fatigue?",
            "1. Call or out-of-band contact the user before trusting the approval. Fatigue attacks rely on the user accepting to make the noise stop.\n\n"
            "2. Inspect the successful session: new user-agent, new ASN, first-time application.\n\n"
            "3. Revoke sessions and reset/phish-resistant factors if the user did not initiate the prompts.\n\n"
            "4. Check whether number-matching or phishing-resistant MFA is required for this role - a detection-only response is incomplete if the control can be strengthened.\n\n"
            "5. Escalate if the session accessed mail forwarding, cloud consoles, or jump hosts.",
        ),
        _triage(
            "An alert says a disabled account just authenticated successfully. Walk through triage.",
            "1. Confirm the IdP/AD still shows disabled. If it is enabled again, that is a mover/rehire or an unauthorized re-enable - check who changed the account.\n\n"
            "2. If still disabled but a token works, suspect a still-valid refresh token, a replica lag, or a shadow account with the same UPN.\n\n"
            "3. Revoke tokens, kill sessions, and search for mailbox rules and app consents created after the disable date.\n\n"
            "4. This is higher severity than a disabled account failing to log in (which is the control working).\n\n"
            "5. ISSO note: PS-4 offboarding may have been incomplete; open a ticket/POA&M if the process gap is real.",
        ),
        _triage(
            "Triage a password-spray pattern: many users, few attempts each, from one source IP, mostly failures plus two successes.",
            "1. Password spray is intentionally below typical lockout thresholds. Do not dismiss because no account locked.\n\n"
            "2. Identify the two successes: privilege level, MFA status, whether those passwords were known-reused.\n\n"
            "3. Block or challenge the source IP/ASN if policy allows, and force password reset + session revoke on the successes.\n\n"
            "4. Search for the same source against VPN, email, and VPN-less SaaS.\n\n"
            "5. Escalate the successful logons as likely account compromise until proven otherwise.",
        ),
        _triage(
            "A SOC analyst sees Kerberos service-ticket request spikes consistent with Kerberoasting teaching patterns. What is a defensive triage (no exploit steps)?",
            "1. Identify which service principal names were requested in volume and whether those accounts have weak/old passwords (the actual risk).\n\n"
            "2. Check whether the requesting host/user is a known admin jumphost or an unusual workstation.\n\n"
            "3. Do not 'test the attack' against production. Involve IR to validate with logs and directory hygiene (long random service-account secrets, gMSA where appropriate).\n\n"
            "4. Contain by resetting suspected exposed service-account secrets from the vault workflow, not by emailing a new password.\n\n"
            "5. Document for ISSO: this is an IA-5/AC-6 hygiene issue as well as a possible incident.",
        ),
        _triage(
            "Walk through triage when Windows Security log shows audit log cleared on a domain controller.",
            "1. Clearing security logs on a DC is a high-signal event. Identify the user, source, and time, and whether it matches a documented maintenance procedure.\n\n"
            "2. If not documented, treat as suspected tampering: isolate administrative paths, preserve remaining logs (forwarded copies in SIEM may still exist - that is why AU-9 forwarding matters).\n\n"
            "3. Hunt for group changes, new accounts, and GPO edits in the same window from SIEM copies.\n\n"
            "4. Escalate immediately to IR. Do not rebuild the DC before evidence collection guidance.\n\n"
            "5. Process follow-up: if admins routinely clear logs, that is a control failure, not 'normal IT.'",
        ),
        _triage(
            "A new scheduled task appears on a server, created by a user who is not on the admin roster. How do you triage?",
            "1. Capture the task name, action (binary/script path), run-as account, and creator.\n\n"
            "2. Hash/path-review the payload with EDR; do not execute it to 'see what it does' on a production host.\n\n"
            "3. Check if config-management should have created it (benign drift) versus a unique name and a user-writable path (more suspicious).\n\n"
            "4. Disable the task if unauthorized, isolate the host if the payload looks malicious, and hunt for the same task name elsewhere.\n\n"
            "5. Escalate when the run-as identity is privileged or the binary is unsigned in a user directory.",
        ),
        _triage(
            "SOC notices SMB session spikes from a workstation to many file servers it never touches (possible lateral movement). Walk through triage.",
            "1. Confirm the source host's user and whether a scan/backup tool is supposed to do this. Admin jump boxes and vuln scanners can look similar - check change windows and scanner inventory.\n\n"
            "2. If it is a standard user workstation, this is more serious: check for newly dumped credentials in memory alerts, unusual processes, and concurrent VPN from elsewhere.\n\n"
            "3. Contain the workstation (network isolation) if lateral movement is plausible; reset the user's credentials and review privileged group use.\n\n"
            "4. Search SIEM for the same source hitting RDP/WinRM/LDAP.\n\n"
            "5. Escalate to IR; notify ISSO if a privileged credential may have been reused (POA&M-worthy hygiene later).",
        ),
        _triage(
            "A user reports they clicked a phishing link; minutes later a mailbox forwarding rule appears. How should SOC triage?",
            "1. Believe the user and act on the mailbox immediately: remove forwarding/inbox rules, revoke sessions, reset credentials, and review sent items for BEC-style fraud.\n\n"
            "2. Check OAuth consent grants and mobile-device enrollments added after the click time.\n\n"
            "3. Identify whether MFA was phished or bypassed; step up to phishing-resistant methods if available.\n\n"
            "4. Search for other mailboxes with rules created by the same session or IP.\n\n"
            "5. This is an incident, not a 'user education only' ticket, until mailbox persistence is gone.",
        ),
        _triage(
            "A dormant account with no logons for a year suddenly succeeds at VPN. Walk through triage.",
            "1. Dormant-then-active is a classic stolen-credential or rehire-without-process signal. Check HR/contractor status first.\n\n"
            "2. If the person should not have access, disable, revoke tokens, and treat as unauthorized access.\n\n"
            "3. If they were rehired, confirm the joiner process (screening, training, new approval) happened - successful VPN does not prove the process ran.\n\n"
            "4. Review what the session accessed. Year-old accounts often still have leftover groups (AC-2 failure).\n\n"
            "5. ISSO follow-up: unused-account disablement automation may have failed.",
        ),
        _triage(
            "After-hours VPN logon followed by internal port scanning from that user session. How do you triage?",
            "1. After-hours VPN can be benign. Internal scanning from a user workstation is not typical of a help-desk analyst - treat as hostile reconnaissance until a change ticket explains a scanner.\n\n"
            "2. Isolate the VPN session/host, revoke credentials, and check EDR for scan tools or living-off-the-land discovery commands.\n\n"
            "3. Correlate with failed logons on servers during the same window.\n\n"
            "4. Escalate to IR. Preserve VPN and firewall logs.\n\n"
            "5. Do not run your own aggressive scan 'to confirm' from another admin box in a way that destroys evidence or expands impact.",
        ),
        _triage(
            "EDR flags a large zip of file-share data staged in a user temp directory after hours. Walk through triage.",
            "1. Staging archives are a common pre-exfil step. Identify data sensitivity and whether a known backup or legal-hold tool created the zip.\n\n"
            "2. Check subsequent outbound transfers (cloud drive, email, USB, scp).\n\n"
            "3. If unexplained, isolate the host, disable the account, and hold the zip as evidence - do not email the zip around as 'FYI.'\n\n"
            "4. Escalate as potential data exposure; involve the ISSO/privacy officer if PII may be included.\n\n"
            "5. Later package lesson: DLP/egress use-cases (SI-4) may need a rule if none fired.",
        ),
        _triage(
            "WAF or EDR suggests a web shell file on an internet-facing IIS/Apache host. Defensive triage only.",
            "1. High priority. Snapshot/isolate the host per IR; do not 'clean the file' before memory/disk evidence if the playbook says preserve.\n\n"
            "2. Identify the write path (vulnerable app, weak credential, mispublished directory) from logs - for containment and the later POA&M, not for publishing exploit steps.\n\n"
            "3. Hunt for persistence (new tasks, new users, outbound beacons) on that host and peers.\n\n"
            "4. Rotate secrets that resided on the host. Rebuild from known-good images when IR says to.\n\n"
            "5. ISSO: this will likely become an IR-6 report plus RA-5/SI-2/CM-6 findings - do not hide it as a 'webmaster cleanup.'",
        ),
        _triage(
            "SOC sees periodic outbound connections every few minutes to a rare domain (possible beacon). How do you triage?",
            "1. Measure interval regularity, bytes, and whether the process is a browser versus an unsigned service binary.\n\n"
            "2. Check DNS/HTTP(S) destination reputation and first-seen time versus host build date.\n\n"
            "3. Benign lookalikes exist (update checks, telemetry). Confirm against software inventory before declaring C2.\n\n"
            "4. If the process is unexpected, isolate and escalate; capture the process hash and parent tree from EDR.\n\n"
            "5. Avoid paying the destination or interacting beyond approved intel lookups.",
        ),
        _triage(
            "A break-glass emergency admin account was used during business hours with no outage ticket. Walk through triage.",
            "1. Break-glass use is supposed to be rare and alarmed. Business-hours use without a Sev-1 ticket is suspicious or a process fail.\n\n"
            "2. Identify the source host and whether the vault checkout workflow was used.\n\n"
            "3. Review actions performed by that account (group changes, mailbox access, cloud IAM).\n\n"
            "4. If unauthorized, contain, rotate the break-glass secret, and hunt for other uses.\n\n"
            "5. If authorized but unalarmed, fix the detection (AU-6) and the vault process - still document as an event.",
        ),
        _triage(
            "Cloud console login from a new country for a tenant global-admin, MFA successful. How should SOC triage?",
            "1. Privileged cloud consoles are crown-jewel. Contact the admin out-of-band. New geo plus global-admin is isolate-first if they do not confirm.\n\n"
            "2. Review IAM changes, access-key creation, and federation changes in the same session.\n\n"
            "3. Revoke sessions, disable unused access keys, and require phishing-resistant MFA for that role.\n\n"
            "4. Check cloud trail for the same IP against other accounts.\n\n"
            "5. Notify the ISSO: this may be both IR and an IA-2/AC-6 residual-risk conversation.",
        ),
        _triage(
            "A service account used interactive RDP, but it is documented as 'batch only.' Walk through triage.",
            "1. Interactive use of a batch account is a strong misuse/compromise signal. Confirm the documentation and the AD 'logon locally / RDP' rights.\n\n"
            "2. Identify source workstation and whether a human is sharing that password (process fail) or an attacker is using it.\n\n"
            "3. Disable interactive rights, rotate the secret from the vault, and review what the session accessed.\n\n"
            "4. Escalate if the account is privileged or the source host is unusual.\n\n"
            "5. ISSO follow-up: AC-2/AC-6 implementation may not match the SSP.",
        ),
        _triage(
            "DNS query logs show long, regular queries with unusually long subdomains (possible tunneling). Defensive triage.",
            "1. Compare the domain to known software update and CDN patterns. Some security tools also use odd DNS.\n\n"
            "2. Identify the internal host and process making the queries via EDR/DNS logs.\n\n"
            "3. If unexplained and high-volume, isolate the host and escalate; do not attempt to 'decode the tunnel' on a production jumphost as a curiosity project.\n\n"
            "4. Check whether recursive resolvers should have blocked the parent domain (SI-4 use-case gap).\n\n"
            "5. Preserve pcap/DNS logs for IR.",
        ),
        _triage(
            "EDR alerts on encoded PowerShell launched by Office on a workstation. How do you triage defensively?",
            "1. Office spawning encoded PowerShell is a common malicious-document pattern, but some enterprise macros still do it. Check the parent file path, hash, and whether it came from email.\n\n"
            "2. Isolate the workstation if the document was unexpected. Do not open the sample on your own desktop.\n\n"
            "3. Pull the mailbox/delivery path; hunt the same hash across the fleet.\n\n"
            "4. Reset the user's credentials if callback or credential-prompt activity appears.\n\n"
            "5. Escalate to IR; later ISSO note if macros should have been blocked by policy (CM-7/SC).",
        ),
        _triage(
            "USB mass-storage insert on a server that has USB storage disabled in the STIG baseline - EDR still saw a mount. Walk through triage.",
            "1. Either the baseline drifted (CM-6) or someone overrode it. Confirm current GPO/config versus the alert.\n\n"
            "2. Identify the user at the console and the device serial if available. This may be unauthorized data movement (MP-2/MP-7).\n\n"
            "3. If the server holds sensitive data, treat as a potential incident, image/hold the USB if still present, and review file-copy logs.\n\n"
            "4. Re-apply the USB restriction and open a change/POA&M if drift is confirmed.\n\n"
            "5. Do not assume EDR was wrong because the SSP says USB is disabled.",
        ),
        _triage(
            "A guest or built-in Guest-style account showed a successful logon. How should SOC triage?",
            "1. Guest-style success on a modern baseline is unexpected. Confirm whether Guest is enabled (it should not be on most STIGs) and which host accepted it.\n\n"
            "2. Treat as high until proven to be a misnamed legitimate account. Disable Guest, isolate the host if it is a server, and hunt lateral use.\n\n"
            "3. Check whether a local policy GPO failed (CM-6 finding as well as IR).\n\n"
            "4. Escalate; do not close as informational because the volume is one event.",
        ),
        _triage(
            "SOC sees a new OAuth application consent for a high-privilege Graph/scope on a user's mailbox. Walk through triage.",
            "1. User-consented apps are a common persistence path. Check whether the app is publisher-verified and expected.\n\n"
            "2. If unexpected, revoke consent, revoke sessions, and review mail/files the app could have read.\n\n"
            "3. Search for the same client ID across the tenant.\n\n"
            "4. Tighten consent policies if users can grant risky scopes without admin approval (IA/AC control gap).\n\n"
            "5. Escalate if scopes include mail send, files read, or directory write.",
        ),
        _triage(
            "Honeytoken / canary credential was used to authenticate. How do you triage?",
            "1. Honeytoken use is never 'user error' in the normal sense - no legitimate workflow should use it. Treat as confirmed malicious interest at minimum.\n\n"
            "2. Capture source IP, host, and time; isolate that source if internal.\n\n"
            "3. Hunt what else that source touched. Rotate nearby real credentials of the same class (for example if the canary looked like a service account).\n\n"
            "4. Escalate immediately. Do not disable the canary without IR guidance - it is a detector.\n\n"
            "5. ISSO: document that the detector worked (SI-4), and that this is an incident not a POA&M FP.",
        ),
        _triage(
            "Time-sync on several hosts jumps unexpectedly, breaking Kerberos for users, then an admin logon succeeds. Why does SOC care?",
            "1. Large time jumps can be an operational NTP fault - or an attempt to manipulate log timelines / ticket validity. Check NTP sources and whether the jump is fleet-wide.\n\n"
            "2. Preserve logs with both original and SIEM receipt timestamps.\n\n"
            "3. If only a few high-value hosts jumped, raise suspicion and inspect who can change time (privileged right).\n\n"
            "4. Fix NTP (AU-8) but do not close the ticket until the admin logon is explained.\n\n"
            "5. Escalate if time change and privileged logon coincide without a change ticket.",
        ),
        _triage(
            "Print-spooler or similar high-risk service suddenly starts on a DC where the baseline disables it. Defensive triage.",
            "1. Service enablement against baseline is either drift or tampering. Confirm who started it and from where.\n\n"
            "2. Do not exploit the service to 'prove' risk. Disable per IR/change, isolate if unexplained, and collect service-creation events.\n\n"
            "3. Hunt for the same change on other DCs.\n\n"
            "4. ISSO follow-up: CM-6/CM-7 miss; POA&M if the baseline cannot be enforced.\n\n"
            "5. Escalate if the starter account is not a documented enterprise-admin change.",
        ),
        _triage(
            "A public cloud storage bucket containing [System Name] exports is suddenly world-readable according to a CSP finding. SOC/ISSO triage.",
            "1. This is both a possible exposure incident and a control fail (AC-3/SC-7/CM-3). Confirm the ACL/policy and whether objects are sensitive.\n\n"
            "2. Lock the bucket to private, review access logs for anonymous GETs, and involve IR/privacy if downloads occurred.\n\n"
            "3. Rotate any secrets that lived in the bucket.\n\n"
            "4. Do not leave it public 'until Monday' if logs show anonymous listing.\n\n"
            "5. Open a POA&M for the misconfiguration even if no download is proven - the control failed.",
        ),
        _triage(
            "API keys appearing in a public repository webhook alert (defensive). What should SOC do first?",
            "1. Treat the secret as exposed. Revoke/rotate the key in the vault/IdP before hunting git history for sport.\n\n"
            "2. Review API usage logs for the window the key was public.\n\n"
            "3. Remove the secret from the repo and notify the developers; do not commit a 'cleanup' that leaves the key in history without rotation.\n\n"
            "4. Escalate if the key was privileged or used after the commit time.\n\n"
            "5. ISSO: SA-11/IA-5 pipeline controls may need a secret-scan gate - that is a later POA&M, after containment.",
        ),
        _triage(
            "WAF blocks a sudden storm of requests that look like SQLi from a single botnet ASN. How do you triage versus an application incident?",
            "1. Blocks mean the WAF did its job (good). Still check whether any requests returned 200s with unusual sizes (possible bypass) and whether origin CPU/login errors spiked.\n\n"
            "2. If all blocked and origin healthy, document, tune if needed, and keep as intelligence - not every block is a breach.\n\n"
            "3. If some passed, pull application logs and treat as a possible successful injection attempt; involve app owners and IR.\n\n"
            "4. Do not paste raw attack strings into tickets that are widely readable if they include session tokens.\n\n"
            "5. ISSO note: SI-10/SC-7 evidence that the WAF is in blocking mode, not detect-only.",
        ),
        _triage(
            "Container runtime alerts on a process escaping to the node namespace (defensive). Walk through triage.",
            "1. High priority. Isolate the node/pod per IR; do not keep scheduling production pods on it.\n\n"
            "2. Identify the image, entrypoint, and whether it ran privileged or with dangerous capabilities (CM-7/SC-39 issues).\n\n"
            "3. Hunt for node-level persistence (new cron, new kube credentials).\n\n"
            "4. Rotate cluster credentials that were mounted to the pod.\n\n"
            "5. Escalate; later rebuild the node from a clean image. This is not a 'restart the pod' close.",
        ),
        _triage(
            "SOC sees successful logons for five users from the same hosting-provider IP that none of them use for VPN. How do you triage credential stuffing?",
            "1. Shared hosting IP plus multiple users is more stuffing/combo-list than five people on the same coffee shop.\n\n"
            "2. Check MFA: if password-only succeeded, contain all five (reset, revoke). If MFA also succeeded, still contact users - token/phishing possible.\n\n"
            "3. Block the IP/ASN if policy allows and search historical successes from it.\n\n"
            "4. Escalate the set as a cluster, not five isolated 'user forgot password' tickets.\n\n"
            "5. ISSO: IA-2/IA-5 residual risk if password-only is still allowed.",
        ),
        _triage(
            "A mailbox has a new hidden inbox rule deleting 'invoice' mail after a successful OWA logon from a rare ASN. Walk through triage.",
            "1. Classic BEC persistence. Remove the rule, revoke sessions, reset credentials, and review sent items and lookalike domains in sent mail.\n\n"
            "2. Warn finance/out-of-band if invoices or wire discussions exist.\n\n"
            "3. Hunt the same rule pattern tenant-wide.\n\n"
            "4. Escalate as an incident; this is not a junk-mail preference.\n\n"
            "5. Document times for IR-6 if reporting thresholds are met.",
        ),
        _triage(
            "EDR shows rundll32/living-off-the-land binaries with unusual parents on a jump host. Defensive triage.",
            "1. Jump hosts are high-value. Unusual LOLBin parents deserve isolation if not in the approved admin toolkit list.\n\n"
            "2. Collect the command line from EDR; do not re-run it to see what happens.\n\n"
            "3. Check the admin's other sessions and whether a ticket matches.\n\n"
            "4. Escalate when the parent is Office, a browser, or a user-writable path.\n\n"
            "5. Later: CM-7 allowlisting gaps are a package issue; containment is first.",
        ),
        _triage(
            "VPN split-tunnel appears enabled on a host that the SSP says must full-tunnel. SOC sees corporate and raw-internet egress. How do you triage?",
            "1. This can be malware bypass or a configuration drift. Confirm the actual VPN profile versus AC-17 SSP claims.\n\n"
            "2. If the user just switched to an unofficial client, treat as unauthorized remote-access path: disable, require the approved client, and review what left the raw interface.\n\n"
            "3. If malware is suspected (unexpected process holding the route), isolate and escalate.\n\n"
            "4. ISSO: this is a control implementation mismatch even when no malware is found - possible POA&M.\n\n"
            "5. Do not close as 'VPN is noisy' without comparing to the approved profile.",
        ),
        _triage(
            "A certificate on a public VIP is replaced by an unexpected issuer overnight. What should SOC/ISSO triage include?",
            "1. Unexpected issuer can be a legitimate emergency reissue or an adversary-in-the-middle / unauthorized change. Compare to the SC-17 inventory and change tickets.\n\n"
            "2. Check who had access to the load-balancer/cert store and whether ACME or a human issued it.\n\n"
            "3. If unauthorized, pull the VIP, restore the known certificate, and treat as incident (integrity of auth path).\n\n"
            "4. Review whether users received new trust-prompt phishing around the same time.\n\n"
            "5. Escalate; do not wait for the next monthly scan to notice TLS identity changed.",
        ),
        _triage(
            "SOC gets an alert that a user exported a large report of PII at 2 AM from an app they use daily at 2 PM. How do you triage?",
            "1. Volume plus odd hour is the anomaly, not the fact that they can export (their role may allow it).\n\n"
            "2. Contact the user/manager out-of-band. Confirm whether a legitimate deadline exists.\n\n"
            "3. If unexplained, disable export/download if the app allows, revoke sessions, and preserve the export audit record.\n\n"
            "4. Involve privacy/ISSO if the export left the boundary (email, USB, personal cloud).\n\n"
            "5. This can be insider-risk or account takeover - do not assume which without the session/device context.",
        ),
        _triage(
            "Multiple workstations show the same rare hash 10 minutes after a software-deployment job. How do you avoid a false incident?",
            "1. Check the software-distribution change ticket and publisher signature first. Mass-rare-hash right after a push is often the new agent.\n\n"
            "2. If the hash is unsigned or not in the catalog, isolate a sample host and escalate - worms also move fast.\n\n"
            "3. Compare parent process: SCCM/Intune versus WinWord.\n\n"
            "4. Document the benign case so the next shift does not re-page.\n\n"
            "5. If malicious, this is fleet IR, not 200 separate user tickets without a commander.",
        ),
        _triage(
            "A contractor's VPN account is used from their usual city and from a second country the same afternoon after they returned their laptop. Walk through triage.",
            "1. Returned laptop plus still-valid VPN is an offboarding fail (PS-4) and possibly stolen credentials.\n\n"
            "2. Disable the account immediately, revoke tokens, and see which session was the laptop versus the foreign IP.\n\n"
            "3. Review access after the return date - anything after physical return is unauthorized unless a new approval exists.\n\n"
            "4. Escalate the foreign session; notify contracting officer/ISSO.\n\n"
            "5. Process POA&M: accounts must expire with the start date of asset return, not 'when someone remembers.'",
        ),
        _triage(
            "SIEM correlation: successful privileged logon, then immediate download of NTDS or similar directory database alert from EDR. Defensive triage.",
            "1. Treat as suspected domain compromise until IR says otherwise. Isolate the source host and disable the privileged account.\n\n"
            "2. Preserve EDR artifacts; do not copy NTDS-like files around for curiosity.\n\n"
            "3. Assume secrets may be exposed: plan credential resets with IR (krbtgt and privileged accounts are IR-led, not a solo SOC experiment).\n\n"
            "4. Notify ISSO/ISSM/AO path per the IR plan - this is reportable in most regimes if confirmed.\n\n"
            "5. Later package work is secondary to containment.",
        ),
        _triage(
            "Users report MFA prompts at 4 AM; none approved. How do you triage versus MFA fatigue with a success?",
            "1. Prompts with zero approvals are often password-stuffing or spray that hit MFA and stopped. Still identify the source IPs and targeted accounts (especially admins).\n\n"
            "2. Confirm no sneaky success in a different application.\n\n"
            "3. Block the source if appropriate; tell targeted admins out-of-band.\n\n"
            "4. Lower urgency than an approval-after-spam, but do not ignore admin-targeted sprays.\n\n"
            "5. Document as attempted access; escalate if an admin account shows any success.",
        ),
        _triage(
            "A jump-host session records show clipboard transfer of a large text blob that looks like a secret dump. What should SOC do?",
            "1. Privileged session recording exists to catch this. Pause/disable the account, preserve the recording, and treat as possible credential theft or insider exfil.\n\n"
            "2. Rotate the implied secrets once IR agrees on scope - do not paste the blob into chat tools.\n\n"
            "3. Check whether the session was the real admin (call them) or a hijacked session.\n\n"
            "4. Escalate. This is why MA-4/AC-17 session logging is in the SSP.\n\n"
            "5. Do not play back the recording on a personal laptop.",
        ),
        _triage(
            "SOC alert: security group that grants production data-store access was widened to 'Authenticated Users' by a terraform apply. Walk through triage.",
            "1. This may be a bad pipeline change rather than an external attacker - still an incident-class exposure until the ACL is tight again.\n\n"
            "2. Revert the ACL immediately (CM-3 emergency), then identify who approved the apply and whether credentials for the pipeline were abused.\n\n"
            "3. Review data-store access logs for the open window.\n\n"
            "4. Escalate if any unexpected principals read data.\n\n"
            "5. ISSO: POA&M for pipeline approval gaps (AC-5/CM-3) even if it was 'just a mistake.'",
        ),
    ]
