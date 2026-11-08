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
    from verifier import _figures
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
    names = (
        "Annual total revenue", "Annual revenue growth", "Annual operating income and margin",
        "Annual net income attributable to company", "Annual GAAP diluted EPS",
        "Return on average equity", "Debt to equity including current debt", "Free cash flow",
        "Latest-quarter total revenue", "Latest-quarter year-over-year total revenue growth",
        "Latest-quarter GAAP diluted EPS",
    )
    figures = _figures({**run, "_folder": str(folder)})
    financial["core_claims_display"] = [
        {"number": n, "claim": names[n - 1], "display": (
            "not established" if figures[n][0] is None else
            f"{figures[n][0]:.2f}%" if figures[n][1] == "%" else
            f"${figures[n][0]:.3f} billion" if figures[n][1] == "billion USD" else
            f"${figures[n][0]:.2f} per diluted share"
        ), "source": figures[n][2]} for n in range(1, 12)
    ]
    margin = run["ratios"]["operating_margin"]["value"]
    financial["core_claims_display"][2]["operating_margin"] = "not established" if margin is None else f"{margin * 100:.2f}%"
    return {"research": research, "financial": financial}


def payload(task: str, context: dict, expected_output: str) -> str:
    return json.dumps({"task": task, "context": context, "expected_output": expected_output}, ensure_ascii=False)


def model_call(client, model: str, instructions: str, task: str, context: dict, expected_output: str) -> str:
    try:
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=payload(task, context, expected_output),
            store=False,
        )
    except Exception as error:
        status = getattr(error, "status_code", None)
        if status == 401:
            raise RuntimeError("OpenAI rejected API_KEY in .env (401). Check the developer key; no key text is shown.") from None
        if status is not None:
            code = getattr(error, "code", None)
            body = getattr(error, "body", None)
            if code is None and isinstance(body, dict):
                detail = body.get("error")
                code = body.get("code") or (detail.get("code") if isinstance(detail, dict) else None)
            if code is None and getattr(error, "response", None) is not None:
                try:
                    detail = error.response.json().get("error", {})
                    code = detail.get("code") if isinstance(detail, dict) else None
                except (ValueError, AttributeError):
                    pass
            suffix = f" ({code})" if code in {"insufficient_quota", "rate_limit_exceeded", "model_not_found"} else ""
            raise RuntimeError(f"OpenAI API returned HTTP {status}{suffix} for {task}. No provider error text is shown.") from None
        raise
    output = response.output_text.strip()
    if not output:
        raise RuntimeError(f"{task} returned no text.")
    return output


def missing_parts(text: str, headings: list[str]) -> list[str]:
    return [heading for heading in headings if not re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text)]


def main() -> int:
    from team import main as team_main
    return team_main()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
