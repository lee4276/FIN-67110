"""Four model roles on the verified seven-step SEC data desk.

The human report audit remains a separate task. This program does not sign it.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from desk import DATA_ROOT, ROOT, load_env


PARTS = [
    "Overview",
    "Market Positioning and Growth Outlook",
    "Valuation Insights",
    "Future Developments and Strategic Recommendations",
    "Investment Recommendation",
]

RESEARCH_INSTRUCTIONS = """You are the Research Analyst in an equity research desk. Use only the supplied 10-K and earnings release excerpts. Write Markdown sections headed exactly '## Overview', '## Market Positioning and Growth Outlook', and '## Future Developments and Strategic Recommendations'. Discuss business model, competitive position, catalysts, risks, and recent developments only where supported. Every factual claim needs a short quote and a source filename with line number. Do not make up facts, dates, numbers, or external news. State when evidence is insufficient."""

FINANCIAL_INSTRUCTIONS = """You are the Financial Analyst. Use only the supplied XBRL facts, code-calculated ratios, filing excerpts, release lines, and peer facts. Write one Markdown section headed exactly '## Valuation Insights'. Include a Markdown table for all 11 numbered core claims. For each claim, state the number, fiscal or quarter period, definition, and evidence: a 10-K or release line, or XBRL tag, period end, and accession. For claims 2, 3, 6, 7, 8, and 10, copy the supplied arithmetic. Do not calculate any number yourself. Do not present net sales as total revenue. For claim 4 use net income attributable to the company. For 5 and 11 use GAAP diluted EPS. If a claim is not supported by the supplied data, state 'not established' rather than guessing. Add a peer table with each peer's own fiscal year, total revenue, operating income, tag, accession, and operating margin on operating income divided by total revenue. Include P/E only when a price and date are supplied. Every other number also needs a source and period. Do not add numbers that are absent from the context."""

ADVISOR_INSTRUCTIONS = """You are the Investment Advisor. You receive only the Research Analyst and Financial Analyst outputs, not raw filings or outside data. Write one Markdown section headed exactly '## Investment Recommendation'. State Buy, Hold, or Sell and one report number that drives the thesis. Use only numbers and facts present in the two outputs, with their cited source. If the evidence does not support a directional call, choose Hold and explain the limit. Do not invent a price target, return, or catalyst."""

MANAGER_INSTRUCTIONS = """You are the Strategy Manager. Compile the supplied role outputs into a single Markdown report. Preserve every numerical figure, source reference, definition, and arithmetic exactly. Use exactly these five level-two headings, in order: Overview; Market Positioning and Growth Outlook; Valuation Insights; Future Developments and Strategic Recommendations; Investment Recommendation. Keep the Financial Analyst's 11-row core-claims table and peer table. Remove contradictory prose only when a source supports the correction; otherwise state the conflict. Do not add facts or numbers. The program adds the filing-accession first line and the run-time second line."""


def lines_with_numbers(path: Path, start: int, count: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(f"{path.name}:L{i + 1}: {lines[i]}" for i in range(start, min(start + count, len(lines))))


def section(path: Path, patterns: list[str], count: int, fallback: int = 100, prefer_upper: bool = False) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    for pattern in patterns:
        matches = [i for i, line in enumerate(lines) if i >= fallback and re.search(pattern, line, re.I)]
        if matches:
            if prefer_upper:
                upper_matches = [i for i in matches if lines[i] == lines[i].upper()]
                if upper_matches:
                    return lines_with_numbers(path, upper_matches[0], count)
            return lines_with_numbers(path, matches[0], count)
    return "NO MATCHING SECTION FOUND"


def make_context(run: dict, folder: Path) -> dict:
    ten_k = folder / run["documents"]["10-K"]["path"]
    release = folder / run["documents"]["EX-99.1"]["path"]
    research = {
        "company": run["company"],
        "10_K_accession": run["filings"]["10-K"]["accessionNumber"],
        "earnings_8_K_accession": run["filings"]["8-K"]["accessionNumber"],
        "business_excerpt": section(ten_k, [r"^Item\s*1\s*[—.-]\s*Business", r"^Business\s*$"], 125),
        "management_discussion_excerpt": section(ten_k, [r"^Item\s*7\s*[—.-]\s*Management", r"^Management.s Discussion and Analysis"], 125),
        "earnings_release_excerpt": lines_with_numbers(release, 0, 100),
    }
    financial = {
        "company": run["company"],
        "filings": run["filings"],
        "facts": run["facts"],
        "ratios_calculated_in_code": run["ratios"],
        "quarter_release_lines": run["release_lines"],
        "price_and_date": {"price": run["input"]["price"], "date": run["input"].get("price_date")},
        "income_statement_excerpt": section(ten_k, [r"^CONSOLIDATED STATEMENTS? OF (INCOME|OPERATIONS)", r"^STATEMENTS? OF (INCOME|OPERATIONS)"], 80, prefer_upper=True),
        "balance_sheet_excerpt": section(ten_k, [r"^CONSOLIDATED BALANCE SHEETS?", r"^BALANCE SHEETS?"], 85, prefer_upper=True),
        "cash_flow_excerpt": section(ten_k, [r"^CONSOLIDATED STATEMENTS? OF CASH FLOWS?", r"^STATEMENTS? OF CASH FLOWS?"], 90, prefer_upper=True),
        "release_excerpt": lines_with_numbers(release, 0, 140),
        "peers": {ticker: {"company": peer["company"], "fiscal_year_end": peer["facts"]["fiscal_year_end"], "10_K_accession": peer["facts"]["filing_accession"], "revenue": peer["facts"]["concepts"]["total_revenue"]["current"], "operating_income": peer["facts"]["concepts"]["operating_income"]["current"], "operating_margin_calculated_in_code": peer["operating_margin"]} for ticker, peer in run.get("peers", {}).items()},
    }
    return {"research": research, "financial": financial}


def payload(task: str, context: dict, expected_output: str) -> str:
    return json.dumps({"task": task, "context": context, "expected_output": expected_output}, ensure_ascii=False)


def model_call(client, model: str, instructions: str, task: str, context: dict, expected_output: str) -> str:
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=payload(task, context, expected_output),
        store=False,
    )
    output = response.output_text.strip()
    if not output:
        raise RuntimeError(f"{task} returned no text.")
    return output


def missing_parts(text: str, headings: list[str]) -> list[str]:
    return [heading for heading in headings if not re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text)]


def run_role(client, model: str, name: str, instructions: str, task: str, context: dict, headings: list[str]) -> str:
    print(name, flush=True)
    output = model_call(client, model, instructions, task, context, "Markdown with the required heading(s), source references, and no unsupported figures")
    missing = missing_parts(output, headings)
    if name == "Financial Analyst":
        missing.extend(str(i) for i in range(1, 12) if not re.search(rf"(?m)^\|\s*{i}\s*\|", output))
    if missing:
        print(f"  Revision requested once for missing items: {', '.join(missing)}", flush=True)
        context = {"original_context": context, "draft": output, "missing_items": missing}
        output = model_call(client, model, instructions, f"Revise your {name} draft once. Supply the missing headings or rows. Use 'not established' if a number is unavailable.", context, "Complete revised Markdown")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SEC data steps and four OpenAI report roles")
    parser.add_argument("ticker")
    parser.add_argument("--peers", default="")
    parser.add_argument("--price", type=float)
    parser.add_argument("--price-date", help="Date of the close supplied with --price")
    parser.add_argument("--model", default="gpt-6.1-sol", help="OpenAI model available to your API project")
    parser.add_argument("--dry-run", action="store_true", help="Build and save role inputs without model calls")
    args = parser.parse_args()
    if args.price_date:
        date.fromisoformat(args.price_date)
    load_env(ROOT / ".env")
    existing = set(DATA_ROOT.iterdir()) if DATA_ROOT.exists() else set()
    command = [sys.executable, str(ROOT / "desk.py"), args.ticker]
    if args.peers:
        command.extend(["--peers", args.peers])
    if args.price is not None:
        command.extend(["--price", str(args.price)])
    if args.price_date:
        command.extend(["--price-date", args.price_date])
    subprocess.run(command, cwd=ROOT, check=True)
    created = set(DATA_ROOT.iterdir()) - existing
    if len(created) != 1:
        raise RuntimeError("Could not identify the single new desk run folder.")
    folder = created.pop()
    run = json.loads((folder / "facts.json").read_text(encoding="utf-8"))
    contexts = make_context(run, folder)
    (folder / "role_inputs.json").write_text(json.dumps(contexts, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.dry_run:
        print(f"Saved role inputs without model calls: {folder / 'role_inputs.json'}")
        return 0
    api_key = os.getenv("API_KEY", "")
    if not api_key.startswith("sk-"):
        raise ValueError("API_KEY in .env does not look like an OpenAI developer API key. The SEC data run was saved; no model call was made.")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("Install the Lab 03 dependency with: python -m pip install openai") from error
    client = OpenAI(api_key=api_key)
    research = run_role(client, args.model, "Research Analyst", RESEARCH_INSTRUCTIONS, "Analyze the company from the supplied filings", contexts["research"], [PARTS[0], PARTS[1], PARTS[3]])
    finance = run_role(client, args.model, "Financial Analyst", FINANCIAL_INSTRUCTIONS, "State and source the 11 core claims, ratios, quarter, and peers", contexts["financial"], [PARTS[2]])
    advisor = run_role(client, args.model, "Investment Advisor", ADVISOR_INSTRUCTIONS, "Write a supported investment thesis and recommendation", {"research_analyst": research, "financial_analyst": finance}, [PARTS[4]])
    print("Strategy Manager", flush=True)
    role_outputs = {"Research Analyst": research, "Financial Analyst": finance, "Investment Advisor": advisor}
    manager_context = {"role_outputs": role_outputs, "required_sections": PARTS}
    report = model_call(client, args.model, MANAGER_INSTRUCTIONS, "Check and compile the five-part report", manager_context, "One five-part Markdown report")
    missing = missing_parts(report, PARTS)
    if missing:
        print(f"  Revision requested once for missing sections: {', '.join(missing)}", flush=True)
        report = model_call(client, args.model, MANAGER_INSTRUCTIONS, "Revise the compiled report once to restore missing sections", {**manager_context, "draft": report, "missing_sections": missing}, "One complete five-part Markdown report")
    missing = missing_parts(report, PARTS)
    if missing:
        raise RuntimeError(f"Manager report remains incomplete: {', '.join(missing)}")
    first_line = "Filings read: " + "; ".join(f"{form} {item['accessionNumber']}" for form, item in run["filings"].items()) + f"; earnings release EX-99.1 from 8-K {run['filings']['8-K']['accessionNumber']}"
    final = first_line + "\n" + f"Run time: {run['run_time']}" + "\n\n" + report.strip() + "\n"
    (folder / "role_outputs.json").write_text(json.dumps(role_outputs, indent=2, ensure_ascii=False), encoding="utf-8")
    path = folder / "report.md"
    path.write_text(final, encoding="utf-8")
    print(f"Saved report: {path}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
