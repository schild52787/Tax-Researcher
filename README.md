# Cargill Tax Research Agent

> **Zero-cost AI-assisted international tax research system** for producing practitioner-grade tax memos with verified citations, automated QA checks, and risk analysis.

## 🎯 Purpose

Execute practitioner-grade international tax research for complex Subpart F, GILTI, treaty, transfer pricing, and OECD Pillar 2 matters. Designed for Cargill's international tax team with built-in compliance, confidentiality, and quality controls.

## ✨ Features

- **🔒 Fact Sanitization** - Automatic redaction of confidential information
- **📋 Citation Validation** - Regex-based format checking for IRC, regulations, cases, treaties
- **✅ Automated QA** - Pre-delivery checklist validation
- **🌐 Web Scraping** - Free access to IRS.gov and OECD.org resources
- **🤖 Claude Integration** - AI-powered memo generation and review
- **📊 Risk Assessment** - Opinion level rubric enforcement
- **🛡️ Zero External Costs** - No paid APIs or subscriptions required

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Tax-Researcher

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Basic Usage

```bash
# Sanitize confidential facts
tax-research sanitize facts.txt -o sanitized_facts.txt

# Validate memo citations and format
tax-research validate draft_memo.md

# Run QA checklist
tax-research qa final_memo.md -o qa_report.json

# Generate research plan
tax-research plan -q "Does Entity A have Subpart F income?"

# Search IRS guidance
tax-research search-irs "Notice 2020-69"

# Verify citation exists
tax-research verify-citation "IRC § 951A(c)(2)(A)(i)"
```

## 📁 Project Structure

```
tax-researcher/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── src/
│   ├── __init__.py
│   ├── agent.py                    # Claude orchestration
│   ├── sanitizer.py                # Fact redaction
│   ├── cli.py                      # Command-line interface
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── citation_format.py      # Regex citation validation
│   │   ├── document_structure.py   # Memo structure validation
│   │   └── qa_checker.py           # Automated QA checklist
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── irs_scraper.py         # IRS.gov web scraping
│   │   └── oecd_scraper.py        # OECD.org web scraping
│   └── templates/
│       ├── __init__.py
│       └── memo_template.py       # Memo generation
├── prompts/
│   ├── research_agent_prompt.md   # Main research workflow
│   ├── citation_validator_prompt.md
│   └── qa_checker_prompt.md
├── docs/
│   ├── house_style_guide.md       # Citation & formatting rules
│   ├── opinion_rubric.md          # Risk level standards
│   ├── qa_checklist.md            # Quality assurance checklist
│   └── research_plan_template.md  # Research planning template
├── tests/
│   ├── test_sanitizer.py
│   ├── test_validators.py
│   └── test_scrapers.py
└── examples/
    ├── sample_facts.txt
    ├── sample_memo.md
    └── sample_research_plan.md
```

## 📖 Documentation

- **[House Style Guide](docs/house_style_guide.md)** - Citation formats and writing standards
- **[Opinion Rubric](docs/opinion_rubric.md)** - Risk assessment framework
- **[QA Checklist](docs/qa_checklist.md)** - Pre-delivery validation
- **[Research Plan Template](docs/research_plan_template.md)** - Research planning guide

## 🔧 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
# Format code
black src/ tests/

# Type checking
mypy src/
```

## 🔐 Security & Compliance

- **Confidentiality**: All facts automatically sanitized before AI processing
- **No Data Storage**: No information sent to external services (except Claude API)
- **Enterprise Claude Only**: Designed for Anthropic's enterprise API
- **Audit Trail**: All operations logged for compliance

## 📝 Typical Workflow

1. **Intake & Sanitization**
   ```bash
   tax-research sanitize client_facts.txt -o sanitized.txt
   ```

2. **Research Plan**
   ```bash
   tax-research plan -q "Tax treatment question?" -f sanitized.txt
   ```

3. **Draft Memo** (using Claude with prompts)
   - Use `prompts/research_agent_prompt.md` as system prompt
   - Feed sanitized facts and research plan

4. **Validate Citations**
   ```bash
   tax-research validate draft_memo.md
   ```

5. **QA Check**
   ```bash
   tax-research qa draft_memo.md -o report.json
   ```

6. **Final Review** (manual Shepardization via Lexis/Bloomberg)

## 🤝 Contributing

Internal Cargill project. Contact the International Tax team for access.

## 📄 License

Proprietary - Cargill Incorporated

## 🆘 Support

For issues or questions, contact the International Tax AI Working Group.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Maintained by**: Cargill International Tax Team
