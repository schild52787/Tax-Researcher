"""
Memo Template Generator

Generate structured memo templates following Cargill house style.
"""

from datetime import datetime
from typing import Optional, List


class MemoTemplate:
    """Generate tax memo templates"""

    @staticmethod
    def generate_blank_memo(
        matter_title: str,
        question: str,
        author: Optional[str] = None,
        date: Optional[str] = None
    ) -> str:
        """
        Generate blank memo template with all required sections

        Args:
            matter_title: Short title for the matter
            question: Research question
            author: Author name (default: [Author])
            date: Date (default: today)

        Returns:
            Formatted memo template
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        if not author:
            author = "[Author]"

        template = f"""# International Tax Memo: {matter_title}

**Date:** {date}
**Prepared by:** {author}
**Matter:** {matter_title}

---

## Executive Answer

[Provide bottom-line answer in ≤150 words. State the conclusion first, then key supporting points. No citations unless critical.]

---

## Issue Presented

{question}

---

## Facts (Sanitized)

[Concise bullets of essential facts. Use placeholders for entities: [Cargill Entity A], [Cargill Entity B]. Redact confidential figures unless essential.]

-
-
-

---

## Law & Authorities

[Primary sources first, with pincites. List in logical order.]

### U.S. Statutes & Regulations

- IRC § [section]([subsection])
- Treas. Reg. § [regulation]

### IRS Guidance

- Notice [number], [IRB citation]
- Rev. Rul. [number], [IRB citation]

### Cases

- *[Case Name]*, [Reporter] [Page], [Pincite] ([Court] [Year])

### Treaties & Technical Explanations

- [Treaty name], Art. [number]

### OECD Guidance

- OECD Model Tax Convention, Art. [number], Commentary ¶[number]

### Secondary Sources (if applicable - label clearly)

- [Source] (secondary)

---

## Analysis

[Apply law to facts. Organize by sub-issue. Address counterpoints inline.]

### Sub-Issue 1: [Title]

[Analysis with citations]

### Sub-Issue 2: [Title]

[Analysis with citations]

---

## Conclusion

On balance, we assess **[Opinion Level]** that [restate conclusion].

Opinion levels:
- **Reasonable authority** (~20-30%): Non-frivolous basis in law
- **Substantial authority** (~35-45%): Substantial weight of authorities
- **More likely than not** (>50%): Likely to be sustained
- **Should** (~70-80%): High confidence

[2-3 sentences explaining why this level is appropriate based on authorities and facts]

---

## Red-Team (Counter-Arguments)

[Present 3 strongest counter-arguments, each with: (1) thesis, (2) authority cite, (3) likelihood (Low/Med/High), (4) mitigation]

### 1. [Counter-Argument Title]

**Thesis:** [Brief description]

**Authority:** [Citation]

**Likelihood:** [Low/Medium/High]

**Mitigation:** [How to address]

### 2. [Counter-Argument Title]

**Thesis:** [Brief description]

**Authority:** [Citation]

**Likelihood:** [Low/Medium/High]

**Mitigation:** [How to address]

### 3. [Counter-Argument Title]

**Thesis:** [Brief description]

**Authority:** [Citation]

**Likelihood:** [Low/Medium/High]

**Mitigation:** [How to address]

---

## Risk & Penalty Shield

[Include ONLY if overall risk > Medium]

[Discuss reasonable-cause defense, substantial authority standard, and documentation requirements. Reference contemporaneous records needed.]

---

## Follow-Ups & Assumptions

### Assumptions

1.
2.
3.

### Follow-Up Questions

1.
2.
3.

### Additional Data Needed

-
-

---

## Exhibits / Evidence List

- **Ex. A** — [Description]
- **Ex. B** — [Description]
- **Ex. C** — [Description]

---

## QA Checklist

- [ ] All required sections present
- [ ] Executive Answer ≤150 words
- [ ] Citations properly formatted with pincites
- [ ] Cases use Bluebook format
- [ ] IRC citations use § symbol
- [ ] IRS guidance includes I.R.B. citations
- [ ] Opinion level stated in Conclusion
- [ ] Red-Team has 3 counter-arguments with likelihoods
- [ ] Risk section included only if risk > Medium
- [ ] Facts sanitized (no client identifiers)
- [ ] URLs include date accessed
- [ ] No fabricated citations
- [ ] Cases Shepardized (evidence on file)

**Reviewer:** _________________ **Date:** _________

---

*This memo is attorney work product prepared for internal use. Confidential and privileged.*
"""

        return template

    @staticmethod
    def generate_research_plan_template(
        matter_title: str,
        question: str
    ) -> str:
        """
        Generate research plan template

        Args:
            matter_title: Matter title
            question: Research question

        Returns:
            Formatted research plan template
        """
        date = datetime.now().strftime("%Y-%m-%d")

        template = f"""# Research Plan: {matter_title}

**Date:** {date}
**Question:** {question}

---

## 1) Matter Snapshot

- **Short Title:** {matter_title}
- **Question to Answer:** {question}
- **Jurisdictions / Regimes:** [US Subpart F/GILTI; OECD Pillar Two; Treaty X-Y; Country A/B]
- **Time Period / Tax Years:** [Specify]
- **Deliverable:** Executive answer + Practitioner memo
- **Deadline:** [Date]

---

## 2) Facts (Sanitized)

[3-10 bullets of essential facts. Remove/mask identifiers.]

-
-
-

---

## 3) Issues & Sub-Issues

1. **[Sub-issue #1]**
   - Hypothesis / what would prove or refute:

2. **[Sub-issue #2]**
   - Hypothesis:

3. **[Sub-issue #3]**
   - Hypothesis:

---

## 4) Authorities to Consult

### 4.1 U.S. Primary

- **IRC:** § [section]
- **Treasury Regulations:** § [regulation]
- **IRS Guidance:** Notice [number]; Rev. Rul. [number]
- **Cases:** [Bluebook cites with pincites]

### 4.2 OECD / Pillar Two

- **Model Convention:** Art. [number], Commentary ¶[number]
- **Administrative Guidance:** §[section] ([Month YYYY] update)

### 4.3 Treaties & Technical Explanations

- **Treaty (X-Y):** Art. [number], LOB provisions
- **Technical Explanation:** pages [number]

### 4.4 Local Law

- **Statutes:** [citation]
- **Regulations:** [citation]
- **Official translations:** [Yes/No]

### 4.5 Secondary (label as secondary)

- [Big Four / law firm memos]
- [Treatises / journals]

---

## 5) Search Strategy & Source Locations

### Government Portals

- IRS.gov: [specific pages]
- OECD.org: [specific pages]
- EUR-Lex / official gazettes: [if applicable]

### Search Strings

- `"[term]" + site:irs.gov + "IRC"`
- `"[term]" + site:oecd.org + "Article X"`

### Case Law

- [Public sources; note Shepardization needed]

---

## 6) Expected Deliverables & Exhibits

### Tables/Appendices

- [ ] Treaty LOB/BO table
- [ ] PE risk grid
- [ ] Withholding rate matrix
- [ ] Other: [specify]

---

## 7) Assumptions, Unknowns, Data Requests

### Assumptions (to proceed)

1.
2.
3.

### Unknowns / Clarifications Needed

1.
2.
3.

### Data / Documents to Request

- Contracts
- Org charts
- Payment logs
- TP documentation
- Other:

---

## 8) Risk Forecasters (Early View)

- **Sub-issue #1:** [Reasonable authority / Substantial authority / MLTN / Should] (tentative)
- **Sub-issue #2:** [Level] (tentative)
- **Overall:** [Level] (tentative)

**Penalty shield needed:** [Yes/No - only if overall risk > Medium]

---

## 9) Plan Approval

- **Reviewer:** [Name]
- **Date:** [Date]
- **Decision:** [Approved / Revise: ...]
- **Notes:**

---
"""

        return template


def generate_memo(matter_title: str, question: str) -> str:
    """
    Quick helper to generate blank memo

    Args:
        matter_title: Matter title
        question: Research question

    Returns:
        Blank memo template
    """
    return MemoTemplate.generate_blank_memo(matter_title, question)


def generate_research_plan(matter_title: str, question: str) -> str:
    """
    Quick helper to generate research plan

    Args:
        matter_title: Matter title
        question: Research question

    Returns:
        Research plan template
    """
    return MemoTemplate.generate_research_plan_template(matter_title, question)
