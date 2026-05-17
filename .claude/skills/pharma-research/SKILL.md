---
name: pharma-research
description: |
  Runs a structured pharma market research report for a given therapeutic area,
  drug, or competitor. Use when user asks for competitive landscape, pipeline
  analysis, market sizing, payer access, regulatory intelligence, deal activity,
  or launch readiness in life sciences. Trigger with "research [topic]",
  "competitive landscape for [drug/TA]", "pharma market report", "what is the
  market for [indication]", or "analyse [competitor]".
version: 1.0.0
allowed-tools: "Write, Read, Glob"
context: fork
agent: general-purpose
argument-hint: "[therapeutic area or drug name]"
tags: [pharma, life-sciences, market-research, competitive-intelligence]
---

# Pharma Market Research Skill

## Purpose
Produce a structured, consulting-grade pharma market research report for
`$ARGUMENTS`. Each section is concise, evidence-backed, and written for a
life science consulting audience.

## Output
Save the final report to `output/pharma-research-<slug>-<YYYY-MM-DD>.md`
where `<slug>` is a lowercase hyphenated version of `$ARGUMENTS`.

## Report Structure

Run all 6 sections below in order. Do not skip any.

---

### 1. MARKET OVERVIEW
- Disease/indication definition and patient population (global + key markets)
- Total Addressable Market (TAM) in USD — current year and 5-year projection
- Key geographies: US, EU5, Japan, emerging markets
- Growth drivers and headwinds

### 2. COMPETITIVE LANDSCAPE
For each major approved and late-stage asset in this space:

| Asset | Company | MOA | Stage | Approval Date | Key Markets | Indication |
|---|---|---|---|---|---|---|

- Identify market leader and basis for leadership (share, label breadth, pricing)
- Note any biosimilar or generic threat timeline

### 3. PIPELINE INTELLIGENCE
- Phase 2 and Phase 3 assets not yet approved
- Mechanism of action differentiation vs approved agents
- Expected readout / PDUFA dates in next 24 months
- Any breakthrough therapy, fast track, or orphan designations

### 4. REGULATORY INTELLIGENCE
- Recent FDA / EMA approvals or complete response letters (CRLs) in this space
- Label trends: any expansions, restrictions, or REMS requirements
- Precedent-setting decisions relevant to new entrants

### 5. PAYER & MARKET ACCESS
- Formulary positioning of leading agents (preferred / non-preferred / PA required)
- Reimbursement landscape: Medicare Part B vs D, EU HTA outcomes
- Pricing benchmarks: WAC, net price estimates where available
- Access barriers: step therapy, prior auth prevalence

### 6. DEALS & BUSINESS DEVELOPMENT
- Licensing, co-promotion, and M&A activity in last 24 months
- Deal structures: upfront, milestones, royalties where disclosed
- Strategic implications for market entrants

---

## Output Format Rules
- Use the exact section headers above
- Each section: 3–6 bullet points or a table — no long prose paragraphs
- Flag data gaps explicitly: write `[Data unavailable — verify via IQVIA/Clarivate]`
- End with a one-paragraph **Strategic Implication** summary for a consulting client

## After Saving
Write one log line to `logs/<today>.log`:
```
[HH:MM:SS] INFO     | SKILL        | pharma-research completed  topic: $ARGUMENTS  file: output/pharma-research-<slug>-<date>.md
```