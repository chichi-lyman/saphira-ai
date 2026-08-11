"""Tampa Bay roofing prospect profiling and approval-queue generation.

The pipeline performs lightweight public-site analysis and produces a human-review
queue. It never sends outbound messages and does not harvest restricted personal data.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

from src.tools.free_scraper import Lead, fetch_public_html


@dataclass
class ProspectProfile:
    company_name: str
    city: str
    state: str
    website: str
    business_phone: str
    source_url: str
    source_name: str
    discovered_at: str
    website_status: str
    booking_available: bool
    contact_form_available: bool
    lead_capture_quality: str
    seo_observations: str
    detected_pain_point: str
    pain_evidence: str
    icp_score: int
    recommended_service: str
    personalized_outreach: str
    approval_status: str = "PENDING_REVIEW"
    approved_at: str = ""
    outreach_status: str = "NOT_SENT"
    response_status: str = "NOT_CONTACTED"
    appointment_status: str = "NOT_BOOKED"
    customer_status: str = "PROSPECT"


def _links(html_text: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r'href=[\"\']([^\"\']+)', html_text, re.I)]


def profile_lead(lead: Lead, *, timeout: int = 8) -> ProspectProfile:
    if not lead.website:
        return _profile_without_site(lead)

    try:
        html = fetch_public_html(lead.website, timeout=timeout)
        status = "reachable"
    except RuntimeError as exc:
        return _profile_without_site(lead, status=f"unreachable: {exc}")

    lower = html.lower()
    links = [urljoin(lead.website, href) for href in _links(html)]
    booking_terms = ("book", "schedule", "appointment", "estimate", "calendly", "booking")
    contact_terms = ("contact", "quote", "estimate", "form")
    booking = any(any(term in link.lower() for term in booking_terms) for link in links)
    contact = "<form" in lower or any(any(term in link.lower() for term in contact_terms) for link in links)

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = " ".join((title_match.group(1) if title_match else "").split())
    observations = []
    if not title:
        observations.append("Missing or unreadable homepage title")
    if not booking:
        observations.append("No obvious online booking/scheduling path found")
    if not contact:
        observations.append("No obvious contact/quote form found")
    if not observations:
        observations.append("Homepage exposes basic contact/lead-capture paths")

    pain = "No obvious booking or scheduling path found" if not booking else "Lead-capture path could be evaluated for follow-up automation"
    score = 6
    if lead.website:
        score += 1
    if not booking:
        score += 1
    if not contact:
        score += 1
    if title:
        score += 1
    score = min(score, 10)

    pitch = (
        f"Hi {lead.business_name} team — I was reviewing your public web presence and noticed "
        f"{pain.lower()}. I build AI lead-generation and follow-up systems for service businesses "
        f"that want more consistent handling of inbound opportunities. If improving lead capture "
        f"and follow-up is a priority, I can show you a simple $500/month system tailored to your workflow."
    )

    return ProspectProfile(
        company_name=lead.business_name,
        city=lead.city,
        state=lead.state,
        website=lead.website,
        business_phone=lead.business_phone,
        source_url=lead.source_url,
        source_name=lead.source_name,
        discovered_at=lead.discovered_at,
        website_status=status,
        booking_available=booking,
        contact_form_available=contact,
        lead_capture_quality="good" if booking and contact else "needs_review",
        seo_observations="; ".join(observations),
        detected_pain_point=pain,
        pain_evidence="Observed from publicly accessible homepage/link structure.",
        icp_score=score,
        recommended_service="$500/mo AI B2B Lead Generation System",
        personalized_outreach=pitch,
    )


def _profile_without_site(lead: Lead, status: str = "no_public_website") -> ProspectProfile:
    return ProspectProfile(
        company_name=lead.business_name, city=lead.city, state=lead.state,
        website=lead.website, business_phone=lead.business_phone,
        source_url=lead.source_url, source_name=lead.source_name,
        discovered_at=lead.discovered_at, website_status=status,
        booking_available=False, contact_form_available=False,
        lead_capture_quality="needs_review",
        seo_observations="Website unavailable for automated public-footprint review.",
        detected_pain_point="Public website unavailable for review",
        pain_evidence="No website evidence available; manual review required.",
        icp_score=4,
        recommended_service="$500/mo AI B2B Lead Generation System",
        personalized_outreach=(
            f"Hi {lead.business_name} team — I work with service businesses on AI-powered lead "
            "capture and follow-up. I'd be happy to show you a simple system built around your sales process."
        ),
    )


def write_approval_queue(profiles: list[ProspectProfile], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(ProspectProfile.__dataclass_fields__.keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(asdict(p) for p in profiles)
    return path


def write_summary(profiles: list[ProspectProfile], output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    ranked = sorted(profiles, key=lambda p: p.icp_score, reverse=True)
    lines = [
        "# Saphira — Tampa Bay Roofing Approval Queue",
        "",
        f"Prospects profiled: {len(profiles)}",
        f"Priority prospects (ICP >= 7): {sum(p.icp_score >= 7 for p in profiles)}",
        "",
        "## Priority Prospects",
        "",
    ]
    for p in ranked[:20]:
        lines.extend([
            f"### {p.company_name} — {p.city}, {p.state} — ICP {p.icp_score}/10",
            f"- Pain: {p.detected_pain_point}",
            f"- Evidence: {p.pain_evidence}",
            f"- Website: {p.website or 'N/A'}",
            f"- Approval: {p.approval_status}",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


if __name__ == "__main__":
    print("Pipeline module ready. Feed normalized Lead records into profile_lead().")
