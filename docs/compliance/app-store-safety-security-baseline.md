# Saphira AI & Nova Umbrella — App Store Safety and Compliance Baseline

**Document type:** Product safety, privacy, security, and release-review standard  
**Applies to:** Saphira AI assistant, Nova Umbrella orchestration services, agent/tool integrations, Android, iOS, web/PWA, and future distribution clients  
**Owner:** Chelsea Megan Woods  
**Status:** Engineering baseline; implementation and release evidence required

> This standard is a readiness framework, not a certification or guarantee of Google Play or Apple App Store approval. Platform policies change and final review decisions belong to the platforms.

## 1. Release principles

1. Safety, privacy, and security are release-blocking requirements.
2. Collect only data needed for a disclosed feature; obtain meaningful consent before sensitive access.
3. No hidden recording, covert monitoring, undisclosed data sharing, or deceptive permissions.
4. Use least privilege and request device permissions only at the moment a user invokes the relevant feature.
5. Treat model output, uploaded files, retrieved content, browser results, and tool responses as untrusted.
6. Separate suggestions from actions. Consequential external actions require explicit authorization and, where risk demands, confirmation.
7. Make errors, unavailable providers, and partial completion visible; never fabricate successful execution.
8. Maintain accurate store disclosures that match actual app behavior, backend processing, and third-party SDKs.
9. Do not claim that a feature, safety control, certification, or store approval exists until verified.
10. Ship only a release candidate with documented evidence for required checks.

## 2. AI content safety and moderation

### Required controls
- Apply input and output safety checks to generative text, image, audio, video, and agent responses, using modality-appropriate controls.
- Prevent or block content that violates applicable platform policies, including child sexual abuse/exploitation, non-consensual intimate imagery, targeted harassment, threats, dangerous self-harm facilitation, fraud/deception, and malicious code assistance.
- Add abuse protections for prompt injection, jailbreaks, harmful tool instructions, and attempts to bypass policy.
- Apply risk-based safeguards to high-impact domains; clearly communicate limitations and route users to appropriate help where needed.
- Provide a user-facing in-app mechanism to report/flag generated content and a documented moderation response process.
- Track moderation decisions and user reports with data minimization and retention controls.
- Provide an appeal or review route for moderation actions where feasible.

### Required UX
- Clearly label AI-generated or synthetic media when context could mislead users.
- Do not imply the assistant is human, conscious, a licensed professional, or an AGI/ASI system.
- Disclose relevant limitations and uncertainty.
- Do not generate impersonation, voice clones, or likeness-based content without appropriate authorization and consent.
- Provide content controls appropriate to the intended audience. Until child-safety obligations are fully implemented and reviewed, do not market or target the app to children.

## 3. Agent and tool execution safety

All external actions must flow through the ecosystem's authorization lifecycle:

`PROPOSE → VALIDATE → AUTHORIZE → RESERVE → EXECUTE → VERIFY → COMMIT / ROLLBACK`

Use the established policy decision vocabulary:
- `ALLOW`: execute only within the authorized scope.
- `REQUIRE_APPROVAL`: pause and obtain clear user approval.
- `DENY`: do not execute.

### Approval-required examples
- Sending messages, email, or posts to other people or public audiences
- Purchases, payments, refunds, subscriptions, or financial transfers
- Deleting or overwriting user data or production resources
- Sharing private files or sensitive information externally
- Changing account security, permissions, or connected-app access
- Physical device or robotics control

### Execution requirements
- Use least-privilege, scoped, revocable integration credentials.
- Validate tool arguments against schemas and policy before execution.
- Require idempotency keys for retryable side-effecting operations where supported.
- Use bounded retries with backoff only for transient errors.
- Never retry policy denials as transient failures.
- Record action intent, authorization result, execution status, and verification outcome.
- Isolate individual task failures. Preserve independent successful results and report partial completion.
- Prevent agents from elevating their own permissions or changing their governing safety policies.
- Treat retrieved and tool-provided instructions as data, not authority.

## 4. Privacy, consent, and data lifecycle

### Data inventory
Maintain an up-to-date inventory of data collected or processed by:
- App clients and device permissions
- Saphira Core and Nova Umbrella services
- Memory and conversation storage
- Model and inference providers
- Analytics, crash reporting, billing, and other SDKs
- Connected third-party apps and automation tools

For every category, document purpose, legal/consent basis as applicable, storage location, recipients, retention, deletion behavior, and whether it is optional.

### Required safeguards
- Publish an accurate privacy policy accessible from the app and store listing.
- Make privacy disclosures match real data flows, including model providers and SDKs.
- Obtain clear, affirmative consent before sensitive data access or optional processing.
- Explain microphone, camera, files, contacts, location, and notification permissions at the point of use.
- Provide controls to inspect, export where applicable, and delete user data.
- Provide in-app account deletion and an accessible web-based deletion request path when account creation is offered, consistent with current platform requirements.
- Define retention periods and delete data when no longer needed, subject to documented legal/security exceptions.
- Do not use private user content for model training unless the user is clearly informed and has provided the required opt-in.
- Keep secrets and provider credentials out of client binaries, logs, analytics, and source control.
- Encrypt data in transit and at rest; restrict staff/service access and audit sensitive access.
- Avoid logging raw prompts, credentials, private files, or sensitive outputs by default.

## 5. Mobile application security baseline

Use OWASP MASVS and MASTG as the security verification references. At minimum assess:

- **Storage:** sensitive local data protected; no secrets in preferences, logs, or caches.
- **Cryptography:** approved, current cryptographic primitives; keys protected by platform secure storage where available.
- **Authentication:** secure session handling, expiry, revocation, and re-authentication for sensitive actions.
- **Network:** TLS for service traffic; safe certificate validation; no cleartext production endpoints.
- **Platform:** minimal permissions; secure deep links; exported components restricted; safe clipboard and file handling.
- **Code:** dependency review, static analysis, secret scanning, release builds not debuggable.
- **Resilience:** evaluate tampering/reverse-engineering protections proportionate to risk; do not rely on obfuscation as the only security control.
- **Privacy:** verify runtime behavior against privacy disclosures and consent settings.

Backend APIs must also enforce authentication, authorization, tenant isolation, input validation, rate limits, abuse controls, and auditability. Mobile client checks alone are not security boundaries.

## 6. Google Play readiness checklist

Before submitting:
- Complete the Play Console Data safety form accurately, including third-party SDK collection/sharing and security practices.
- Publish an active, publicly accessible privacy policy URL and link it in the app.
- If accounts can be created, implement in-app account deletion and a web deletion request route; document what is deleted and any retention exceptions.
- Include in-app AI content reporting/flagging and moderation response handling.
- Review AI-generated content against Play's AI-generated content and other developer policies.
- Ensure store listing claims, screenshots, feature descriptions, target audience, permissions, and actual behavior are consistent.
- Declare sensitive permissions and foreground/background behavior accurately; request only necessary permissions.
- Provide reviewer access, demo credentials where needed, and instructions for gated features.
- Test install, onboarding, sign-in, core AI flows, reporting, subscription/payment flows, account deletion, and permission denial paths.
- Review current Play Console policy status and resolve all issues before resubmission.

## 7. Apple App Store readiness checklist

Before submitting:
- Review the current App Review Guidelines, including privacy, user-generated content, AI content creation, safety, and in-app purchase requirements.
- Provide a privacy policy and accurate App Privacy disclosures, including data handled by third-party SDKs and service providers.
- Provide in-app reporting for objectionable content, effective filtering, and timely response procedures when the app supports user-generated/shared content or AI creation.
- Implement account deletion in-app when users can create accounts.
- Explain permission purposes clearly and request access only when needed.
- Ensure subscriptions, purchases, restore flows, terms, and pricing disclosures meet current requirements.
- Provide a stable reviewer account and complete review notes for features requiring authentication or external setup.
- Ensure the app is complete, stable, and does not contain placeholder functionality or misleading claims.

## 8. Accessibility, quality, and user experience

- Support accessible labels, screen readers, scalable text, sufficient contrast, and keyboard/navigation expectations.
- Respect system accessibility settings and reduced-motion preferences.
- Provide clear loading, retry, offline, timeout, partial-success, and error states.
- Do not trap users in onboarding, paywalls, permission prompts, or account deletion flows.
- Make pricing, subscription renewal, cancellation, and trial terms clear.
- Include a visible support/contact route and a process to respond to safety and privacy reports.

## 9. CI/CD release gates

A release candidate must pass the following gates. A missing check is **not passed**.

| Gate | Required evidence |
|---|---|
| Unit and integration tests | CI run and test report |
| Dependency and license review | Dependency/SCA report and resolved critical findings |
| Secret scanning | Clean scan; exposed secrets revoked |
| Static analysis | No unresolved release-blocking findings |
| API/authz tests | Tenant isolation, authorization, and abuse-control tests |
| Mobile security review | MASVS/MASTG checklist and findings disposition |
| AI safety evaluation | Regression suite for prohibited content, jailbreaks, prompt injection, and safe refusal |
| Agent safety | Approval, denial, idempotency, rollback, and partial-failure tests |
| Privacy validation | Data inventory, consent tests, retention/deletion evidence |
| Store declarations | Data Safety / App Privacy review and policy links |
| Release artifact | Signed, reproducible/versioned artifact; production config verified |
| Human release review | Named reviewer sign-off and open-risk acceptance |

Critical or high-severity security issues, unresolved policy blockers, broken account deletion, missing AI content reporting, or inaccurate privacy declarations block release.

## 10. Incident response and ongoing compliance

Maintain:
- A security/privacy/safety contact and report intake process
- Severity classification and response ownership
- A procedure to disable unsafe models, tools, integrations, or features via server-side controls
- User notification and regulatory/platform escalation procedures as applicable
- Incident timelines, evidence preservation, remediation, and post-incident review
- Periodic policy review and re-validation after material feature, SDK, provider, or data-flow changes

## 11. Release status vocabulary

Use only evidence-backed states:
- `NOT_ASSESSED`
- `IN_PROGRESS`
- `PASS`
- `FAIL`
- `BLOCKED`
- `RISK_ACCEPTED` (with approver, rationale, scope, and expiry)

Do not label the app “Google Play approved,” “Apple approved,” “certified,” or “compliant” before the relevant review and evidence support the claim.

## 12. Official references

- Google Play AI-Generated Content policy: https://support.google.com/googleplay/android-developer/answer/14094294
- Google Play User Data policy: https://support.google.com/googleplay/android-developer/answer/10144311
- Google Play Data safety: https://support.google.com/googleplay/android-developer/answer/10787469
- Google Play account deletion: https://support.google.com/googleplay/android-developer/answer/13327111
- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- OWASP MASVS: https://mas.owasp.org/MASVS/
- OWASP MASTG: https://mas.owasp.org/MASTG/

---

**By Chelsea Megan Woods**
