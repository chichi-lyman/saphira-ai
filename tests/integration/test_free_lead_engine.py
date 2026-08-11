from pathlib import Path

from src.integrations.p0_adapters import SalesSwarmAdapter
from src.tools.free_scraper import Lead, normalize_leads, parse_fixture_html, write_csv


FIXTURE = """
<html><body>
<article class="business-card">
  <a class="business-name"> Gulf Roof Co. </a>
  <span class="business-phone"> (813) 555-0101 </span>
  <a class="business-website" href="https://gulfroof.example/">Website</a>
</article>
<article class="business-card">
  <a class="business-name"> Bay Roofing Group </a>
  <span class="business-phone">813-555-0102</span>
  <a class="business-website" href="https://bayroof.example/">Website</a>
</article>
<article class="business-card">
  <a class="business-name"> Gulf Roof Co. </a>
  <span class="business-phone">813-555-0101</span>
  <a class="business-website" href="https://gulfroof.example/">Website</a>
</article>
</body></html>
"""


def test_parse_and_deduplicate_fixture():
    leads = parse_fixture_html(
        FIXTURE,
        source_url="https://example.test/results",
        source_name="fixture",
        industry="Roofing Contractors",
        city="Tampa Bay",
        state="FL",
    )
    assert len(leads) == 2
    assert leads[0].business_name == "Gulf Roof Co."
    assert leads[0].website == "https://gulfroof.example/"


def test_sales_swarm_discovery_contract():
    result = SalesSwarmAdapter().discover_fixture_leads(
        FIXTURE,
        source_url="https://example.test/results",
        source_name="fixture",
        industry="Roofing Contractors",
        city="Tampa Bay",
        state="FL",
        max_leads=1,
    )
    assert len(result) == 1
    assert result[0]["industry"] == "Roofing Contractors"
    assert result[0]["source_name"] == "fixture"


def test_normalize_leads_removes_duplicate_records():
    leads = normalize_leads(
        [
            Lead("Same Co", website="https://same.example", city="Tampa", state="FL"),
            Lead("Same Co", website="https://same.example", city="Tampa", state="FL"),
        ]
    )
    assert len(leads) == 1


def test_write_csv(tmp_path: Path):
    destination = write_csv([Lead("Test Co", industry="Roofing Contractors")], tmp_path / "leads.csv")
    text = destination.read_text(encoding="utf-8")
    assert "business_name" in text
    assert "Test Co" in text
