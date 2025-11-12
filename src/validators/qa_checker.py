"""
QA Checker

Automated validation of tax memo against QA checklist.
Checks structure, citations, formatting, and completeness.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class QACheck:
    """Individual QA check result"""
    category: str
    check_name: str
    passed: Optional[bool]
    details: str = ""
    expected: str = ""
    actual: str = ""
    line_number: Optional[int] = None


@dataclass
class QAReport:
    """Complete QA report"""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: int = 0
    checks: List[QACheck] = field(default_factory=list)

    @property
    def score(self) -> str:
        return f"{self.passed_checks}/{self.total_checks}"

    @property
    def passed(self) -> bool:
        return self.failed_checks == 0


class QAChecker:
    """Automated QA checklist validation for tax memos"""

    # Required sections per Cargill style guide
    REQUIRED_SECTIONS = [
        "Executive Answer",
        "Issue Presented",
        "Facts",
        "Law & Authorities",
        "Law and Authorities",  # Alternate
        "Analysis",
        "Conclusion",
        "Red-Team",
        "Red Team",  # Alternate
        "Counter-Arguments",  # Alternate
        "Follow-Ups",
        "Follow-Up",  # Alternate
        "Assumptions",
        "Exhibits",
    ]

    # Optional sections
    OPTIONAL_SECTIONS = [
        "Risk & Penalty Shield",
        "Risk and Penalty Shield",
        "QA Checklist",
    ]

    # Opinion levels
    OPINION_LEVELS = [
        "Reasonable authority",
        "Substantial authority",
        "More likely than not",
        "Should",
    ]

    def __init__(self, memo: str):
        """
        Initialize QA checker with memo text

        Args:
            memo: Full text of the tax memo
        """
        self.memo = memo
        self.memo_lower = memo.lower()
        self.lines = memo.split('\n')
        self.report = QAReport()

    def run_all_checks(self) -> QAReport:
        """Run complete QA checklist"""

        self.check_structure()
        self.check_citations()
        self.check_formatting()
        self.check_word_counts()
        self.check_risk_assessment()
        self.check_sanitization()

        # Calculate totals
        self.report.total_checks = len(self.report.checks)
        self.report.passed_checks = sum(
            1 for check in self.report.checks if check.passed is True
        )
        self.report.failed_checks = sum(
            1 for check in self.report.checks if check.passed is False
        )
        self.report.warnings = sum(
            1 for check in self.report.checks if check.passed is None
        )

        return self.report

    def check_structure(self):
        """Check all required sections are present"""

        # Core required sections (must have at least these)
        core_sections = [
            "Executive Answer",
            "Issue Presented",
            "Facts",
            "Analysis",
            "Conclusion",
        ]

        for section in core_sections:
            found, line_num = self._find_section(section)
            self.report.checks.append(QACheck(
                category="Structure",
                check_name=f"Section: {section}",
                passed=found,
                details=f"Found at line {line_num}" if found else "Section not found",
                line_number=line_num
            ))

        # Check for Red-Team section (any variant)
        red_team_found = (
            self._find_section("Red-Team")[0] or
            self._find_section("Red Team")[0] or
            self._find_section("Counter-Arguments")[0]
        )
        self.report.checks.append(QACheck(
            category="Structure",
            check_name="Section: Red-Team/Counter-Arguments",
            passed=red_team_found,
            details="Found" if red_team_found else "Section not found"
        ))

        # Check for Exhibits section
        exhibits_found = self._find_section("Exhibits")[0]
        self.report.checks.append(QACheck(
            category="Structure",
            check_name="Section: Exhibits",
            passed=exhibits_found,
            details="Found" if exhibits_found else "Section not found"
        ))

    def check_citations(self):
        """Validate citations using citation validator"""

        # Import here to avoid circular imports
        from .citation_format import CitationValidator

        validator = CitationValidator()
        valid, issues = validator.validate_all(self.memo)

        # Overall citation validity
        self.report.checks.append(QACheck(
            category="Citations",
            check_name="All citations properly formatted",
            passed=valid,
            details=f"Found {len(issues)} citation issues" if not valid else "All citations valid"
        ))

        # Check for pincites
        citation_pattern = r'(?:IRC\s*§|Treas\.\s*Reg\.\s*§|Art\.)\s*[\d\.]+[A-Z]?'
        citations = re.findall(citation_pattern, self.memo)

        self.report.checks.append(QACheck(
            category="Citations",
            check_name="Citations include pincites",
            passed=None,  # Requires manual verification
            details=f"Found {len(citations)} citations - verify pincites manually",
            actual=str(len(citations))
        ))

        # Check for unknown/unverified citations
        has_unknown = "Unknown—needs manual check" in self.memo
        self.report.checks.append(QACheck(
            category="Citations",
            check_name="No unverified citations",
            passed=not has_unknown,
            details="Found 'Unknown—needs manual check' flags" if has_unknown else "All citations appear verified"
        ))

        # Check for case validation notes
        case_pattern = r'\*[^*]+\*[^.]*\d+\s+[A-Z][A-Za-z\.]*\s+\d+'
        cases = re.findall(case_pattern, self.memo)

        if cases:
            shepardize_mentioned = bool(re.search(r'shepard|bcite|cite check', self.memo_lower))
            self.report.checks.append(QACheck(
                category="Citations",
                check_name="Case validation documented",
                passed=None,  # Requires manual verification
                details=f"Found {len(cases)} cases - Shepardization {'mentioned' if shepardize_mentioned else 'not mentioned'}",
                actual=str(len(cases))
            ))

    def check_formatting(self):
        """Check formatting requirements"""

        # Check for proper IRC format
        bad_irc = re.findall(r'\bIRC\s+Section\s+\d+', self.memo, re.IGNORECASE)
        self.report.checks.append(QACheck(
            category="Formatting",
            check_name="IRC uses § symbol (not 'Section')",
            passed=len(bad_irc) == 0,
            details=f"Found {len(bad_irc)} instances of 'IRC Section X'" if bad_irc else "Correct"
        ))

        # Check for case name italicization
        potential_cases = re.findall(r'\b\w+\s+v\.\s+\w+\b', self.memo)
        unitalicized_cases = [c for c in potential_cases if f'*{c}*' not in self.memo]

        if potential_cases:
            self.report.checks.append(QACheck(
                category="Formatting",
                check_name="Case names italicized",
                passed=len(unitalicized_cases) == 0,
                details=f"Found {len(unitalicized_cases)} potentially unitalicized cases" if unitalicized_cases else "Correct"
            ))

        # Check for heading structure
        headings = [line for line in self.lines if line.startswith('#')]
        self.report.checks.append(QACheck(
            category="Formatting",
            check_name="Uses markdown headings",
            passed=len(headings) > 0,
            details=f"Found {len(headings)} headings",
            actual=str(len(headings))
        ))

    def check_word_counts(self):
        """Check word count requirements"""

        # Executive Answer must be ≤150 words
        exec_answer = self._extract_section("Executive Answer")
        if exec_answer:
            word_count = len(exec_answer.split())
            self.report.checks.append(QACheck(
                category="Word Counts",
                check_name="Executive Answer ≤150 words",
                passed=word_count <= 150,
                details=f"{word_count} words",
                expected="≤150",
                actual=str(word_count)
            ))
        else:
            self.report.checks.append(QACheck(
                category="Word Counts",
                check_name="Executive Answer ≤150 words",
                passed=False,
                details="Executive Answer section not found"
            ))

        # Check total memo length (should be substantial)
        total_words = len(self.memo.split())
        self.report.checks.append(QACheck(
            category="Word Counts",
            check_name="Memo is substantial (>500 words)",
            passed=total_words > 500,
            details=f"{total_words} total words",
            actual=str(total_words)
        ))

    def check_risk_assessment(self):
        """Check risk assessment and opinion level"""

        # Check if opinion level is stated
        opinion_found = None
        opinion_used = None

        for level in self.OPINION_LEVELS:
            if level.lower() in self.memo_lower:
                opinion_found = True
                opinion_used = level
                break

        self.report.checks.append(QACheck(
            category="Risk Assessment",
            check_name="Opinion level stated",
            passed=opinion_found,
            details=f"Found: {opinion_used}" if opinion_found else "No opinion level found",
            actual=opinion_used or "None"
        ))

        # Check if Red-Team has 3 counter-arguments
        red_team_section = self._extract_section("Red-Team") or self._extract_section("Red Team")
        if red_team_section:
            # Count numbered items or bullet points in red-team section
            numbered = re.findall(r'^\s*\d+\.', red_team_section, re.MULTILINE)
            bullets = re.findall(r'^\s*[-*]', red_team_section, re.MULTILINE)
            counter_args = max(len(numbered), len(bullets))

            self.report.checks.append(QACheck(
                category="Risk Assessment",
                check_name="Red-Team has 3 counter-arguments",
                passed=counter_args >= 3,
                details=f"Found {counter_args} counter-arguments",
                expected="3",
                actual=str(counter_args)
            ))

            # Check if likelihoods mentioned
            has_likelihood = bool(re.search(r'\b(?:low|medium|med|high)\b', red_team_section, re.IGNORECASE))
            self.report.checks.append(QACheck(
                category="Risk Assessment",
                check_name="Counter-arguments include likelihood",
                passed=has_likelihood,
                details="Likelihood assessments found" if has_likelihood else "No likelihood assessments found"
            ))

        # Check Risk & Penalty Shield section logic
        has_risk_section = (
            "Risk & Penalty Shield" in self.memo or
            "Risk and Penalty Shield" in self.memo
        )

        self.report.checks.append(QACheck(
            category="Risk Assessment",
            check_name="Risk & Penalty Shield section appropriateness",
            passed=None,  # Requires judgment
            details="Risk section present - verify only included if risk > Medium" if has_risk_section else "No risk section - acceptable if risk ≤ Medium"
        ))

    def check_sanitization(self):
        """Check if facts appear to be sanitized"""

        # Look for potential confidential information
        warnings = []

        # Check for email addresses
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', self.memo)
        if emails:
            warnings.append(f"Found {len(emails)} email addresses")

        # Check for specific dollar amounts (not rounded)
        specific_amounts = re.findall(r'\$\d+,\d{3},\d{3}(?:\.\d{2})', self.memo)
        if specific_amounts:
            warnings.append(f"Found {len(specific_amounts)} specific dollar amounts")

        # Check for common entity suffixes without placeholders
        entities = re.findall(r'\b(?!Cargill)[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:LLC|Inc\.|Corp\.)', self.memo)
        if entities:
            warnings.append(f"Found {len(entities)} named entities (verify sanitized)")

        sanitized = len(warnings) == 0
        self.report.checks.append(QACheck(
            category="Sanitization",
            check_name="Facts appear sanitized",
            passed=sanitized,
            details="Looks sanitized" if sanitized else "; ".join(warnings)
        ))

    def _find_section(self, section_name: str) -> Tuple[bool, Optional[int]]:
        """Find if section exists and return line number"""

        # Look for section as heading
        patterns = [
            rf'^#+\s*{re.escape(section_name)}\s*$',
            rf'^#+\s*{re.escape(section_name)}[:\s]',
            rf'^\*\*{re.escape(section_name)}\*\*',
        ]

        for i, line in enumerate(self.lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return True, i

        return False, None

    def _extract_section(self, section_name: str) -> Optional[str]:
        """Extract text content of a section"""

        found, start_line = self._find_section(section_name)
        if not found or start_line is None:
            return None

        # Extract content from start_line to next section
        content_lines = []
        in_section = False

        for i, line in enumerate(self.lines, 1):
            if i == start_line:
                in_section = True
                continue

            if in_section:
                # Stop at next heading
                if re.match(r'^#+\s', line):
                    break
                content_lines.append(line)

        return '\n'.join(content_lines).strip()


def generate_qa_report_text(report: QAReport) -> str:
    """
    Generate human-readable QA report

    Args:
        report: QAReport object

    Returns:
        Formatted text report
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"QA REPORT: {report.score}")
    lines.append(f"Status: {'✓ PASSED' if report.passed else '✗ FAILED'}")
    lines.append("=" * 60)
    lines.append("")

    # Group by category
    categories = {}
    for check in report.checks:
        if check.category not in categories:
            categories[check.category] = []
        categories[check.category].append(check)

    for category, checks in categories.items():
        lines.append(f"\n{category.upper()}:")
        lines.append("-" * 60)

        for check in checks:
            if check.passed is True:
                status = "✓"
            elif check.passed is False:
                status = "✗"
            else:
                status = "⚠"

            lines.append(f"  {status} {check.check_name}")

            if check.details:
                lines.append(f"      {check.details}")

            if check.expected and check.actual:
                lines.append(f"      Expected: {check.expected}, Actual: {check.actual}")

    lines.append("\n" + "=" * 60)
    lines.append(f"Summary: {report.passed_checks} passed, {report.failed_checks} failed, {report.warnings} warnings")
    lines.append("=" * 60)

    return '\n'.join(lines)
