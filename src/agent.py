"""
Tax Research Agent

Claude-powered orchestration for tax research workflow.
Uses Claude API for complex validation and memo generation.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import json
from anthropic import Anthropic


class TaxResearchAgent:
    """Orchestrate tax research workflow using Claude"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize tax research agent

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use (defaults to CLAUDE_MODEL env var or sonnet)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.client = Anthropic(api_key=self.api_key)
        self.prompts_dir = Path(__file__).parent.parent / "prompts"

    def generate_research_plan(
        self,
        question: str,
        facts: str,
        jurisdictions: Optional[List[str]] = None
    ) -> str:
        """
        Generate research plan using template

        Args:
            question: Tax research question
            facts: Sanitized facts
            jurisdictions: List of jurisdictions involved

        Returns:
            Formatted research plan
        """
        jurisdictions_str = ", ".join(jurisdictions) if jurisdictions else "To be determined"

        prompt = f"""Generate a comprehensive research plan for this international tax matter.

## Question
{question}

## Facts (Sanitized)
{facts}

## Jurisdictions
{jurisdictions_str}

Create a research plan following the Cargill Research Plan Template format. Include:

1. Matter snapshot (question, jurisdictions, time period)
2. Essential facts (3-10 bullets)
3. Issues & sub-issues with hypotheses
4. Authorities to consult:
   - U.S. primary (IRC sections, regulations, IRS guidance, cases)
   - OECD / Pillar Two guidance
   - Treaties & Technical Explanations
   - Local law
   - Secondary sources (labeled)
5. Search strategy with specific search strings
6. Expected deliverables & exhibits
7. Assumptions, unknowns, data requests
8. Risk forecasters (tentative opinion levels)

Format as markdown with clear sections. Be specific about IRC sections, regulation citations, and OECD guidance to review."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def validate_memo_structure(self, memo: str) -> Dict:
        """
        Use Claude to check memo structure comprehensively

        Args:
            memo: Draft memo text

        Returns:
            Dict with validation results
        """
        prompt = f"""Review this tax memo draft and verify it follows Cargill's house style requirements.

Check for ALL required sections:
1. Executive Answer (≤150 words)
2. Issue Presented (framed as question)
3. Facts (Sanitized)
4. Law & Authorities (with pincites)
5. Analysis (apply law to facts)
6. Conclusion (firm, mirrored to issue)
7. Red-Team (3 counter-arguments with authorities and likelihoods)
8. Risk & Penalty Shield (only if risk > Medium)
9. Follow-Ups & Assumptions
10. Exhibits / Evidence List

Also check:
- Executive Answer word count
- Opinion level stated (Reasonable authority / Substantial authority / More likely than not / Should)
- Citations include pincites
- Red-Team has 3 counter-arguments with likelihood ratings
- Professional tone, active voice

Memo:
{memo}

Return detailed JSON with:
{{
  "all_sections_present": true/false,
  "missing_sections": [],
  "executive_answer_word_count": X,
  "executive_answer_ok": true/false,
  "opinion_level_stated": true/false,
  "opinion_level": "...",
  "red_team_counter_args": X,
  "issues": ["list of specific issues"],
  "overall_assessment": "..."
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON from response
        try:
            result_text = response.content[0].text
            # Extract JSON if wrapped in markdown
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()

            return json.loads(result_text)
        except json.JSONDecodeError:
            return {
                "error": "Could not parse validation results",
                "raw_response": response.content[0].text
            }

    def review_citations(self, memo: str) -> Dict:
        """
        Use Claude to substantively review citations

        Args:
            memo: Memo text with citations

        Returns:
            Dict with citation review
        """
        # Load citation validator prompt if available
        citation_prompt_path = self.prompts_dir / "citation_validator_prompt.md"

        system_prompt = """You are a tax citation expert. Review citations for:
1. Proper format (IRC §, Treas. Reg. §, Bluebook cases)
2. Pincites present
3. Public URLs included where applicable
4. No hallucinated citations
5. Primary sources cited before secondary
6. Treaties include article numbers

Flag any suspicious or improperly formatted citations."""

        if citation_prompt_path.exists():
            with open(citation_prompt_path) as f:
                system_prompt = f.read()

        prompt = f"""Review all citations in this tax memo:

{memo}

Identify:
1. Improperly formatted citations
2. Missing pincites
3. Missing I.R.B. citations for Notices/Rev. Ruls.
4. Cases without Bluebook format
5. Any citations that seem fabricated or questionable
6. URLs without date accessed

Return JSON:
{{
  "total_citations": X,
  "issues": [
    {{
      "citation": "...",
      "issue": "...",
      "severity": "high|medium|low"
    }}
  ],
  "overall_quality": "excellent|good|needs_work|poor"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            result_text = response.content[0].text
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()

            return json.loads(result_text)
        except json.JSONDecodeError:
            return {
                "error": "Could not parse citation review",
                "raw_response": response.content[0].text
            }

    def draft_memo(
        self,
        research_plan: str,
        sanitized_facts: str,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Generate initial memo draft using Claude

        Args:
            research_plan: Approved research plan
            sanitized_facts: Sanitized fact pattern
            additional_context: Any additional context or research

        Returns:
            Draft memo text
        """
        # Load research agent prompt
        agent_prompt_path = self.prompts_dir / "research_agent_prompt.md"

        system_prompt = "You are an international tax expert drafting practitioner-grade tax memos."

        if agent_prompt_path.exists():
            with open(agent_prompt_path) as f:
                system_prompt = f.read()

        context = f"\n\nAdditional Context:\n{additional_context}" if additional_context else ""

        prompt = f"""Draft a comprehensive international tax memo following Cargill's house style.

## Research Plan
{research_plan}

## Sanitized Facts
{sanitized_facts}
{context}

Create a complete memo with ALL required sections:
1. Executive Answer (≤150 words, bottom line first)
2. Issue Presented (as a question)
3. Facts (sanitized bullets)
4. Law & Authorities (primary sources with pincites)
5. Analysis (apply law to facts, address counterpoints)
6. Conclusion (firm, with opinion level)
7. Red-Team (3 counter-arguments with authority and likelihood)
8. Risk & Penalty Shield (only if risk > Medium)
9. Follow-Ups & Assumptions
10. Exhibits / Evidence List

Requirements:
- Use actual IRC sections, regulations, and authorities from research plan
- Include proper citations with pincites
- State opinion level (Reasonable authority / Substantial authority / MLTN / Should)
- Professional tone, active voice, concise
- Mark any uncertain citations as "Unknown—needs manual check"

Return the complete memo in markdown format."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def suggest_improvements(self, memo: str, qa_report: str) -> str:
        """
        Suggest specific improvements based on QA report

        Args:
            memo: Current memo draft
            qa_report: QA report with failed checks

        Returns:
            Specific improvement suggestions
        """
        prompt = f"""Review this tax memo and QA report, then suggest specific improvements.

## QA Report
{qa_report}

## Memo
{memo[:5000]}... [truncated]

Based on the failed QA checks, provide:
1. Specific sections that need work
2. Citation formatting fixes needed
3. Missing required elements
4. Structural improvements

Format as a numbered list of actionable items."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
