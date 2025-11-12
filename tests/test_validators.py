"""Tests for validators"""

import pytest
from src.validators.citation_format import CitationValidator, validate_specific_citation
from src.validators.qa_checker import QAChecker


class TestCitationValidator:
    """Test citation format validation"""

    def test_valid_irc_citation(self):
        """Test valid IRC citation"""
        validator = CitationValidator()
        text = "IRC § 951A(c)(2)(A)(i) provides that..."
        valid, issues = validator.validate_irc(text)
        assert valid

    def test_invalid_irc_citation(self):
        """Test invalid IRC citation (missing §)"""
        validator = CitationValidator()
        text = "IRC Section 951A provides that..."
        valid, issues = validator.validate_irc(text)
        assert not valid
        assert len(issues) > 0

    def test_valid_regulation(self):
        """Test valid regulation citation"""
        validator = CitationValidator()
        text = "Treas. Reg. § 1.951A-2(b)(2)(i)"
        valid, issues = validator.validate_regulations(text)
        assert valid

    def test_case_citation_format(self):
        """Test case citation format"""
        text = "*WH Holdings, LLC v. United States*, 601 F.3d 1319, 1323 (Fed. Cir. 2010)."
        valid, msg = validate_specific_citation(text, 'case')
        assert valid

    def test_citation_summary(self):
        """Test citation counting"""
        validator = CitationValidator()
        text = """
        IRC § 951A(c)(2) and IRC § 954(a) apply.
        See Treas. Reg. § 1.951A-2(b).
        Notice 2020-69, 2020-40 I.R.B. 600.
        """
        summary = validator.get_citation_summary(text)

        assert summary['irc_sections'] >= 2
        assert summary['regulations'] >= 1
        assert summary['notices'] >= 1


class TestQAChecker:
    """Test QA checker"""

    def test_executive_answer_word_count(self):
        """Test executive answer word count check"""
        memo = """
# Tax Memo

## Executive Answer

This is a test executive answer that contains exactly twenty words to test the word counting functionality properly works.

## Issue Presented

Test question?
        """

        checker = QAChecker(memo)
        checker.check_word_counts()

        # Find the executive answer check
        ea_check = next(
            (c for c in checker.report.checks if "Executive Answer" in c.check_name),
            None
        )
        assert ea_check is not None
        assert ea_check.passed  # 20 words is ≤150

    def test_missing_sections(self):
        """Test detection of missing sections"""
        memo = """
# Incomplete Memo

## Executive Answer

Test

## Facts

Some facts
        """

        checker = QAChecker(memo)
        checker.check_structure()

        # Should fail - missing required sections
        failed_checks = [c for c in checker.report.checks if not c.passed]
        assert len(failed_checks) > 0

    def test_opinion_level_detection(self):
        """Test opinion level detection"""
        memo = """
# Tax Memo

## Conclusion

On balance, we assess **More likely than not** that the position would be sustained.
        """

        checker = QAChecker(memo)
        checker.check_risk_assessment()

        opinion_check = next(
            (c for c in checker.report.checks if "Opinion level" in c.check_name),
            None
        )
        assert opinion_check is not None
        assert opinion_check.passed

    def test_complete_qa_run(self):
        """Test complete QA check run"""
        # Minimal but complete memo
        memo = """
# Tax Memo

## Executive Answer

Brief answer in under 150 words.

## Issue Presented

Question?

## Facts

Facts here.

## Law & Authorities

IRC § 951A(c)(2).

## Analysis

Analysis here.

## Conclusion

We assess **Substantial authority** for this position.

## Red-Team

1. Counter-argument one - Low likelihood
2. Counter-argument two - Medium likelihood
3. Counter-argument three - Low likelihood

## Follow-Ups

None.

## Exhibits

Ex. A - Contract
        """

        checker = QAChecker(memo)
        report = checker.run_all_checks()

        assert report.total_checks > 0
        assert report.passed_checks > 0
        # Some checks may fail, but structure should be good


def test_validate_specific_citation_irc():
    """Test specific IRC citation validation"""
    valid, msg = validate_specific_citation("IRC § 951A(c)(2)(A)(i)", "irc")
    assert valid

    valid, msg = validate_specific_citation("IRC Section 951A", "irc")
    assert not valid
