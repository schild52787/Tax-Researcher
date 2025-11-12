
# Cargill International Tax — House Style & Citation Guide

> **Purpose.** Ensure every memo looks, reads, and cites the same way, with verifiable sources and practitioner‑grade precision. Use with the **Canvas memo template** and the **QA Checklist**. When using GPT‑5 Enterprise, these rules are mandatory.

---

## 1) Document anatomy (match the Canvas template)
1. **Executive Answer (≤150 words)** — one paragraph, bottom line first. No citations here unless critical.
2. **Issue Presented** — framed as a question.
3. **Facts (Sanitized)** — concise bullets; strip identifiers and confidential figures unless essential.
4. **Law & Authorities (with pincites)** — **primary sources first**; list in logical order.
5. **Analysis (apply law to facts)** — organized by sub‑issue; address counterpoints inline.
6. **Conclusion** — firm and mirrored to the Issue.
7. **Red‑Team (Counter‑Arguments)** — top 3, each with authority and likelihood.
8. **Risk & Penalty Shield** — **include only when overall risk > Medium** (see §7).
9. **Follow‑Ups & Assumptions**
10. **Exhibits / Evidence List**
11. **QA Checklist** — tick before delivery.

---

## 2) Tone & voice
- Professional, precise, and concise; define terms; prefer **plain English**.
- Avoid unjustified hedging (“appears,” “may”) unless tied to a concrete uncertainty.
- Use active voice; aim for ≤ ~25 words per sentence.

---

## 3) Formatting & conventions
- **Headings:** H2 for top‑level; H3/H4 sparingly.
- **Numbers:** Use non‑rounded figures if decision‑relevant; otherwise round. Footnote exchange rates.
- **Dates:** ISO in workpapers (e.g., 2025‑11‑12); narrative may use “November 12, 2025.”
- **Currency:** ISO codes (USD, EUR) and thousands separators (1,234,567).
- **Tables:** Prefer simple 5–7 column tables. Put cites in a “Cite” column when helpful.
- **Cross‑references:** “See §4.2, infra.” Link when practical.
- **Exhibits:** Label **Ex. A**, **Ex. B**, etc., with descriptors (“Ex. C — IC Services Agreement §7.3”).

---

## 4) Citation policy (general)
- Cite **public, verifiable sources** wherever possible (IRS.gov, OECD.org, EUR‑Lex, official gazettes, law.cornell.edu for reference text).
- **Primary authority first.** Label secondary sources clearly as **(secondary)**.
- Use **inline citations** at the end of the sentence they support; include **pincites**.
- If a cite cannot be verified quickly, write **“Unknown—needs manual check.”**
- If using unofficial translations, add: “Unofficial translation; confirm against official.”
- **No AI sources.** Do **not** cite AI output; cite the underlying authority the AI located.
- **Archive web sources.** Include an archived URL or “on file” copy reference and **date accessed**.

---

## 5) Specific citation formats & examples
### 5.1 U.S. statutes & regulations
- **Statutes:** `IRC § 951A(c)(2)(A)(i) (2017).`
- **Regs:** `Treas. Reg. § 1.951A-2(b)(2)(i).`
- **IRS guidance:** `Notice 2020-69, 2020-40 I.R.B. 600.`; `Rev. Rul. 2019-01, 2019-02 I.R.B. 123.`
- **Chief Counsel Advice (non‑precedential):** `CCA 202042015 (Oct. 16, 2020) (non‑precedential).`

### 5.2 Courts (Bluebook required)
- *Case name* **italicized**, reporter, page, court, year, **with pincite**.
- Examples: `*WH Holdings, LLC v. United States*, 601 F.3d 1319, 1323 (Fed. Cir. 2010).`; `*Bausch & Lomb Inc. v. Comm’r*, 92 T.C. 525, 532 (1989), aff’d, 933 F.2d 1084 (2d Cir. 1991).`

### 5.3 OECD / Pillar Two
- **Model & Commentary:** `OECD Model Tax Convention on Income and on Capital (Condensed Version 2017), Art. 5(5), Commentary ¶32.`
- **Administrative Guidance:** `OECD/G20 Inclusive Framework on BEPS, Pillar Two Administrative Guidance (updated [Month YYYY]) § X.Y.`

### 5.4 Treaties & Technical Explanations
- **Treaty text:** `Convention Between the Government of the United States of America and the Government of [Country] for the Avoidance of Double Taxation, Art. 10(2)(a) (signed [Date]).`
- **LOB / BO references:** `id. Art. 22 (LOB); Technical Explanation at 12–14.`

### 5.5 Local law (outside U.S.)
- Use official citation conventions when applicable (e.g., Canada: `ITA s. 212(1)(d)`; UK: `CTA 2009, s. 130`; EU: `Council Directive (EU) 2016/1164 (ATAD), art. 7`).

### 5.6 Secondary sources (must be labeled)
- `KPMG Insights (secondary), “Title,” (Date), URL.`
- `Law firm client alert (secondary), “Title,” (Date), URL.`

---

## 6) Shepardization / case validation (manual)
- For every **case** that materially affects the conclusion, run **Shepard’s (Lexis)** or **BCite (Bloomberg Law)**.
- Record: (i) treatment flags, (ii) citing references that change scope, (iii) subsequent history (aff’d, rev’d, vacated, etc.).
- Update the citation to reflect subsequent history where material and attach screenshot/notes **on file**.
- If validation cannot be completed before delivery, mark the citation **“Unknown—needs manual check.”**

---

## 7) Risk ratings & when to include penalty shield
Use the **standard opinion scale** in conclusions and the risk section:
- **Reasonable authority (~20–30%)**
- **Substantial authority (~35–45%)**
- **More likely than not (>50%)**
- **Should (~70–80%)**

Include the **Risk & Penalty Shield** section **only** when overall risk > Medium; tie to documentation (reasonable cause, substantial authority, contemporaneous records).

---

## 8) Red‑team presentation
- Present **3 strongest counter‑arguments**, each with: (1) concise thesis, (2) authority cite, (3) likelihood (Low/Med/High), (4) mitigation note.

---

## 9) Data & calculations
- State formulas in text before results (e.g., “GloBE ETR = Covered Taxes / GloBE Income”). Note assumptions, rounding, currency codes. Provide CSV/Excel where appropriate.

---

## 10) Confidentiality & hygiene
- Avoid direct identifiers; use placeholders (e.g., “[Cargill Entity A]”). Verify redactions.
- File naming: `YYYY-MM-DD_Country_Matter_Deliverable_v01.docx` (increment versions).
- Use only **enterprise‑approved** AI tools (ChatGPT Enterprise, Microsoft 365 Copilot). Do not input confidential data into public or unauthorized tools.

---

## 11) Embedded AI prompt (copy/paste when using GPT‑5)
> **System/Assistant Guidance for Drafting Memos**  
> - Follow Cargill’s **House Style & Citation Guide** and **QA Checklist** exactly.  
> - **Never invent** authorities, quotes, or facts. If uncertain or unverifiable, write **“Unknown—needs manual check.”**  
> - Cite **primary** law first (statutes, regulations, IRB, cases, treaties, OECD) with **pincites** and public links where available; flag **secondary** sources.  
> - Use **live web browsing** to retrieve current law and provide public URLs and **date accessed**; **do not** cite AI output.  
> - For **cases**, add a placeholder: “(Shepardization/BCite pending).”  
> - Use the **Opinion Level Rubric** language in the Conclusion (Reasonable authority / Substantial authority / MLTN / Should) and include **Risk & Penalty Shield** **only if** overall risk > Medium.  
> - Keep the Executive Answer ≤150 words; maintain professional, concise tone; active voice.  
