"""Tests for web scrapers"""

import pytest
from src.scrapers.irs_scraper import IRSScraper
from src.scrapers.oecd_scraper import OECDScraper


class TestIRSScraper:
    """Test IRS scraper"""

    @pytest.mark.skip(reason="Requires network access")
    def test_search_irb(self):
        """Test IRB search"""
        scraper = IRSScraper()
        results = scraper.search_irb(2020, "951A")

        assert isinstance(results, list)
        # May or may not find results depending on IRS site

    @pytest.mark.skip(reason="Requires network access")
    def test_verify_notice(self):
        """Test notice verification"""
        scraper = IRSScraper()
        result = scraper.verify_notice_exists("2020-69")

        assert isinstance(result, dict)
        assert 'valid' in result

    def test_guidance_type_detection(self):
        """Test guidance type detection"""
        scraper = IRSScraper()

        assert scraper._detect_guidance_type("Notice 2020-69") == "Notice"
        assert scraper._detect_guidance_type("Revenue Ruling 2019-01") == "Revenue Ruling"
        assert scraper._detect_guidance_type("Revenue Procedure 2020-01") == "Revenue Procedure"


class TestOECDScraper:
    """Test OECD scraper"""

    @pytest.mark.skip(reason="Requires network access")
    def test_search_pillar_two(self):
        """Test Pillar Two search"""
        scraper = OECDScraper()
        results = scraper.search_pillar_two("GloBE")

        assert isinstance(results, list)

    @pytest.mark.skip(reason="Requires network access")
    def test_get_model_convention(self):
        """Test model convention access"""
        scraper = OECDScraper()
        result = scraper.get_model_convention_info(5)

        assert isinstance(result, dict)
        assert 'url' in result


# Integration tests (these are skipped by default as they require network)

@pytest.mark.skip(reason="Integration test - requires network")
def test_irs_integration():
    """Integration test for IRS scraper"""
    scraper = IRSScraper()

    # Test searching for a well-known notice
    result = scraper.verify_notice_exists("2020-69")
    assert result['valid'] or 'error' in result  # Should either work or have error


@pytest.mark.skip(reason="Integration test - requires network")
def test_oecd_integration():
    """Integration test for OECD scraper"""
    scraper = OECDScraper()

    # Test accessing model convention
    result = scraper.get_model_convention_info()
    assert 'url' in result
