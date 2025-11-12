"""
IRS Scraper

Scrape IRS.gov for public tax guidance - completely free, no API required.
Accesses Internal Revenue Bulletins, Notices, Revenue Rulings, regulations.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re


class IRSScraper:
    """Scrape IRS.gov for public guidance"""

    BASE_URL = "https://www.irs.gov"
    IRB_BASE = "https://www.irs.gov/irb"

    def __init__(self, timeout: int = 10):
        """
        Initialize IRS scraper

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Cargill Tax Research Tool (Compliance Research)'
        })

    def search_irb(self, year: int, search_term: str) -> List[Dict]:
        """
        Search Internal Revenue Bulletins for a specific year

        Args:
            year: Tax year (e.g., 2020)
            search_term: Search term (e.g., "951A", "Subpart F")

        Returns:
            List of matching IRB items with URLs
        """
        url = f"{self.IRB_BASE}/{year}"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            results = []

            # Find all links in the IRB index
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                href = link['href']

                # Check if search term is in the link text
                if search_term.lower() in link_text.lower():
                    # Make URL absolute
                    if href.startswith('/'):
                        href = self.BASE_URL + href

                    results.append({
                        'title': link_text,
                        'url': href,
                        'year': year,
                        'type': self._detect_guidance_type(link_text)
                    })

            return results

        except requests.RequestException as e:
            return [{'error': str(e), 'url': url}]

    def verify_notice_exists(self, notice_number: str) -> Dict:
        """
        Verify a Notice citation exists

        Args:
            notice_number: Notice number (e.g., "2020-69")

        Returns:
            Dict with verification status and URL if found
        """
        # Extract year from notice number
        match = re.match(r'(\d{4})-(\d+)', notice_number)
        if not match:
            return {'valid': False, 'error': 'Invalid notice number format'}

        year = match.group(1)
        search_url = f"{self.BASE_URL}/pub/irs-drop/n-{notice_number.replace('-', '')}.pdf"

        try:
            response = self.session.head(search_url, timeout=self.timeout)

            if response.status_code == 200:
                return {
                    'valid': True,
                    'notice': notice_number,
                    'url': search_url,
                    'type': 'Notice'
                }
            else:
                # Try searching IRB index
                irb_results = self.search_irb(int(year), f"Notice {notice_number}")
                if irb_results and 'error' not in irb_results[0]:
                    return {
                        'valid': True,
                        'notice': notice_number,
                        'url': irb_results[0]['url'],
                        'type': 'Notice',
                        'source': 'IRB'
                    }

                return {'valid': False, 'notice': notice_number}

        except requests.RequestException as e:
            return {'valid': False, 'error': str(e)}

    def verify_revenue_ruling(self, rev_rul_number: str) -> Dict:
        """
        Verify a Revenue Ruling exists

        Args:
            rev_rul_number: Rev. Rul. number (e.g., "2019-01")

        Returns:
            Dict with verification status and URL if found
        """
        match = re.match(r'(\d{4})-(\d+)', rev_rul_number)
        if not match:
            return {'valid': False, 'error': 'Invalid revenue ruling format'}

        year = match.group(1)

        # Try direct PDF link
        search_url = f"{self.BASE_URL}/pub/irs-drop/rr-{rev_rul_number.replace('-', '')}.pdf"

        try:
            response = self.session.head(search_url, timeout=self.timeout)

            if response.status_code == 200:
                return {
                    'valid': True,
                    'ruling': rev_rul_number,
                    'url': search_url,
                    'type': 'Revenue Ruling'
                }
            else:
                # Try IRB search
                irb_results = self.search_irb(int(year), f"Rev. Rul. {rev_rul_number}")
                if irb_results and 'error' not in irb_results[0]:
                    return {
                        'valid': True,
                        'ruling': rev_rul_number,
                        'url': irb_results[0]['url'],
                        'type': 'Revenue Ruling',
                        'source': 'IRB'
                    }

                return {'valid': False, 'ruling': rev_rul_number}

        except requests.RequestException as e:
            return {'valid': False, 'error': str(e)}

    def search_code_section(self, section: str) -> Dict:
        """
        Search for IRC section information

        Args:
            section: IRC section (e.g., "951A")

        Returns:
            Dict with search results and links
        """
        search_url = f"{self.BASE_URL}/search"
        params = {
            'q': f"IRC section {section}",
            'scope': 'tax'
        }

        try:
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            results = []
            # Parse search results
            for result_div in soup.find_all('div', class_='result')[:5]:  # Top 5 results
                title_elem = result_div.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')

                    if url.startswith('/'):
                        url = self.BASE_URL + url

                    results.append({
                        'title': title,
                        'url': url,
                        'section': section
                    })

            return {
                'section': section,
                'results': results,
                'search_url': f"{search_url}?q=IRC+section+{section}"
            }

        except requests.RequestException as e:
            return {'error': str(e), 'section': section}

    def get_regulation_info(self, reg_section: str) -> Dict:
        """
        Get information about a Treasury Regulation

        Args:
            reg_section: Regulation section (e.g., "1.951A-2")

        Returns:
            Dict with regulation info and links
        """
        # Search for regulation
        search_url = f"{self.BASE_URL}/search"
        params = {
            'q': f"Treasury Regulation {reg_section}",
            'scope': 'tax'
        }

        try:
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            results = []
            for result_div in soup.find_all('div', class_='result')[:3]:
                title_elem = result_div.find('a')
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': self.BASE_URL + title_elem.get('href', '') if title_elem.get('href', '').startswith('/') else title_elem.get('href', '')
                    })

            return {
                'regulation': reg_section,
                'results': results,
                'search_url': f"{search_url}?q=Treasury+Regulation+{reg_section}"
            }

        except requests.RequestException as e:
            return {'error': str(e), 'regulation': reg_section}

    def _detect_guidance_type(self, text: str) -> str:
        """Detect type of IRS guidance from text"""
        text_lower = text.lower()

        if 'notice' in text_lower:
            return 'Notice'
        elif 'revenue ruling' in text_lower or 'rev. rul.' in text_lower:
            return 'Revenue Ruling'
        elif 'revenue procedure' in text_lower or 'rev. proc.' in text_lower:
            return 'Revenue Procedure'
        elif 'announcement' in text_lower:
            return 'Announcement'
        elif 'private letter ruling' in text_lower or 'plr' in text_lower:
            return 'Private Letter Ruling'
        elif 'chief counsel advice' in text_lower or 'cca' in text_lower:
            return 'Chief Counsel Advice'
        else:
            return 'Other'

    def rate_limit_delay(self):
        """Polite delay between requests"""
        time.sleep(0.5)  # 500ms delay
