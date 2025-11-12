# Getting Started with Cargill Tax Research Agent

## Quick Start Guide

### 1. Installation (5 minutes)

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

### 2. First Use - Sanitize Facts (2 minutes)

Create a file with your facts:

```bash
# Create facts file
cat > my_facts.txt << 'EOF'
ABC Trading LLC entered into an agreement with DEF Corp.
John Smith, CFO, approved the transaction for $1,500,000.
Contact: john.smith@example.com
EOF

# Sanitize the facts
python -m src.cli sanitize my_facts.txt

# View sanitized output
cat my_facts_sanitized.txt
```

You'll see:
- Company names → `[Third Party Entity A]`
- Personal names → `[CFO]`
- Dollar amounts → `[Amount]`
- Emails → `[Email]`

### 3. Generate a Blank Memo Template (1 minute)

```bash
python -m src.cli template \
  --matter "Transfer Pricing Analysis" \
  --question "Are services at arm's length?" \
  --output my_memo.md
```

This creates a complete memo structure with all required sections.

### 4. Validate Citation Format (1 minute)

```bash
python -m src.cli validate examples/sample_memo.md
```

See validation results for:
- IRC citations (§ symbol usage)
- Case citations (Bluebook format)
- IRS guidance citations (I.R.B. references)
- Pincites

### 5. Run QA Checklist (1 minute)

```bash
python -m src.cli qa examples/sample_memo.md
```

Get automated QA report checking:
- All required sections present
- Executive Answer word count (≤150)
- Opinion level stated
- Red-Team counter-arguments (3 required)
- Citation formats
- Fact sanitization

### 6. Generate Research Plan with Claude (2 minutes)

```bash
# Make sure ANTHROPIC_API_KEY is set in .env
python -m src.cli plan \
  --question "Does Entity A have Subpart F income?" \
  --facts my_facts_sanitized.txt \
  --jurisdictions "US" "Luxembourg" \
  --output research_plan.md
```

Claude will generate a comprehensive research plan with:
- Relevant IRC sections and regulations to review
- IRS guidance to search
- Cases to research
- OECD guidance (if applicable)
- Search strategy
- Assumptions and follow-ups

### 7. Search IRS Guidance (30 seconds)

```bash
# Search for a Notice
python -m src.cli search-irs "Notice 2020-69" --year 2020

# Verify a citation exists
python -m src.cli verify-citation "Notice 2020-69" --type notice
```

### 8. Comprehensive Memo Review with Claude (2 minutes)

```bash
python -m src.cli review my_memo.md
```

Claude will:
- Check structure and completeness
- Review all citations substantively
- Identify potential issues
- Assess overall quality

## Typical Workflow

### For a New Tax Research Project:

**Step 1: Intake & Sanitization (5 min)**
```bash
# Get facts from client/team
# Sanitize immediately
python -m src.cli sanitize raw_facts.txt -o sanitized_facts.txt
```

**Step 2: Research Planning (10 min)**
```bash
# Generate research plan with Claude
python -m src.cli plan \
  -q "Your tax question?" \
  -f sanitized_facts.txt \
  -o research_plan.md

# Review and refine the plan
# Approve before drafting
```

**Step 3: Research & Drafting (manual)**
- Use research plan to guide research
- Search IRS and OECD as needed
- Draft memo following template

**Step 4: Validation (5 min)**
```bash
# Validate citations
python -m src.cli validate draft_memo.md

# Fix any issues found

# Run QA checklist
python -m src.cli qa draft_memo.md -o qa_report.json

# Address failed checks
```

**Step 5: Final Review (5 min)**
```bash
# Use Claude for comprehensive review
python -m src.cli review draft_memo.md

# Manual Shepardization (required)
# Check cases on Lexis or Bloomberg Law

# Final QA check
python -m src.cli qa final_memo.md
```

## CLI Command Reference

### `sanitize` - Redact Confidential Information
```bash
python -m src.cli sanitize <input_file> [-o output_file] [-r report_file]
```

### `validate` - Check Citation Formats
```bash
python -m src.cli validate <memo_file> [-f json|text] [-o output]
```

### `qa` - Run QA Checklist
```bash
python -m src.cli qa <memo_file> [-o output] [-f json|text]
```

### `plan` - Generate Research Plan
```bash
python -m src.cli plan \
  --question "Tax question?" \
  [--facts facts_file] \
  [--jurisdictions US EU] \
  [--output plan.md]
```

### `template` - Generate Blank Template
```bash
python -m src.cli template \
  --matter "Matter title" \
  --question "Question?" \
  [--output file.md] \
  [--type memo|research_plan]
```

### `search-irs` - Search IRS Guidance
```bash
python -m src.cli search-irs "search term" [--year 2020] [-o output]
```

### `verify-citation` - Verify Citation Exists
```bash
python -m src.cli verify-citation "Notice 2020-69" --type notice
```

### `search-oecd` - Search OECD Guidance
```bash
python -m src.cli search-oecd "GloBE" [-o output]
```

### `review` - Comprehensive Claude Review
```bash
python -m src.cli review <memo_file>
```

## Tips & Best Practices

### 1. Always Sanitize First
Never feed raw client facts to Claude. Use `sanitize` first.

### 2. Use Research Plans
Generate a research plan before drafting. It ensures comprehensive coverage.

### 3. Validate Early and Often
Run `validate` after adding citations to catch format issues immediately.

### 4. QA Before Delivery
Always run `qa` before finalizing. Fix all failed checks.

### 5. Manual Shepardization Required
The tool cannot Shepardize cases automatically. This must be done manually on Lexis/Bloomberg.

### 6. Document Assumptions
Use the Follow-Ups & Assumptions section to document what you assumed.

### 7. Red-Team Your Analysis
Include 3 strong counter-arguments with authorities and likelihoods.

### 8. Opinion Level Precision
Use the correct opinion level based on authority weight:
- **Reasonable authority** (~20-30%): Non-frivolous basis
- **Substantial authority** (~35-45%): Substantial weight
- **More likely than not** (>50%): Likely sustained
- **Should** (~70-80%): High confidence

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_sanitizer.py -v

# Run with coverage
pytest --cov=src tests/
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
```bash
# Check .env file exists
cat .env

# Verify key is set
grep ANTHROPIC_API_KEY .env

# If not set, add it
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### "Module not found"
```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Citations Not Validating
- Check IRC uses § not "Section"
- Verify cases use Bluebook format with italics (asterisks in markdown)
- Ensure pincites are included
- IRS guidance must have I.R.B. citations

## Need Help?

- **Documentation**: See `/docs` for house style guide, QA checklist, and templates
- **Examples**: See `/examples` for sample memo and research plan
- **Issues**: Contact Cargill International Tax team

---

**Version**: 1.0.0
**Last Updated**: 2024-11-12
