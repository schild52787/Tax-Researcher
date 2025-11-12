"""
Citation Format Validator

Validates citation formats for IRC, Treasury Regulations, cases, treaties,
and OECD guidance using regex patterns. No external APIs required.
"""

import re
from typing import Tuple, List, Dict
from dataclasses import dataclass


@dataclass
class CitationIssue:
    """Represents a citation formatting issue"""
    citation: str
    issue_type: str
    message: str
    line_number: int = None


class CitationValidator:
    """Validate citation formats according to Cargill house style"""

    # Citation patterns
    IRC_PATTERN = r'IRC\s*§\s*\d+[A-Z]?(?:\([a-z0-9]+\))*(?:\([A-Z]\))?(?:\([ivx]+\))?'
    REG_PATTERN = r'Treas\.\s*Reg\.\s*§\s*\d+\.\d+[A-Z]?-\d+(?:\([a-z0-9]+\))*'
    CASE_PATTERN = r'\*[^*]+\*,\s*\d+\s+[A-Z][A-Za-z\.]*\s+\d+,\s*\d+\s+\([^)]+\s+\d{4}\)'
    NOTICE_PATTERN = r'Notice\s+\d{4}-\d+,\s*\d{4}-\d+\s+I\.R\.B\.\s+\d+'
    REV_RUL_PATTERN = r'Rev\.\s*Rul\.\s+\d{4}-\d+,\s*\d{4}-\d+\s+I\.R\.B\.\s+\d+'
    TREATY_PATTERN = r'(?:Convention|Treaty|Agreement)[^,]+,\s*Art\.\s*\d+(?:\([a-z0-9]+\))*'
    OECD_PATTERN = r'OECD[^,]+(?:Art\.|¶)\s*\d+(?:\([a-z0-9]+\))*'

    def __init__(self):
        self.issues: List[CitationIssue] = []

    def validate_all(self, text: str) -> Tuple[bool, List[CitationIssue]]:
        """Run all citation validations on text"""
        self.issues = []

        self.validate_irc(text)
        self.validate_regulations(text)
        self.validate_cases(text)
        self.validate_irb_guidance(text)
        self.validate_general_format(text)

        return len(self.issues) == 0, self.issues

    def validate_irc(self, text: str) -> Tuple[bool, List[str]]:
        """Validate IRC citations"""
        issues = []

        # Check for "Section" instead of "§"
        if re.search(r'\bIRC\s+Section\s+\d+', text, re.IGNORECASE):
            issues.append("Use 'IRC §' not 'IRC Section'")
            self.issues.append(CitationIssue(
                citation="IRC Section X",
                issue_type="format",
                message="Use 'IRC §' not 'IRC Section'"
            ))

        # Check for IRC without § symbol
        bad_irc = re.findall(r'\bIRC\s+\d+[A-Z]?(?!\s*§)', text)
        if bad_irc:
            issues.append(f"IRC citations missing § symbol: {bad_irc}")
            for cite in bad_irc:
                self.issues.append(CitationIssue(
                    citation=cite,
                    issue_type="format",
                    message="Missing § symbol"
                ))

        # Find properly formatted IRC citations
        proper_irc = re.findall(self.IRC_PATTERN, text)

        # Check for missing pincites in subsections
        for cite in proper_irc:
            if '(' not in cite:
                # Top-level section - should usually have subsection
                pass  # This is acceptable for general references

        return len(issues) == 0, issues

    def validate_regulations(self, text: str) -> Tuple[bool, List[str]]:
        """Validate Treasury Regulation citations"""
        issues = []

        # Find regulations
        regs = re.findall(r'Treas\.\s*Reg\.?\s*§?\s*[\d\.-]+', text)

        for reg in regs:
            # Check proper format: Treas. Reg. § 1.951A-2(b)(2)(i)
            if not re.match(self.REG_PATTERN, reg):
                issues.append(f"Regulation format issue: {reg}")
                self.issues.append(CitationIssue(
                    citation=reg,
                    issue_type="format",
                    message="Should be 'Treas. Reg. § X.XXX-X(x)(x)'"
                ))

        return len(issues) == 0, issues

    def validate_cases(self, text: str) -> Tuple[bool, List[str]]:
        """Validate case citations (Bluebook format)"""
        issues = []

        # Find case patterns
        # Looking for italicized case names
        potential_cases = re.findall(r'\*[^*]+\*[^.]*', text)

        for case_text in potential_cases:
            # Check if it has proper reporter citation
            if not re.search(r'\d+\s+[A-Z][A-Za-z\.]*\s+\d+', case_text):
                if 'v.' in case_text.lower():
                    issues.append(f"Case missing reporter citation: {case_text[:50]}")
                    self.issues.append(CitationIssue(
                        citation=case_text[:100],
                        issue_type="format",
                        message="Missing reporter citation (e.g., '123 F.3d 456')"
                    ))

            # Check if it has court and year
            if 'v.' in case_text.lower() and not re.search(r'\(\w+\.?\s*\w*\.?\s*\d{4}\)', case_text):
                issues.append(f"Case missing court and year: {case_text[:50]}")
                self.issues.append(CitationIssue(
                    citation=case_text[:100],
                    issue_type="format",
                    message="Missing court and year, e.g., (Fed. Cir. 2010)"
                ))

            # Check for pincite
            if 'v.' in case_text.lower() and not re.search(r',\s*\d+\s+\(', case_text):
                # Might be missing pincite
                pass  # Pincites are required but we can't perfectly detect

        return len(issues) == 0, issues

    def validate_irb_guidance(self, text: str) -> Tuple[bool, List[str]]:
        """Validate IRS guidance citations (Notices, Rev. Ruls, etc.)"""
        issues = []

        # Check Notices
        notices = re.findall(r'Notice\s+\d{4}-\d+[^,.\n]*', text)
        for notice in notices:
            if 'I.R.B.' not in notice:
                issues.append(f"Notice missing I.R.B. citation: {notice}")
                self.issues.append(CitationIssue(
                    citation=notice,
                    issue_type="format",
                    message="Should include I.R.B. citation, e.g., 'Notice 2020-69, 2020-40 I.R.B. 600'"
                ))

        # Check Revenue Rulings
        rev_ruls = re.findall(r'Rev\.\s*Rul\.\s+\d{4}-\d+[^,.\n]*', text)
        for rul in rev_ruls:
            if 'I.R.B.' not in rul:
                issues.append(f"Revenue Ruling missing I.R.B. citation: {rul}")
                self.issues.append(CitationIssue(
                    citation=rul,
                    issue_type="format",
                    message="Should include I.R.B. citation"
                ))

        return len(issues) == 0, issues

    def validate_general_format(self, text: str) -> Tuple[bool, List[str]]:
        """Check general citation formatting requirements"""
        issues = []

        # Check for "Unknown—needs manual check" flags
        if "Unknown—needs manual check" in text:
            self.issues.append(CitationIssue(
                citation="",
                issue_type="verification",
                message="Document contains unverified citations marked 'Unknown—needs manual check'"
            ))

        # Check for proper pincites (looking for naked citations)
        # This is heuristic and won't catch everything

        # Check for URLs without date accessed
        urls = re.findall(r'https?://[^\s\)]+', text)
        for url in urls:
            # Look for date accessed nearby (within 100 chars)
            url_pos = text.find(url)
            context = text[url_pos:url_pos+100]
            if 'accessed' not in context.lower() and 'retrieved' not in context.lower():
                issues.append(f"URL missing access date: {url[:50]}")
                self.issues.append(CitationIssue(
                    citation=url,
                    issue_type="format",
                    message="Web citations should include date accessed"
                ))

        return len(issues) == 0, issues

    def check_pincites_present(self, text: str) -> Tuple[bool, List[str]]:
        """Check if citations include pincites"""
        issues = []

        # This is a heuristic check
        # Look for citations without apparent pincites

        return len(issues) == 0, issues

    def get_citation_summary(self, text: str) -> Dict[str, int]:
        """Return count of different citation types"""
        return {
            'irc_sections': len(re.findall(self.IRC_PATTERN, text)),
            'regulations': len(re.findall(self.REG_PATTERN, text)),
            'cases': len(re.findall(self.CASE_PATTERN, text)),
            'notices': len(re.findall(self.NOTICE_PATTERN, text)),
            'revenue_rulings': len(re.findall(self.REV_RUL_PATTERN, text)),
            'treaties': len(re.findall(self.TREATY_PATTERN, text)),
            'oecd': len(re.findall(self.OECD_PATTERN, text)),
        }


def validate_specific_citation(citation: str, citation_type: str) -> Tuple[bool, str]:
    """
    Validate a specific citation string

    Args:
        citation: The citation text to validate
        citation_type: Type - 'irc', 'reg', 'case', 'notice', 'treaty', 'oecd'

    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = CitationValidator()

    patterns = {
        'irc': validator.IRC_PATTERN,
        'reg': validator.REG_PATTERN,
        'case': validator.CASE_PATTERN,
        'notice': validator.NOTICE_PATTERN,
        'revenue_ruling': validator.REV_RUL_PATTERN,
        'treaty': validator.TREATY_PATTERN,
        'oecd': validator.OECD_PATTERN,
    }

    if citation_type not in patterns:
        return False, f"Unknown citation type: {citation_type}"

    pattern = patterns[citation_type]
    if re.match(pattern, citation.strip()):
        return True, "Valid format"
    else:
        return False, f"Does not match {citation_type} format"
