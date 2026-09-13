"""RMF process Q&A examples for CountGPT SFT."""

from __future__ import annotations


def examples() -> list[dict]:
    return [
        {
            "instruction": "Explain what an Authorizing Official (AO) does in the RMF process, in plain language for someone new to compliance work.",
            "output": (
                "The Authorizing Official is the person with the actual authority to say 'yes, this system can operate on our network' or 'no, not yet.' Think of them as the final decision-maker in the process - everyone else (the ISSO writing documentation, the assessor testing controls) is gathering and validating the evidence that the AO will use to make that call.\n\n"
                "The AO reviews the full authorization package - the System Security Plan, the Security Assessment Report, and the POA&M - to understand the system's current risk posture: what's implemented correctly, what's missing, and what the plan is to fix any gaps. Based on their risk tolerance and the severity of what remains open, the AO either grants an Authorization to Operate (ATO), grants a conditional/limited ATO with required follow-up actions, or denies authorization until specific issues are resolved.\n\n"
                "A key rule to know: an AO generally cannot approve a system for full authorization if it has any open control with a High or Very High residual risk - that has to be resolved or formally mitigated first."
            ),
        },
        {
            "instruction": "Explain the difference between the ISSO and ISSM roles in a DoD RMF context.",
            "output": (
                "The ISSO (Information System Security Officer) is typically the hands-on role for a single system - they write and maintain the System Security Plan, draft and track POA&M items, coordinate account management, and are the day-to-day point of contact for that system's security posture.\n\n"
                "The ISSM (Information System Security Manager) generally has broader oversight - often responsible for security across multiple systems or an entire program, and ultimately accountable for ensuring RMF is implemented correctly across everything under their purview. The ISSM often reviews and approves what the ISSO has documented before it moves forward in the authorization process.\n\n"
                "In practice, the two roles are frequently referenced together as 'ISSM/ISSO' because their responsibilities overlap closely, especially on smaller programs where one person may perform both functions. For someone entering the field, ISSO is typically the more common starting role, with ISSM being a step up in scope and seniority."
            ),
        },
        {
            "instruction": "Explain what 'Continuous Monitoring' means in the RMF process, in plain language.",
            "output": (
                "Continuous Monitoring is the ongoing, after-the-fact phase of RMF that happens once a system has already received its ATO - it's the answer to 'how do we make sure this system stays secure over time, instead of just checking once and walking away.'\n\n"
                "Rather than treating the authorization as a one-time snapshot, Continuous Monitoring requires the system owner to keep tracking things like: new vulnerability scan results, whether existing POA&M items are on schedule, whether any security-relevant changes have been made to the system, and whether previously implemented controls are still functioning as described.\n\n"
                "In practice, this means an ISSO doesn't stop working on a system's documentation after the ATO is granted - they continue updating the POA&M as new findings come in, re-validate controls periodically, and report status at scheduled review intervals (often annually, sometimes more frequently for higher-risk systems). If a significant security-relevant change happens, it may need to be reported and reviewed before the system can continue operating under its existing authorization."
            ),
        },
        {
            "instruction": "Explain what a Security Assessment Report (SAR) is and how it relates to the SSP and POA&M.",
            "output": (
                "The SAR is the document where an independent assessor reports the results of actually testing whether a system's controls work as described - it's the bridge between what the SSP claims and what the POA&M has to track.\n\n"
                "Here's how the three documents connect: the SSP describes how each control is supposedly implemented (like our AC-2 example describing Okta-based account management). The assessor then tests those specific claims and writes up the results in the SAR - confirming what worked as described and flagging what didn't. Any gap the SAR identifies becomes a finding, and every finding from the SAR must have a corresponding entry in the POA&M describing how and when it will be fixed.\n\n"
                "In short: SSP describes intended implementation, SAR reports whether that implementation actually held up under testing, and POA&M tracks the fixes for anything that didn't. An Authorizing Official reviews all three together to decide whether to grant an ATO."
            ),
        },
        {
            "instruction": "Explain what a Security Requirements Traceability Matrix (SRTM) is and how it's used in the RMF process.",
            "output": (
                "An SRTM is a document that maps each individual security requirement (typically each applicable NIST 800-53 control) to specific evidence of how it's satisfied - essentially a tracking spreadsheet that ensures nothing required gets overlooked.\n\n"
                "How it's used: for every control in a system's applicable baseline, the SRTM lists the control, a brief description of the requirement, how the system addresses it (or a reference to where that's documented in the SSP), the responsible party, and its current implementation status.\n\n"
                "Why it matters: it gives an assessor and the ISSO a single, scannable view of the entire control set's status, rather than having to search through hundreds of pages of narrative in the SSP to determine whether something specific was addressed. It's also commonly used to track and justify any approved deviations from standard STIG or control requirements, tying each exception back to a specific approval."
            ),
        },
        {
            "instruction": "Walk through the NIST RMF steps in order and say what artifact usually shows up at each step.",
            "output": (
                "Common teaching sequence (NIST SP 800-37):\n\n"
                "1. Prepare - organization and system context, roles, risk strategy. Artifact: program policies, categorization inputs.\n"
                "2. Categorize - FIPS 199 / CNSSI 1253 impact. Artifact: signed categorization.\n"
                "3. Select - baseline, overlays, tailoring, overlays. Artifact: control set / SRTM starting point.\n"
                "4. Implement - build the controls. Artifact: SSP implementation statements, diagrams.\n"
                "5. Assess - independent test. Artifact: SAP then SAR.\n"
                "6. Authorize - AO risk decision. Artifact: ATO letter/eMASS authorization, conditions.\n"
                "7. Monitor - ConMon, ongoing scans, POA&M, significant change. Artifact: ConMon reports, updated POA&M/SSP.\n\n"
                "The steps loop; Monitor often sends you back to implement/assess for a change. This is a learning outline, not a substitute for 800-37."
            ),
        },
        {
            "instruction": "What is the difference between an ATO, a conditional/limited ATO, and a denial?",
            "output": (
                "An Authorization to Operate (ATO) means the AO accepted the residual risk for a stated period and the system may run in production under the documented conditions.\n\n"
                "A conditional or time-limited authorization still allows operation, but the AO attaches mandatory actions and dates (often High/Moderate POA&M items). Missing those conditions can suspend the authorization.\n\n"
                "A denial (or authorization not granted) means the AO did not accept the residual risk. The system should not operate in production, or must stop, until named issues are fixed and the package is re-presented.\n\n"
                "CountGPT cannot issue any of these. They are AO decisions recorded in the official GRC system."
            ),
        },
        {
            "instruction": "What is an IATT or IATO, and when do people use those terms instead of a full ATO?",
            "output": (
                "Programs sometimes use Interim Authority To Test (IATT) or similar interim language for a tightly scoped, time-boxed permission to connect or test before a full ATO - for example to run assessment scans on a range. Exact names and rules are organizational (DoD components differ).\n\n"
                "These are not informal 'the ISSO said it was OK.' They still need the designated authorizing official (or delegated official) and a written scope: what may connect, for how long, and what data is allowed.\n\n"
                "If your organization does not use IATT/IATO, do not put those acronyms in the SSP to sound official. Ask the ISSM what authorization types exist locally."
            ),
        },
        {
            "instruction": "Explain authorization reciprocity in plain language (DoD and FedRAMP flavors).",
            "output": (
                "Reciprocity means one AO may choose to reuse another authorization package instead of re-testing everything, when the boundary, overlay, and residual risk are close enough.\n\n"
                "FedRAMP is a common pattern: a JAB or agency authorization of a cloud service can be leveraged by other agencies, who still accept residual risk for their use and still own customer-responsibility controls.\n\n"
                "DoD reciprocity is similar in spirit but overlays (SRGs, impact levels, classified data) often block a straight copy-paste of a civilian package. Reciprocity is an AO decision, not an ISSO shortcut to skip the POA&M."
            ),
        },
        {
            "instruction": "What is the difference between a common control, a hybrid control, and a system-specific control?",
            "output": (
                "A common control is implemented once by a provider (for example a data-center PE control or an enterprise IdP) and inherited by many systems. The child SSP points to the provider package instead of rewriting the implementation.\n\n"
                "A system-specific control is implemented entirely inside this system's boundary (for example this application's AC-3 role checks).\n\n"
                "A hybrid control is split: part inherited, part local (for example the CSP encrypts disks, the customer manages application keys). Hybrid statements must say who does which piece, or assessors will test the wrong owner.\n\n"
                "Inheritance does not make residual risk disappear from the AO's view if the provider's control is weak or overdue."
            ),
        },
        {
            "instruction": "What is a control overlay in RMF, using a DoD or privacy example?",
            "output": (
                "An overlay is an extra set of control selections or parameter settings on top of the NIST baseline, written for a community (DoD, privacy, classified, industrial control, and so on).\n\n"
                "Example: a DoD system may apply CNSSI 1253 and DoD overlays that add enhancements the civilian Moderate baseline would not. A system that processes PII may apply a privacy overlay (PT family emphasis).\n\n"
                "Overlays are selected during Select, documented in the SSP, and tested in the SAR. You cannot 'forget' an overlay at assessment time because the SSP narrative was written to the lighter baseline."
            ),
        },
        {
            "instruction": "Explain tailoring versus 'we just skipped that control.'",
            "output": (
                "Tailoring is the documented, justified adjustment of the baseline: dropping a control that cannot apply (no wireless, therefore AC-18 not selected), adding extras, or setting organization-defined parameters.\n\n"
                "Skipping is leaving a selected control unimplemented without a tailoring statement, inheritance, or POA&M. Assessors treat that as a fail.\n\n"
                "Not applicable still needs a one-line reason an assessor can verify (for example 'no wireless interfaces in the boundary')."
            ),
        },
        {
            "instruction": "How does FIPS 199 categorization work, including the high-water mark?",
            "output": (
                "You rate the potential impact of a loss of confidentiality, integrity, and availability as Low, Moderate, or High for the system's information types (FIPS 199 / SP 800-60 guidance).\n\n"
                "The system's overall impact is the high-water mark: the highest of the three. A system that is Low/Low/High is still a High-impact system for baseline selection.\n\n"
                "DoD often uses CNSSI 1253, which can result in more granular CIA selections than a single high-water mark, but the teaching idea is the same: honest data types drive the baseline. Recategorize when the data or mission changes."
            ),
        },
        {
            "instruction": "What is residual risk in an ATO decision?",
            "output": (
                "Residual risk is the leftover risk after implemented controls, compensating controls, and accepted gaps. No system is risk-free; the AO is paid to accept or reject that leftover.\n\n"
                "It is not the same as scanner severity. A High plugin behind a documented, tested isolation may be proposed for adjustment; a Low item that is a year overdue can still be a ConMon problem.\n\n"
                "The POA&M plus SAR plus SSP are how residual risk is shown. A verbal 'we're okay with it' from the ISSO is not residual-risk acceptance."
            ),
        },
        {
            "instruction": "What is the difference between a 3PAO and a Security Control Assessor (SCA)?",
            "output": (
                "Both are independent testers relative to the people who implemented the system. A 3PAO (Third Party Assessment Organization) is the FedRAMP-style accredited commercial assessor that produces the SAR for many cloud packages.\n\n"
                "SCA (or SCA-V in some DoD usage) is the assessor role more generally - it may be an organic government assessment team rather than a FedRAMP 3PAO.\n\n"
                "Neither is the AO. They report findings; they do not grant the ATO. The ISSO should not assess their own system for the authorization SAR."
            ),
        },
        {
            "instruction": "What is eMASS, and what does CountGPT not do with it?",
            "output": (
                "eMASS is a government GRC application used by many DoD programs as the official system of record for SSPs, POA&Ms, and authorization workflow.\n\n"
                "CountGPT can help you practice the wording that later gets typed into eMASS. It does not log in, submit packages, or change official status. Treat generated text as a draft you still validate against your local eMASS business rules and overlays."
            ),
        },
        {
            "instruction": "What is a Security Assessment Plan (SAP) and how is it different from the SAR?",
            "output": (
                "The SAP is written before testing. It says what will be tested, which methods (examine, interview, test), the schedule, and the rules of engagement.\n\n"
                "The SAR is written after testing. It records what happened, what passed, what failed, and residual risk.\n\n"
                "If the team skips the SAP, the assessment is harder to scope and easier to dispute. If they skip the SAR, the AO has no independent results package."
            ),
        },
        {
            "instruction": "What is a Risk Assessment Report (RAR) versus the SAR?",
            "output": (
                "A SAR is the assessor's control-test report. A Risk Assessment Report (when a program uses that name) is a broader likelihood/impact analysis of threats and residual risk, sometimes produced by the ISSO/ISSM rather than the SCA.\n\n"
                "Programs vary: some fold risk analysis into the SAR or eMASS fields and do not keep a separate RAR. Use the name your AO expects. Do not treat a scanner PDF as either document."
            ),
        },
        {
            "instruction": "Explain examine, interview, and test as 800-53A assessment methods.",
            "output": (
                "Examine means the assessor reviews artifacts (SSP text, policies, configs, tickets, diagrams).\n\n"
                "Interview means they ask people how the control actually works and listen for mismatches with the SSP.\n\n"
                "Test means they exercise the control (try a denied access, inspect a scan, watch a restore).\n\n"
                "A control that only has a paragraph in the SSP has been examined at best. Strong packages expect test evidence on technical controls."
            ),
        },
        {
            "instruction": "What is a significant change in RMF, and why does it matter after ATO?",
            "output": (
                "A significant change is a security-relevant change large enough that the existing authorization may no longer match the system: new external connection, new data type, new cloud region, removal of a compensating control, and similar.\n\n"
                "It is not every ticket. It is also not 'only if we feel like telling the AO.' The ISSO/ISSM compare the change to the documented boundary and control implementations, then notify the AO per policy - sometimes with a re-assessment of affected controls.\n\n"
                "Shipping a new internet API and updating the SSP next year is a common failure mode."
            ),
        },
        {
            "instruction": "What is an authorization boundary, and why do ISSOs argue about it?",
            "output": (
                "The authorization boundary is the set of components, networks, and data flows the ATO covers. Inside: you implement, scan, and assess. Outside: someone else's package or an interconnection agreement.\n\n"
                "Arguments happen when a jump host, a shared logging system, or a customer tenant plugin sits on the line. The diagram and inventory (CM-8) must match. A host you scan but claim is out of scope, or a host you do not scan but claim is in scope, will fail a careful assessment."
            ),
        },
        {
            "instruction": "What is an Interconnection Security Agreement (ISA) or MOU in this process?",
            "output": (
                "When two systems exchange data or users across authorization boundaries, programs typically require a written agreement (ISA, MOU/MOA, or equivalent) that states what data, what protections, and who reports incidents.\n\n"
                "The technical allowlist (ports, crypto, IPs) should match the paper. A live circuit with an expired ISA is a CA-3 / AC-20 problem, not a paperwork nicety."
            ),
        },
        {
            "instruction": "Explain type authorization versus site authorization in plain language.",
            "output": (
                "A type authorization covers a standard system design that will be instantiated more than once (a product image, a kit). A site authorization covers a specific instance at a location, including local PE and local connections.\n\n"
                "Many programs combine them: inherit the type package, then add site-specific controls and a site AO decision. Copying a type ATO to a site with extra interconnections without a site review is not reciprocity magic."
            ),
        },
        {
            "instruction": "What are DoD Information Impact Levels (IL2, IL4, IL5, IL6) at a teaching level?",
            "output": (
                "Impact levels are DoD cloud/hosting labels for the sensitivity of information and the required isolation (for example publicly releasable versus controlled unclassified versus classified). Exact definitions live in current DoD cloud SRG/policy - do not treat a blog post as the overlay.\n\n"
                "Teaching point: the impact level drives where the system may be hosted and which overlays apply. An IL5 mission on an IL2 commercial tenant is a categorization and hosting fail, not an SSP wording issue.\n\n"
                "Always confirm the current SRG language for a real package."
            ),
        },
        {
            "instruction": "How does FedRAMP relate to NIST RMF without treating FedRAMP as a different physics?",
            "output": (
                "FedRAMP is RMF applied to cloud services with a standardized baseline, 3PAO assessments, a POA&M format, and a marketplace so agencies can leverage a package.\n\n"
                "The agency still has customer-responsibility controls and still has an AO (or equivalent) for their use of the service. A FedRAMP authorization is not a government-wide hall pass to skip agency privacy, identity, or data-type reviews."
            ),
        },
        {
            "instruction": "What is the difference between NIST SP 800-53 and 800-53A?",
            "output": (
                "800-53 is the catalog of controls (what to implement). 800-53A is the assessment catalog (how an assessor might examine, interview, and test those controls, including objectives).\n\n"
                "SSP writers implement 800-53. Assessors often structure the SAP/SAR around 800-53A objectives. Writing SSP statements that cannot be tested against 800-53A objectives is how you get 'implemented' on paper and 'failed' in the SAR."
            ),
        },
        {
            "instruction": "How does NIST 800-171 relate to 800-53 without mixing CMMC marketing into the answer?",
            "output": (
                "800-171 is a subset-style set of requirements aimed at protecting Controlled Unclassified Information in nonfederal systems. 800-53 is the broader federal catalog used in RMF baselines.\n\n"
                "Some 800-171 requirements map to 800-53 controls, but a Moderate 800-53 package is not automatically an 800-171 assessment, and the reverse is not a full RMF ATO. Use the framework your contract actually cites."
            ),
        },
        {
            "instruction": "What is a Control Correlation Identifier (CCI) and why do STIGs mention them?",
            "output": (
                "A CCI is a DoD-style identifier that maps a granular assessment item (often a STIG check) to NIST control language. It helps automated tools and eMASS show that a configuration check supports, for example, CM-6 or AC-3.\n\n"
                "A passed CCI/STIG check is evidence toward a control, not a full control assessment by itself. A failed CCI is usually a STIG/POA&M item, not a CVE."
            ),
        },
        {
            "instruction": "What does CNSSI 1253 change compared with a plain FIPS 199 high-water-mark baseline?",
            "output": (
                "CNSSI 1253 is used in many national-security systems to select 800-53 controls using confidentiality, integrity, and availability impact independently, plus overlays, rather than only one high-water-mark baseline.\n\n"
                "Teaching point: two systems with the same 'Moderate' nickname may have different selected enhancements. Always export the actual selected set from eMASS/the SRTM instead of assuming the NIST Moderate PDF is the whole story."
            ),
        },
        {
            "instruction": "Who is the System Owner versus the ISSO?",
            "output": (
                "The system owner is accountable for the mission system: resources, operations, and supporting the authorization. The ISSO is the security officer who maintains the package and day-to-day security coordination.\n\n"
                "The owner does not get to skip POA&M work because they are 'not the security person,' and the ISSO does not get to accept residual risk that belongs to the AO. On small programs one person may wear both hats - document that, because independence of assessment still matters."
            ),
        },
        {
            "instruction": "What is an Authorization Termination Date (ATD) and what should an ISSO do as it approaches?",
            "output": (
                "The ATD is when the current authorization ends unless the AO renews or reauthorizes. It is not a suggestion.\n\n"
                "As it approaches, the ISSO should already have current ConMon evidence, a current POA&M, and any required re-assessment scheduled. Showing up at the ATD with stale scans and overdue Highs is how programs get short extensions - or a stop."
            ),
        },
        {
            "instruction": "What happens in decommission from an RMF paperwork view?",
            "output": (
                "Decommission is a controlled end of authorization: data disposition (MP-6, privacy), account removal, inventory retirement, interconnection teardown, and a record that the system is no longer authorized to process.\n\n"
                "Turning off VMs without sanitization evidence or leaving stale scan targets in ACAS is an incomplete decommission. The AO/ISSM should see a closure package, not silence."
            ),
        },
        {
            "instruction": "Explain 'organization-defined parameter' (ODP) or assignment in 800-53 language.",
            "output": (
                "Many controls say the organization assigns a value: how many failed logons, how long to retain logs, how often to scan. Those assignments must be written (policy or SSP) so an assessor can test against a number, not against 'we do something reasonable.'\n\n"
                "If the user did not give the number, keep a placeholder like [organization-defined period] rather than inventing 90 days and presenting it as law."
            ),
        },
        {
            "instruction": "What is a body of evidence in an authorization package?",
            "output": (
                "The body of evidence is the collection of artifacts that back the SSP claims: diagrams, policies, scan reports, training rosters, tickets, ISA letters, inheritance letters, and the SAR.\n\n"
                "eMASS fields without attachments are a weak body of evidence. A huge zip of unexplained screenshots is also weak. Map each selected control to a retrievable artifact (that is what the SRTM is for)."
            ),
        },
        {
            "instruction": "Why must the assessor be independent of the ISSO who wrote the SSP?",
            "output": (
                "If the same person writes the implementation and grades it, the SAR is a self-grade. RMF expects an SCA/3PAO (or equivalent independent team) to test claims.\n\n"
                "Independence is about bias, not about being rude. The ISSO should still attend interviews and fetch evidence. They should not rewrite SAR fails into passes without a retest."
            ),
        },
        {
            "instruction": "What is a Plan of Action versus a milestone on a POA&M row?",
            "output": (
                "The plan of action is what you will do (patch, isolate, replace, accept). Milestones are dated checkpoints that show the plan is real (staging by X, production by Y, validate by Z).\n\n"
                "A row with a vague action and no dates is not a plan. A row with dates that never move after they expire is not Continuous Monitoring."
            ),
        },
        {
            "instruction": "How should inherited POA&Ms from a common-control provider show up for a child system?",
            "output": (
                "The child package should reference the provider's open items that affect inherited controls, especially Highs. The child ISSO monitors status; they do not invent a local fix they cannot perform.\n\n"
                "The child's AO still sees that residual risk. 'Inherited' is not a synonym for 'Closed.'"
            ),
        },
        {
            "instruction": "What is a privacy overlay / PT family doing in an otherwise 'security' package?",
            "output": (
                "When the system processes PII, privacy controls (PT family and related) describe authority, minimization, notices, and individual participation - not just encryption.\n\n"
                "A technically hardened system that collects extra PII without authority still fails. Security ISSOs should not ignore PT because it 'belongs to the privacy office' - the AO package is one package."
            ),
        },
        {
            "instruction": "Explain P-ATO versus an agency ATO in FedRAMP conversation.",
            "output": (
                "A provisional authorization (often JAB P-ATO in FedRAMP talk) is a central provisional decision that agencies may leverage. An agency ATO is that agency's AO accepting residual risk for their use, including customer responsibilities.\n\n"
                "Agencies still have work after a P-ATO: identity integration, their data types, their POA&Ms. Exact FedRAMP labels change over time - confirm current FedRAMP documentation for a live package."
            ),
        },
        {
            "instruction": "What is Continuous Monitoring 'operational visibility' versus a once-a-year paperwork refresh?",
            "output": (
                "Operational visibility means someone is actually looking at scans, tickets, and incidents on a defined cadence and escalating. A once-a-year SSP font update is not ConMon.\n\n"
                "CA-7 strategies usually mix automated feeds (scans, inventory) with periodic control sampling. If the only update is the week before the AO briefing, the process already failed."
            ),
        },
        {
            "instruction": "What should an ISSO do first on Monday after a new ACAS High appears?",
            "output": (
                "Validate the asset is in the boundary and the scan was credentialed enough to trust. Confirm whether it is new versus a recurrence. Open or update the POA&M with the real discovery date, plugin placeholder if needed, and a 30-day-style plan if that is the local High clock.\n\n"
                "Tell the implementer and ISSM if exposure is internet-facing. Do not wait for the annual assessment. Do not invent a plugin ID if the export is blank."
            ),
        },
        {
            "instruction": "How do authorization conditions differ from POA&M milestones?",
            "output": (
                "POA&M milestones are the system's plan to close weaknesses. Authorization conditions are the AO's extra requirements attached to the decision (report monthly, no internet until X is fixed, retest control Y in 90 days).\n\n"
                "You can meet a milestone and still violate a condition if you forgot to send the AO the required report. Track both."
            ),
        },
        {
            "instruction": "What is a Security CONOPS and when is it useful?",
            "output": (
                "A security concept of operations describes in narrative how users, admins, and data actually move - useful when the SSP control list is too fragmented for a new assessor or AO to understand the system.\n\n"
                "It does not replace implementation statements. If the CONOPS says 'all admin is via CAC VPN' and the SSP AC-17 says something else, the package is inconsistent."
            ),
        },
        {
            "instruction": "Explain 'common control provider' responsibilities to a new ISSM.",
            "output": (
                "If you offer a common control (enterprise logging, facility, IdP), you maintain that implementation, assess it, track its POA&Ms, and give inheriting systems a current inheritance letter or package excerpt.\n\n"
                "When your High is overdue, you notify inheritors. You do not tell them to hide it. Child ISSOs should ping you when their AO asks for status, rather than guessing."
            ),
        },
        {
            "instruction": "What is the difference between risk acceptance and a false positive?",
            "output": (
                "A false positive means the reported weakness is not really there. Risk acceptance means the weakness is there (or might be) and the AO agrees to operate anyway for a time.\n\n"
                "Using FP to hide a real weakness is incorrect. Using acceptance without an AO is also incorrect. Risk adjustment is a third path: severity changes because of extra evidence, still usually pending assessor/AO validation."
            ),
        },
        {
            "instruction": "How does a SAR fail become a POA&M row if there is no CVE?",
            "output": (
                "Copy the SAR finding title, control ID, assessor severity, and the test that failed. Detector source is SAR/manual, not ACAS. Closure evidence is a retest of that objective, not a green plugin dashboard.\n\n"
                "Every open SAR fail that remains at authorization time should be visible to the AO in the POA&M."
            ),
        },
        {
            "instruction": "What is 'high water mark' versus 'not all High systems are equal' for a new ISSO?",
            "output": (
                "The high-water mark sets the baseline selection. Two High systems can still have different data (health records versus a High-availability empty web banner) and different overlays.\n\n"
                "Do not tell the AO that High-water-mark High means the same residual risk as another High system. Categorization starts the conversation; the SAR and POA&M finish it."
            ),
        },
        {
            "instruction": "Explain the AO, SCA, ISSO triangle when they disagree about a finding.",
            "output": (
                "The SCA records what they observed. The ISSO may dispute with evidence (wrong host, patch already in, test method wrong). The AO decides whether to authorize with that residual risk if the dispute is unresolved.\n\n"
                "The ISSO does not unilaterally delete a SAR fail. The SCA does not grant the ATO. Email tone does not replace evidence."
            ),
        },
        {
            "instruction": "What is a PIT system (Platform IT) in DoD conversation, at a teaching level?",
            "output": (
                "Platform IT often means hardware/software integral to a weapons or industrial platform rather than a general-purpose business enclave. Authorization and overlay rules can differ, and some controls are not realistic in the same way as an office web app.\n\n"
                "Teaching point: do not force a business-system SSP template onto PIT without the component's overlay. Confirm current DoD policy for the platform type."
            ),
        },
        {
            "instruction": "How should an ISSO describe 'operational requirement' (OR) to an AO?",
            "output": (
                "An operational requirement is a request to keep operating with a known weakness for a mission reason, with compensating controls and an end date. It is not a lower scanner severity and not a false positive.\n\n"
                "The AO may grant, shorten, or deny it. If denied, the system follows the normal High/Moderate clock or stops the risky function."
            ),
        },
        {
            "instruction": "What artifacts does a new ISSO usually touch in the first 30 days on a live ATO system?",
            "output": (
                "Read the current SSP boundary diagram, the open POA&M, the last SAR, the last scan cycle, the inheritance letters, and the IR/CP plans. Meet the system owner and the people who actually change GPO, cloud ACLs, and the SIEM.\n\n"
                "Then fix stale dates and obvious SSP lies (named tools that were decommissioned). Do not rewrite the entire SSP from scratch in week one unless the ISSM asked for that."
            ),
        },
        {
            "instruction": "Why can an AO decline a full ATO for open High residual risk even if the mission is urgent?",
            "output": (
                "Urgency is an input to risk decisions, not an automatic override. Many policies tell AOs not to fully authorize open High residual risk without documented mitigation and a time box.\n\n"
                "The AO can still choose a very short conditional authorization or a limited scope (test only, no production data). That is still an explicit decision, not ISSO improvisation."
            ),
        },
        {
            "instruction": "What is the relationship between the SSP control implementation and an assessor's test case?",
            "output": (
                "A good implementation statement names the who/what/where an assessor can repeat: tool, event types, review cadence, and a customer-responsibility split.\n\n"
                "If the statement is only 'the system complies with AC-2,' the assessor has nothing to test except your optimism. That usually becomes a documentation fail or a weak 'implemented' that collapses in interview."
            ),
        },
        {
            "instruction": "Explain 'leverage' in FedRAMP versus 'copy the SSP into our agency template.'",
            "output": (
                "Leverage means reuse the CSP's assessed baseline and residual-risk picture, then add your customer-responsibility implementation and your data types.\n\n"
                "Copying CSP SSP prose into an agency template as if you implemented the hypervisor is incorrect and will fail interviews. Quote inheritance, do not impersonate the CSP."
            ),
        },
        {
            "instruction": "What is a Security Control Assessor Representative or similar support role, versus the AO?",
            "output": (
                "Some organizations assign people to help the SCA gather evidence or to advise the AO technically. They still are not the AO and usually are not the ISSO.\n\n"
                "If your org chart uses extra acronyms, write down who can actually change authorization status. Title inflation does not close POA&Ms."
            ),
        },
        {
            "instruction": "How do you explain 'authorization to use' a shared service versus authorizing your own system?",
            "output": (
                "When you consume a shared enterprise service (email, IdP), you typically inherit that service's authorization and still authorize your own system that relies on it.\n\n"
                "Your ATO does not re-authorize the enterprise IdP. The enterprise IdP ATO does not automatically authorize your application to hold High data. Two boundaries, two decisions, one interconnection story."
            ),
        },
        {
            "instruction": "What should be true before an ISSO marks a control 'implemented' in eMASS?",
            "output": (
                "The implementation exists in production (or the inherited provider), the SSP statement matches reality, and you can point to evidence. Planned or 'in progress' is not implemented.\n\n"
                "Partially implemented belongs with a POA&M. Implemented with a known High gap is how packages lose assessor trust."
            ),
        },
        {
            "instruction": "Explain the difference between a policy control (xx-1) and a technical control for a beginner.",
            "output": (
                "Family '-1' controls are usually about having current policy and procedures. They are real, but an assessor who only sees a policy PDF has not tested whether accounts are actually reviewed (AC-2) or logs actually exist (AU-2).\n\n"
                "Beginners often spend weeks polishing AC-1 text while AC-2 is failing in the directory. Do both; do not confuse them."
            ),
        },
        {
            "instruction": "What is 'ongoing authorization' language trying to say?",
            "output": (
                "Some programs emphasize that authorization is maintained through ConMon rather than a giant every-three-years rewrite. You still have an AO, an ATD or continuous decision process, and you still report residual risk.\n\n"
                "Ongoing authorization is not 'we never assess again.' It is 'assessment and risk reporting are continuous enough that the AO stays informed.'"
            ),
        },
        {
            "instruction": "How does supply-chain risk (SR family) show up in an ATO conversation?",
            "output": (
                "The AO may ask where critical software and devices come from, whether you can trust updates, and what you do if a supplier is compromised. That is SR/SA territory, not only RA-5 CVEs.\n\n"
                "If you cannot name your gold-image source or your last firmware vendor, the supply-chain story is weak even if ACAS is clean."
            ),
        },
        {
            "instruction": "What is the ISSO's job during the Assess step besides answering email?",
            "output": (
                "Schedule evidence, make sure the environment the SCA tests is the real production-like one, track requests, and refrain from 'fixing' things mid-test without telling the assessor (that can make the SAR incoherent).\n\n"
                "After the SAR draft, reconcile every fail to a POA&M or a documented dispute. Do not wait for the AO meeting to read the SAR."
            ),
        },
        {
            "instruction": "Why do AOs ask about 'security-relevant' versus 'cosmetic' changes?",
            "output": (
                "Cosmetic changes (banner text, extra read-only dashboard) rarely change residual risk. Security-relevant changes alter attack surface, identity, crypto, data types, or compensating controls.\n\n"
                "The ISSO's job is to classify honestly. Calling a new public API cosmetic is how significant-change processes fail."
            ),
        },
        {
            "instruction": "What is a 'closed but not validated' problem on a POA&M during authorization?",
            "output": (
                "If eMASS says Closed and the SAR or latest scan still fails, the package is inconsistent. Either reopen, or attach the validation the closer claimed existed.\n\n"
                "AOs and assessors look for that mismatch. It is more damaging than an honest Open High with a plan."
            ),
        },
        {
            "instruction": "Explain customer responsibility in FedRAMP to a customer ISSO who thinks the CSP 'has an ATO so we are done.'",
            "output": (
                "The CSP ATO covers the inherited baseline they implement. You still configure identity, your data, your admin users, and any customer-responsibility controls in the matrix.\n\n"
                "Your agency AO still accepts residual risk for your use. Misconfigured tenant MFA is your POA&M, not proof the CSP package was fake."
            ),
        },
        {
            "instruction": "What is the difference between a finding, a weakness, and a vulnerability in POA&M talk?",
            "output": (
                "People mix the words. Practical usage: a vulnerability is often a specific flaw (frequently scanner/CVE-shaped). A weakness is the POA&M's description of what is wrong (could be a missing process). A finding is what an assessor or scanner reported.\n\n"
                "You can have a finding that is a weakness but not a CVE (STIG, SAR documentation fail). Write the weakness so a stranger knows the problem; do not only paste a plugin number."
            ),
        },
        {
            "instruction": "How should a new ISSO use NIST 800-37 versus 800-53 day to day?",
            "output": (
                "800-37 tells you the process and roles (when to categorize, assess, authorize, monitor). 800-53 tells you the control catalog to implement and describe.\n\n"
                "Day to day, ISSOs live in 800-53 statements, scans, and POA&Ms, but they get lost if they do not know which RMF step they are in (for example treating ConMon like a brand-new Select)."
            ),
        },
        {
            "instruction": "What does 'adequate security' mean in FISMA/RMF conversation without pretending it is a score?",
            "output": (
                "It means security commensurate with risk to the agency's mission and data - implemented through the RMF decision, not a marketing badge.\n\n"
                "There is no CountGPT score for adequate security. The AO's authorization is the legal/administrative expression of that judgment for a system."
            ),
        },
        {
            "instruction": "Why might a system have both a DoD ATO and a FedRAMP package mentioned in the SSP?",
            "output": (
                "A DoD application may inherit a FedRAMP-authorized CSP and still need a DoD authorization for the mission system, overlays, and impact level. The SSP inheritance table should list both, with different owners.\n\n"
                "The two packages can have different open POA&Ms. The ISSO tracks which residual risks belong to which AO."
            ),
        },
        {
            "instruction": "What is a 'reauthorization' versus an ongoing ConMon review?",
            "output": (
                "Reauthorization is a fresh AO decision, often because the ATD arrived, the system changed significantly, or the AO wants a new SAR. ConMon reviews are the scheduled in-between updates that may not produce a new ATO letter.\n\n"
                "Organizations differ on how formal each review is. The ISSO should know which meeting can actually change authorization status."
            ),
        },
        {
            "instruction": "Explain 'security categorization memo' versus the SSP introductory chapter.",
            "output": (
                "The categorization memo (or eMASS equivalent) is the signed CIA impact decision that drives baseline selection. The SSP intro retells the system description and often repeats that categorization.\n\n"
                "If they disagree (SSP says Moderate, memo says High), fix it before assessment. Assessors notice."
            ),
        },
        {
            "instruction": "What is the role of legal/counsel in incident reporting versus the ISSO?",
            "output": (
                "The ISSO/SOC handle technical detection and the IR plan. Counsel often decides privilege, external notification nuance, and sometimes whether a privacy event is reportable.\n\n"
                "The ISSO should not delay required cyber reporting while waiting for a perfect legal memo if policy sets a short clock - escalate in parallel. Exact rules are organizational."
            ),
        },
        {
            "instruction": "How do you explain 'compensating control' to an engineer who thinks a WAF means the CVE is gone?",
            "output": (
                "A compensating control reduces likelihood or impact so residual risk may be acceptable for a while. The vulnerability can still be present.\n\n"
                "The POA&M stays Open (or accepted) until the underlying fix, with the compensating control described specifically enough to test. 'We have a WAF' with detect-only mode is usually not compensation."
            ),
        },
        {
            "instruction": "What is a 'package kickoff' in Assess, and what should already be true?",
            "output": (
                "Kickoff is when the SCA and system team agree on scope, schedule, and evidence channels. The SSP should already match production, scan targets should match inventory, and known Highs should already be on the POA&M.\n\n"
                "Kickoff is late to discover the boundary diagram is three years old. That discovery belongs in Prepare/Implement/ConMon."
            ),
        },
        {
            "instruction": "Why is 'the scanner was noisy' a bad AO briefing line by itself?",
            "output": (
                "Scanners are noisy, but AOs need a validated list: confirmed, FP-pending, out-of-scope, vendor-dependent. Noise is a reason to do credentialed scans and triage, not a reason to show zero findings.\n\n"
                "Bring the triage metrics (how many validated Highs) rather than insulting the tool."
            ),
        },
        {
            "instruction": "What does an ISSO hand the AO in a one-page residual-risk summary?",
            "output": (
                "Categorization, authorization dates, count of open High/Moderate/Low, overdue Highs, inherited Highs, last SAR date, last credentialed scan date, and any requested decisions (OR, adjustment, significant change).\n\n"
                "Do not bury the overdue Highs on page 40. Do not invent plugin numbers in the one-pager."
            ),
        },
        {
            "instruction": "How is a 'plan of action and milestones' different from a project plan in Jira?",
            "output": (
                "Jira may implement the work. The POA&M is the authorization-facing record of residual weakness, severity, and official dates the AO and assessors use.\n\n"
                "If Jira is green and eMASS is stale, ConMon failed. If eMASS is green and production is unpatched, honesty failed. Keep them reconciled."
            ),
        },
        {
            "instruction": "What is 'security authorization' versus 'security accreditation' in older DoD language?",
            "output": (
                "Older DoD documents said accreditation; RMF says authorization. People still say both. They mean the official risk decision to allow a system to operate.\n\n"
                "If you are writing a new SSP, use authorization/ATO unless your template still says accreditation. Do not treat them as two different current processes."
            ),
        },
        {
            "instruction": "Explain why 'implemented by policy' is a weak status for a technical control.",
            "output": (
                "Policy can satisfy a -1 control. A technical control like IA-2 or SC-8 needs a mechanism an assessor can test. Policy that says 'we shall use MFA' while the IdP allows password-only is a fail.\n\n"
                "Put the mechanism in the SSP. Put the policy reference in the -1 statement."
            ),
        },
        {
            "instruction": "What is a 'conditional authorization to operate' condition example that is actually testable?",
            "output": (
                "Example: 'Internet-facing VIP may remain only if the High cipher finding is closed by [date] and a credentialed scan is uploaded to eMASS within 7 days after.' That is testable.\n\n"
                "'Team will try harder on security' is not a condition. ISSOs should help the AO write conditions that map to POA&M IDs and dates."
            ),
        },
        {
            "instruction": "How do privacy threshold analyses (PTA) or similar intake docs relate to RMF Select?",
            "output": (
                "Privacy intake decides whether PII is involved and which privacy artifacts and PT controls apply. That outcome should match FIPS 199 information types and the selected privacy overlay.\n\n"
                "If the PTA says no PII and the app collects SSNs, both privacy and categorization are wrong. Fix the intake, do not only add encryption."
            ),
        },
        {
            "instruction": "What is the difference between the ISSO and a Privacy Officer on a system that has both?",
            "output": (
                "The ISSO owns the security authorization artifacts and technical controls. The privacy officer owns privacy program artifacts (notices, minimization, individual rights) and often the PT control narrative.\n\n"
                "They must reconcile: encryption (security) does not legalize extra collection (privacy). One AO package should not tell two stories."
            ),
        },
        {
            "instruction": "When is a 'dev/test' environment inside the authorization boundary?",
            "output": (
                "If it holds production-like data, shares credentials with production, or can reach production data stores, it is usually in or interconnected - not a free pass.\n\n"
                "A fully isolated synthetic-data lab may be out of boundary if the diagram and inventory say so and it cannot jump to prod. Hope is not isolation; network evidence is."
            ),
        },
        {
            "instruction": "What does 'reciprocity review' look like when an agency wants to use another agency's ATO?",
            "output": (
                "The gaining AO (or delegate) reads the package enough to see boundary, overlays, residual risk, and date currency. They document what they leverage and what extra local controls they require.\n\n"
                "Rubber-stamping a five-year-old SAR for a different data type is not a review. Refusing to leverage without reading is also not analysis - but the AO may still require extra assessment."
            ),
        },
        {
            "instruction": "Why do ConMon strategies sample some controls annually and watch others monthly?",
            "output": (
                "Volatility and automation: vulnerability scans and inventory can be monthly. Personnel screening evidence might be sampled less often. Critical volatile controls (boundary, identity, logging) deserve more frequent checks.\n\n"
                "The written CA-7 strategy should say that mix. If everything is 'annual PDF,' you will miss scan Highs that appeared in February."
            ),
        },
        {
            "instruction": "What is an 'authorization official designated representative' in some org charts?",
            "output": (
                "Some AOs designate a representative to run the process, collect briefings, or even sign certain actions per local policy. Whether they can actually grant an ATO is a written delegation question.\n\n"
                "ISSOs should not assume a helpful colonel is the AO. Check the appointment letter."
            ),
        },
        {
            "instruction": "How should an ISSO record a disagreement that the scan repository includes the wrong plugin set for the OS?",
            "output": (
                "That is an RA-5 process finding: the scan is not authoritative until the credentialed plugin set matches the OS. Document it, fix the repository, rescan, then update POA&Ms.\n\n"
                "It is not automatically a false positive on every plugin, and it is not permission to ignore Highs that still look valid on the host."
            ),
        },
        {
            "instruction": "What is 'common control inheritance letter' content, briefly?",
            "output": (
                "It usually names the provider system, the controls offered, the provider authorization date, open provider POA&Ms that affect inheritors, and a point of contact.\n\n"
                "A logo slide that says 'we are secure' is not an inheritance letter."
            ),
        },
        {
            "instruction": "Explain why 'ATO in eMASS' plus 'production not scanned' is a ConMon fail.",
            "output": (
                "Authorization assumes the inventory is assessed. If production hosts are not in the scan job, RA-5 and CM-8 are drifting from the SSP.\n\n"
                "The ISSO should reconcile cloud/AD inventory to scan targets every cycle. New autoscaled nodes are a common hole."
            ),
        },
        {
            "instruction": "What is the teaching difference between IAVM and a STIG and an ACAS plugin?",
            "output": (
                "IAVM-style messages are DoD vulnerability management directives about specific issues and timelines. ACAS plugins detect many of those issues technically. STIGs are configuration guides, not the IAVM list.\n\n"
                "An ISSO may need to track all three. Closing a STIG does not close an IAVM, and a plugin miss does not mean the IAVM does not apply if the software is present."
            ),
        },
        {
            "instruction": "How does an ISSO handle a control that is 'planned' at Assess time?",
            "output": (
                "Planned is not implemented. It should be a POA&M (and possibly a tailoring/OR if the AO will authorize without it). The SAR should not say implemented.\n\n"
                "If the control is required for the baseline and still planned, expect residual risk to be visible to the AO."
            ),
        },
        {
            "instruction": "What is 'security authorization package' versus the living eMASS record after day 1?",
            "output": (
                "The package is the set of artifacts used for the decision (SSP, SAR, POA&M, diagrams, letters). After authorization, eMASS (or equivalent) should stay living: POA&M and SSP updates, new scans.\n\n"
                "A frozen PDF binder that diverges from production is how programs fail the next review. Version the SSP; do not only keep the authorization-day zip."
            ),
        },
    ]
