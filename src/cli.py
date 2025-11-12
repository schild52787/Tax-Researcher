#!/usr/bin/env python3
"""
Cargill Tax Research Agent CLI

Command-line interface for tax research automation.
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional

from .sanitizer import FactSanitizer, sanitize_file
from .validators.citation_format import CitationValidator, validate_specific_citation
from .validators.qa_checker import QAChecker, generate_qa_report_text
from .scrapers.irs_scraper import IRSScraper
from .scrapers.oecd_scraper import OECDScraper
from .agent import TaxResearchAgent
from .templates.memo_template import MemoTemplate


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Cargill Tax Research Agent

    Zero-cost AI-assisted international tax research system.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path')
@click.option('--report', '-r', help='Save redaction report to file')
def sanitize(input_file, output, report):
    """Sanitize confidential facts in a text file"""
    click.echo(f"🔒 Sanitizing {input_file}...")

    output_path = output or str(Path(input_file).with_suffix('')) + '_sanitized.txt'

    redaction_report = sanitize_file(input_file, output_path)

    click.echo(f"✓ Sanitized text saved to {output_path}")
    click.echo(f"  Entities redacted: {redaction_report.entities_redacted}")
    click.echo(f"  People redacted: {redaction_report.people_redacted}")
    click.echo(f"  Amounts redacted: {redaction_report.amounts_redacted}")
    click.echo(f"  Total redactions: {redaction_report.total_redactions}")

    if report:
        with open(report, 'w') as f:
            json.dump({
                'entities_redacted': redaction_report.entities_redacted,
                'people_redacted': redaction_report.people_redacted,
                'amounts_redacted': redaction_report.amounts_redacted,
                'emails_redacted': redaction_report.emails_redacted,
                'total_redactions': redaction_report.total_redactions,
                'details': redaction_report.details
            }, f, indent=2)
        click.echo(f"  Report saved to {report}")


@cli.command()
@click.argument('memo_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['json', 'text']), default='text')
@click.option('--output', '-o', help='Output file for results')
def validate(memo_file, format, output):
    """Validate memo citations and format"""
    click.echo(f"📋 Validating {memo_file}...")

    with open(memo_file, encoding='utf-8') as f:
        memo = f.read()

    validator = CitationValidator()
    valid, issues = validator.validate_all(memo)

    summary = validator.get_citation_summary(memo)

    if format == 'json':
        results = {
            'valid': valid,
            'total_issues': len(issues),
            'issues': [
                {
                    'citation': issue.citation,
                    'type': issue.issue_type,
                    'message': issue.message,
                    'line': issue.line_number
                }
                for issue in issues
            ],
            'summary': summary
        }

        output_text = json.dumps(results, indent=2)
        click.echo(output_text)

        if output:
            with open(output, 'w') as f:
                f.write(output_text)

    else:
        click.echo("\n" + "=" * 60)
        click.echo("CITATION VALIDATION REPORT")
        click.echo("=" * 60)

        click.echo(f"\n📊 Citation Summary:")
        click.echo(f"  IRC sections: {summary['irc_sections']}")
        click.echo(f"  Regulations: {summary['regulations']}")
        click.echo(f"  Cases: {summary['cases']}")
        click.echo(f"  Notices: {summary['notices']}")
        click.echo(f"  Revenue Rulings: {summary['revenue_rulings']}")
        click.echo(f"  Treaties: {summary['treaties']}")
        click.echo(f"  OECD: {summary['oecd']}")

        if valid:
            click.echo(f"\n✓ All citations valid")
        else:
            click.echo(f"\n✗ Found {len(issues)} citation issues:\n")
            for issue in issues:
                click.echo(f"  {issue.issue_type.upper()}: {issue.message}")
                if issue.citation:
                    click.echo(f"    Citation: {issue.citation[:80]}")
                if issue.line_number:
                    click.echo(f"    Line: {issue.line_number}")
                click.echo()


@cli.command()
@click.argument('memo_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output report file (JSON or text)')
@click.option('--format', '-f', type=click.Choice(['json', 'text']), default='text')
def qa(memo_file, output, format):
    """Run QA checklist on memo"""
    click.echo(f"✅ Running QA checklist on {memo_file}...")

    with open(memo_file, encoding='utf-8') as f:
        memo = f.read()

    checker = QAChecker(memo)
    report = checker.run_all_checks()

    if format == 'json':
        results = {
            'score': report.score,
            'passed': report.passed,
            'total_checks': report.total_checks,
            'passed_checks': report.passed_checks,
            'failed_checks': report.failed_checks,
            'warnings': report.warnings,
            'checks': [
                {
                    'category': check.category,
                    'name': check.check_name,
                    'passed': check.passed,
                    'details': check.details,
                    'expected': check.expected,
                    'actual': check.actual,
                    'line': check.line_number
                }
                for check in report.checks
            ]
        }

        output_text = json.dumps(results, indent=2)

        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            click.echo(f"✓ QA report saved to {output}")
        else:
            click.echo(output_text)

    else:
        report_text = generate_qa_report_text(report)
        click.echo("\n" + report_text)

        if output:
            with open(output, 'w') as f:
                f.write(report_text)
            click.echo(f"\n✓ QA report saved to {output}")

        if report.passed:
            click.echo("\n🎉 All QA checks passed!")
            sys.exit(0)
        else:
            click.echo(f"\n⚠️  {report.failed_checks} checks failed - review issues above")
            sys.exit(1)


@cli.command()
@click.option('--question', '-q', prompt='Research question', help='Tax research question')
@click.option('--facts', '-f', type=click.Path(exists=True), help='Sanitized facts file')
@click.option('--jurisdictions', '-j', multiple=True, help='Jurisdictions involved')
@click.option('--output', '-o', default='research_plan.md', help='Output file')
def plan(question, facts, jurisdictions, output):
    """Generate research plan using Claude"""
    click.echo("📝 Generating research plan...")

    facts_text = ""
    if facts:
        with open(facts, encoding='utf-8') as f:
            facts_text = f.read()
    else:
        click.echo("💡 Tip: Provide --facts file for better results")

    try:
        agent = TaxResearchAgent()
        plan = agent.generate_research_plan(
            question=question,
            facts=facts_text,
            jurisdictions=list(jurisdictions) if jurisdictions else None
        )

        with open(output, 'w', encoding='utf-8') as f:
            f.write(plan)

        click.echo(f"✓ Research plan saved to {output}")
        click.echo("\nPreview:")
        click.echo("─" * 60)
        click.echo(plan[:800] + "..." if len(plan) > 800 else plan)

    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        click.echo("💡 Set ANTHROPIC_API_KEY environment variable", err=True)
        sys.exit(1)


@cli.command()
@click.argument('search_term')
@click.option('--year', '-y', type=int, help='Tax year (e.g., 2020)')
@click.option('--output', '-o', help='Save results to file')
def search_irs(search_term, year, output):
    """Search IRS.gov for guidance"""
    click.echo(f"🔍 Searching IRS.gov for: {search_term}")

    scraper = IRSScraper()

    if year:
        results = scraper.search_irb(year, search_term)
    else:
        # Search recent years
        results = []
        current_year = 2025
        for y in range(current_year, current_year - 5, -1):
            results.extend(scraper.search_irb(y, search_term))

    if results:
        click.echo(f"\n✓ Found {len(results)} results:\n")
        for i, result in enumerate(results[:10], 1):
            if 'error' in result:
                click.echo(f"  ❌ Error: {result['error']}")
            else:
                click.echo(f"  {i}. {result.get('title', 'No title')}")
                click.echo(f"     {result.get('url', 'No URL')}")
                click.echo(f"     Type: {result.get('type', 'Unknown')}")
                click.echo()

        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"✓ Results saved to {output}")
    else:
        click.echo("  No results found")


@cli.command()
@click.argument('citation')
@click.option('--type', '-t', type=click.Choice(['notice', 'revenue_ruling', 'irc']),
              help='Citation type')
def verify_citation(citation, type):
    """Verify a citation exists"""
    click.echo(f"🔍 Verifying: {citation}")

    scraper = IRSScraper()

    if type == 'notice' or 'Notice' in citation:
        # Extract notice number
        import re
        match = re.search(r'(\d{4}-\d+)', citation)
        if match:
            result = scraper.verify_notice_exists(match.group(1))
            if result.get('valid'):
                click.echo(f"✓ Citation verified")
                click.echo(f"  URL: {result['url']}")
            else:
                click.echo(f"✗ Citation not found")
                if 'error' in result:
                    click.echo(f"  Error: {result['error']}")

    elif type == 'revenue_ruling' or 'Rev. Rul.' in citation:
        import re
        match = re.search(r'(\d{4}-\d+)', citation)
        if match:
            result = scraper.verify_revenue_ruling(match.group(1))
            if result.get('valid'):
                click.echo(f"✓ Citation verified")
                click.echo(f"  URL: {result['url']}")
            else:
                click.echo(f"✗ Citation not found")

    else:
        click.echo("💡 Specify --type (notice|revenue_ruling|irc)")


@cli.command()
@click.option('--matter', '-m', prompt='Matter title', help='Short matter title')
@click.option('--question', '-q', prompt='Research question', help='Tax question')
@click.option('--output', '-o', help='Output file')
@click.option('--type', '-t', type=click.Choice(['memo', 'research_plan']),
              default='memo', help='Template type')
def template(matter, question, output, type):
    """Generate blank memo or research plan template"""

    if type == 'memo':
        content = MemoTemplate.generate_blank_memo(matter, question)
        default_output = f"{matter.replace(' ', '_')}_memo.md"
    else:
        content = MemoTemplate.generate_research_plan_template(matter, question)
        default_output = f"{matter.replace(' ', '_')}_research_plan.md"

    output_file = output or default_output

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    click.echo(f"✓ {type.title()} template saved to {output_file}")


@cli.command()
@click.argument('keyword')
@click.option('--output', '-o', help='Save results to file')
def search_oecd(keyword, output):
    """Search OECD guidance"""
    click.echo(f"🔍 Searching OECD for: {keyword}")

    scraper = OECDScraper()
    results = scraper.search_pillar_two(keyword)

    if results:
        click.echo(f"\n✓ Found {len(results)} results:\n")
        for i, result in enumerate(results[:10], 1):
            if 'error' in result:
                click.echo(f"  ❌ Error: {result['error']}")
            else:
                click.echo(f"  {i}. {result.get('title', 'No title')}")
                click.echo(f"     {result.get('url', 'No URL')}")
                click.echo()

        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"✓ Results saved to {output}")
    else:
        click.echo("  No results found")


@cli.command()
@click.argument('memo_file', type=click.Path(exists=True))
def review(memo_file):
    """Use Claude to comprehensively review memo"""
    click.echo(f"🤖 Reviewing {memo_file} with Claude...")

    with open(memo_file, encoding='utf-8') as f:
        memo = f.read()

    try:
        agent = TaxResearchAgent()

        click.echo("\n1️⃣ Checking structure...")
        structure_result = agent.validate_memo_structure(memo)

        if 'error' not in structure_result:
            click.echo(f"   Executive Answer: {structure_result.get('executive_answer_word_count', '?')} words")
            click.echo(f"   Opinion Level: {structure_result.get('opinion_level', 'Not stated')}")
            click.echo(f"   Sections: {'✓ Complete' if structure_result.get('all_sections_present') else '✗ Missing sections'}")

            if structure_result.get('missing_sections'):
                click.echo(f"   Missing: {', '.join(structure_result['missing_sections'])}")

        click.echo("\n2️⃣ Reviewing citations...")
        citation_result = agent.review_citations(memo)

        if 'error' not in citation_result:
            click.echo(f"   Total citations: {citation_result.get('total_citations', '?')}")
            click.echo(f"   Quality: {citation_result.get('overall_quality', '?')}")

            if citation_result.get('issues'):
                click.echo(f"   Issues found: {len(citation_result['issues'])}")
                for issue in citation_result['issues'][:5]:
                    click.echo(f"     - {issue.get('issue', '')} ({issue.get('severity', '')})")

        click.echo("\n✓ Review complete")

    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
