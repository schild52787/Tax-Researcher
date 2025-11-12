"""
OECD Scraper

Scrape OECD.org for public tax guidance - completely free, no API required.
Accesses Model Tax Convention, Pillar Two guidance, BEPS materials.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re


class OECDScraper:
    """Scrape OECD.org for public tax guidance"""

    BASE_URL = "https://www.oecd.org"
    TAX_BASE = "https://www.oecd.org/tax"
    BEPS_BASE = "https://www.oecd.org/tax/beps"

    def __init__(self, timeout: int = 10):
        """
        Initialize OECD scraper

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Cargill Tax Research Tool (Compliance Research)'
        })

    def search_pillar_two(self, keyword: str) -> List[Dict]:
        """
        Search OECD Pillar Two guidance

        Args:
            keyword: Search term (e.g., "GloBE", "ETR", "IIR")

        Returns:
            List of relevant documents
        """
        search_url = f"{self.TAX_BASE}/beps/pillar-two-model-rules.htm"

        try:
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            results = []

            # Find all links related to keyword
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                href = link['href']

                if keyword.lower() in link_text.lower():
                    if href.startswith('/'):
                        href = self.BASE_URL + href

                    results.append({
                        'title': link_text,
                        'url': href,
                        'type': 'Pillar Two',
                        'keyword': keyword
                    })

            return results

        except requests.RequestException as e:
            return [{'error': str(e), 'url': search_url}]

    def get_model_convention_info(self, article: Optional[int] = None) -> Dict:
        """
        Get OECD Model Tax Convention information

        Args:
            article: Specific article number (optional)

        Returns:
            Dict with model convention info
        """
        url = f"{self.TAX_BASE}/treaties/model-tax-convention-on-income-and-on-capital-condensed-version-20745419.htm"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            return {
                'title': 'OECD Model Tax Convention on Income and on Capital',
                'url': url,
                'article': article,
                'status': 'accessible',
                'note': 'Full text available at OECD.org'
            }

        except requests.RequestException as e:
            return {
                'error': str(e),
                'url': url,
                'article': article
            }

    def search_beps_action(self, action_number: int) -> Dict:
        """
        Search for BEPS Action Plan documents

        Args:
            action_number: BEPS Action number (1-15)

        Returns:
            Dict with BEPS action info
        """
        search_url = f"{self.BEPS_BASE}/beps-actions/action{action_number}"

        try:
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.get_text(strip=True) if title_elem else f"BEPS Action {action_number}"

            # Find PDF documents
            documents = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.pdf' in href.lower():
                    if href.startswith('/'):
                        href = self.BASE_URL + href
                    documents.append({
                        'title': link.get_text(strip=True),
                        'url': href,
                        'type': 'PDF'
                    })

            return {
                'action': action_number,
                'title': title,
                'url': search_url,
                'documents': documents
            }

        except requests.RequestException as e:
            return {
                'error': str(e),
                'action': action_number,
                'url': search_url
            }

    def search_transfer_pricing(self, keyword: str) -> List[Dict]:
        """
        Search OECD transfer pricing guidance

        Args:
            keyword: Search term

        Returns:
            List of relevant documents
        """
        search_url = f"{self.TAX_BASE}/transfer-pricing"

        try:
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            results = []

            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                href = link['href']

                if keyword.lower() in link_text.lower():
                    if href.startswith('/'):
                        href = self.BASE_URL + href

                    results.append({
                        'title': link_text,
                        'url': href,
                        'type': 'Transfer Pricing',
                        'keyword': keyword
                    })

            return results

        except requests.RequestException as e:
            return [{'error': str(e), 'url': search_url}]

    def get_administrative_guidance(self, topic: str = "pillar-two") -> Dict:
        """
        Get latest OECD administrative guidance

        Args:
            topic: Topic area (default: pillar-two)

        Returns:
            Dict with guidance information
        """
        # This would need to be updated as new guidance is published
        guidance_urls = {
            'pillar-two': f"{self.TAX_BASE}/beps/pillar-two-model-rules.htm",
            'globe': f"{self.TAX_BASE}/beps/pillar-two-model-rules.htm",
            'amount-a': f"{self.TAX_BASE}/beps/pillar-one-amount-a.htm",
        }

        url = guidance_urls.get(topic.lower(), f"{self.TAX_BASE}/beps")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find PDF documents (usually the actual guidance)
            documents = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '.pdf' in href.lower():
                    if href.startswith('/'):
                        href = self.BASE_URL + href
                    documents.append({
                        'title': link.get_text(strip=True),
                        'url': href,
                        'type': 'PDF'
                    })

            return {
                'topic': topic,
                'url': url,
                'documents': documents[:10],  # Top 10
                'status': 'accessible'
            }

        except requests.RequestException as e:
            return {
                'error': str(e),
                'topic': topic,
                'url': url
            }

    def verify_citation_exists(self, citation: str) -> Dict:
        """
        Verify an OECD citation exists

        Args:
            citation: OECD citation text

        Returns:
            Dict with verification status
        """
        # Extract key terms from citation
        if 'Model' in citation and 'Convention' in citation:
            return self.get_model_convention_info()

        elif 'Pillar Two' in citation or 'GloBE' in citation:
            results = self.search_pillar_two('GloBE')
            return {
                'valid': len(results) > 0,
                'citation': citation,
                'results': results
            }

        elif 'BEPS' in citation:
            # Try to extract action number
            match = re.search(r'Action\s+(\d+)', citation)
            if match:
                action = int(match.group(1))
                return self.search_beps_action(action)

        # General search
        return {
            'valid': None,
            'citation': citation,
            'note': 'Manual verification recommended'
        }

    def rate_limit_delay(self):
        """Polite delay between requests"""
        time.sleep(0.5)  # 500ms delay
