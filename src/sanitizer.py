"""
Fact Sanitizer

Automatically redact confidential information from tax research facts
before processing with AI or including in memos. Uses pattern matching
and regex - no external APIs required.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class RedactionReport:
    """Report of what was redacted"""
    entities_redacted: int = 0
    people_redacted: int = 0
    amounts_redacted: int = 0
    emails_redacted: int = 0
    dates_redacted: int = 0
    total_redactions: int = 0
    details: List[str] = field(default_factory=list)


class FactSanitizer:
    """Sanitize confidential information from text"""

    def __init__(self, preserve_structure: bool = True):
        """
        Initialize sanitizer

        Args:
            preserve_structure: If True, use placeholder labels instead of [REDACTED]
        """
        self.preserve_structure = preserve_structure
        self.entity_counter = 0
        self.person_counter = 0
        self.entity_map: Dict[str, str] = {}
        self.person_map: Dict[str, str] = {}
        self.report = RedactionReport()

    def sanitize_text(self, text: str) -> str:
        """
        Apply all sanitization rules

        Args:
            text: Original text with confidential information

        Returns:
            Sanitized text safe for AI processing
        """
        # Order matters - do entities first, then people, then other data
        text = self.sanitize_entities(text)
        text = self.sanitize_people(text)
        text = self.sanitize_emails(text)
        text = self.sanitize_amounts(text)
        text = self.sanitize_specific_dates(text)

        return text

    def sanitize_entities(self, text: str) -> str:
        """Replace company/entity names with placeholders"""

        # Pattern for legal entities
        patterns = [
            # LLC, Inc, Corp, Ltd variants
            r'\b([A-Z][a-zA-Z&\'\-]+(?:\s+[A-Z][a-zA-Z&\'\-]+)*)\s+(?:LLC|L\.L\.C\.|Inc\.|Incorporated|Corp\.|Corporation|Ltd\.|Limited|LLP|L\.P\.|LP)',
            # GmbH, AG, SA, BV (international entities)
            r'\b([A-Z][a-zA-Z&\'\-]+(?:\s+[A-Z][a-zA-Z&\'\-]+)*)\s+(?:GmbH|AG|SA|SAS|BV|NV|AB|SpA|Oy)',
        ]

        def replace_entity(match):
            entity = match.group(0)

            # Don't redact "Cargill" itself in general references
            if entity.startswith('Cargill'):
                # But do redact specific Cargill entities
                if entity not in self.entity_map:
                    self.entity_counter += 1
                    letter = chr(64 + self.entity_counter) if self.entity_counter <= 26 else str(self.entity_counter)
                    self.entity_map[entity] = f"[Cargill Entity {letter}]"
                    self.report.details.append(f"Entity: {entity} → {self.entity_map[entity]}")
                    self.report.entities_redacted += 1
                    self.report.total_redactions += 1
                return self.entity_map[entity]

            # Redact other entities
            if entity not in self.entity_map:
                self.entity_counter += 1
                letter = chr(64 + self.entity_counter) if self.entity_counter <= 26 else str(self.entity_counter)
                self.entity_map[entity] = f"[Third Party Entity {letter}]"
                self.report.details.append(f"Entity: {entity} → {self.entity_map[entity]}")
                self.report.entities_redacted += 1
                self.report.total_redactions += 1

            return self.entity_map[entity]

        for pattern in patterns:
            text = re.sub(pattern, replace_entity, text)

        return text

    def sanitize_people(self, text: str) -> str:
        """Replace personal names with role placeholders"""

        # Look for patterns like "John Smith, CFO" or "Jane Doe (Manager)"
        title_patterns = [
            (r'\b([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(CFO|CEO|President|VP|Vice President)', r'[\2]'),
            (r'\b([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+(Manager|Director|Controller|Treasurer)', r'[\2]'),
            (r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+\((CFO|CEO|Manager|Director|VP)\)', r'[\2]'),
        ]

        for pattern, replacement in title_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    name = match[0]
                    if name not in self.person_map:
                        role = match[1] if len(match) > 1 else 'Person'
                        self.person_map[name] = f'[{role}]'
                        self.report.details.append(f"Person: {name} → [{role}]")
                        self.report.people_redacted += 1
                        self.report.total_redactions += 1

            text = re.sub(pattern, replacement, text)

        # Catch remaining capitalized names (heuristic - may have false positives)
        # Only in specific contexts to avoid over-redacting
        name_contexts = [
            r'(?:signed by|prepared by|reviewed by|contact)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]

        for pattern in name_contexts:
            def replace_name(match):
                name = match.group(1)
                if name not in self.person_map:
                    self.person_counter += 1
                    self.person_map[name] = f'[Person {self.person_counter}]'
                    self.report.details.append(f"Person: {name} → [Person {self.person_counter}]")
                    self.report.people_redacted += 1
                    self.report.total_redactions += 1
                return match.group(0).replace(name, self.person_map[name])

            text = re.sub(pattern, replace_name, text, flags=re.IGNORECASE)

        return text

    def sanitize_amounts(self, text: str) -> str:
        """Redact or round dollar amounts"""

        # Match currency amounts
        amount_pattern = r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|USD|EUR|GBP))?'

        def replace_amount(match):
            self.report.amounts_redacted += 1
            self.report.total_redactions += 1
            amount = match.group(0)
            self.report.details.append(f"Amount redacted: {amount}")

            if self.preserve_structure:
                return "[Amount]"
            else:
                return "[REDACTED]"

        text = re.sub(amount_pattern, replace_amount, text, flags=re.IGNORECASE)

        # Also catch written amounts
        written_pattern = r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|hundred|thousand|million|billion)\s+(?:hundred|thousand|million|billion)?\s*dollars?\b'
        text = re.sub(written_pattern, '[Amount]', text, flags=re.IGNORECASE)

        return text

    def sanitize_emails(self, text: str) -> str:
        """Remove email addresses"""

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        def replace_email(match):
            self.report.emails_redacted += 1
            self.report.total_redactions += 1
            email = match.group(0)
            self.report.details.append(f"Email redacted: {email}")
            return "[Email]"

        text = re.sub(email_pattern, replace_email, text)

        return text

    def sanitize_specific_dates(self, text: str) -> str:
        """
        Optionally redact specific dates (keep year/quarter for context)

        This is conservative - only redacts in sensitive contexts
        """

        # Only redact dates in specific sensitive contexts
        sensitive_contexts = [
            r'(?:signed on|executed on|dated)\s+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})',
            r'(?:birth date|DOB|born on)\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})',
        ]

        for pattern in sensitive_contexts:
            def replace_date(match):
                self.report.dates_redacted += 1
                self.report.total_redactions += 1
                date = match.group(1)
                self.report.details.append(f"Date redacted: {date}")
                return match.group(0).replace(date, "[Date]")

            text = re.sub(pattern, replace_date, text, flags=re.IGNORECASE)

        return text

    def get_report(self) -> RedactionReport:
        """Return summary of redactions"""
        return self.report

    def get_reverse_map(self) -> Dict[str, str]:
        """
        Get mapping to reverse sanitization (for internal use only)

        Returns:
            Dict mapping placeholder → original value
        """
        reverse_map = {}

        # Reverse entity map
        for original, placeholder in self.entity_map.items():
            reverse_map[placeholder] = original

        # Reverse person map
        for original, placeholder in self.person_map.items():
            reverse_map[placeholder] = original

        return reverse_map


def sanitize_file(input_path: str, output_path: str) -> RedactionReport:
    """
    Sanitize a text file

    Args:
        input_path: Path to file with confidential information
        output_path: Path to save sanitized output

    Returns:
        RedactionReport with details
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    sanitizer = FactSanitizer()
    sanitized = sanitizer.sanitize_text(text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sanitized)

    return sanitizer.get_report()


def quick_sanitize(text: str) -> Tuple[str, RedactionReport]:
    """
    Quick sanitization helper

    Args:
        text: Text to sanitize

    Returns:
        Tuple of (sanitized_text, report)
    """
    sanitizer = FactSanitizer()
    sanitized = sanitizer.sanitize_text(text)
    return sanitized, sanitizer.get_report()
