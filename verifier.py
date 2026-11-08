"""Evidence checks for the eleven Lab 03 core claims; human checks stay separate."""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import re


def _fact(run: dict, name: str, period: str = "current") -> Decimal | None:
    row = run["facts"]["concepts"][name][period]
    return Decimal(str(row["value"])) if row else None


def _number(text: str) -> Decimal | None:
    match = re.search(r"\$?\s*(-?\d[\d,]*(?:\.\d+)?)", text)
    return Decimal(match.group(1).replace(",", "")) if match else None


def _near(display: Decimal | None, expected: Decimal | None, raw: str) -> bool:
    if display is None or expected is None:
        return False
    match = re.search(r"-?\d[\d,]*(?:\.(\d+))?", raw)
    places = len(match.group(1)) if match and match.group(1) else 0
    tolerance = max(Decimal("0.5") * (Decimal(10) ** -places), Decimal("0.000000001"))
    return abs(display - expected) <= tolerance


def _rows(report: str) -> dict[int, str]:
    found = {}
    for line in report.splitlines():
        match = re.match(r"^\|\s*(\d{1,2})(?:\.[^|]*)?\s*\|", line)
        if match and 1 <= int(match.group(1)) <= 11:
            found[int(match.group(1))] = line
    return found


def _figures(run: dict) -> dict[int, tuple[Decimal | None, str, str]]:
    billion = Decimal(1_000_000_000)
    pct = Decimal(100)
    revenue = _fact(run, "total_revenue")
    prior_revenue = _fact(run, "total_revenue", "prior")
    operating = _fact(run, "operating_income")
    income = _fact(run, "net_income")
    equity = _fact(run, "stockholders_equity")
    prior_equity = _fact(run, "stockholders_equity", "prior")
    debt = _fact(run, "long_term_debt_including_current")
    if debt is None:
        long_debt = _fact(run, "long_term_debt_noncurrent")
        current_debt = _fact(run, "long_term_debt_current")
        debt = long_debt + current_debt if long_debt is not None and current_debt is not None else None
    cfo = _fact(run, "cash_from_operations")
    capex = _fact(run, "property_equipment_additions")
    q = run.get("release_lines", {}).get("quarter_revenue_growth") or {}
    q_current = Decimal(str(q["current"])) if q.get("current") is not None else None
    q_prior = Decimal(str(q["prior"])) if q.get("prior") is not None else None
    release = Path(run["_folder"]) / run["documents"]["EX-99.1"]["path"]
    release_text = release.read_text(encoding="utf-8")
    eps_match = re.search(r"\$(\d+(?:\.\d+)?)\s+per diluted share", release_text, re.I)
    quarter_eps = Decimal(eps_match.group(1)) if eps_match else None
    annual_end = run["facts"]["fiscal_year_end"]
    prior_end = run["facts"]["prior_year_end"]
    acc = run["facts"]["filing_accession"]
    annual = f"10-K {acc}, fiscal years ended {annual_end} and {prior_end}"
    release_source = f"EX-99.1 {run['filings']['8-K']['accessionNumber']}"
    def div(a, b):
        return a / b if a is not None and b not in (None, 0) else None
    return {
        1: (div(revenue, billion), "billion USD", annual + "; total revenue XBRL"),
        2: (div(revenue - prior_revenue, prior_revenue) * pct if revenue is not None and prior_revenue else None, "%", annual + "; (current / prior - 1) × 100"),
        3: (div(operating, billion), "billion USD", annual + "; operating income XBRL"),
        4: (div(income, billion), "billion USD", annual + "; net income XBRL"),
        5: (_fact(run, "diluted_eps"), "USD per diluted share", annual + "; EarningsPerShareDiluted"),
        6: (div(income, (equity + prior_equity) / 2) * pct if income is not None and equity is not None and prior_equity is not None else None, "%", annual + "; net income / average equity × 100"),
        7: (div(debt, equity) * pct if debt is not None and equity is not None else None, "%", annual + "; debt including current portion / equity × 100"),
        8: (div(cfo - capex, billion) if cfo is not None and capex is not None else None, "billion USD", annual + "; operating cash flow - property additions"),
        9: (div(q_current, Decimal(1000)), "billion USD", release_source + f"; line {q.get('source_line', '?')}; quarter revenue"),
        10: (div(q_current - q_prior, q_prior) * pct if q_current is not None and q_prior else None, "%", release_source + f"; line {q.get('source_line', '?')}; (current / prior - 1) × 100"),
        11: (quarter_eps, "USD per diluted share", release_source + "; release narrative, latest quarter"),
    }


def _reported_value(row: str, claim: int) -> tuple[Decimal | None, str]:
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    body = cells[1] if len(cells) > 1 else ""
    if claim in (2, 6, 7, 10):
        match = re.search(r"(-?\d[\d,]*(?:\.\d+)?)\s*%", body)
        if not match:
            match = re.search(r":\s*\*{0,2}(-?\d[\d,]*(?:\.\d+)?)", body)
    elif claim == 3:
        match = re.search(r"\$\s*(-?\d[\d,]*(?:\.\d+)?)", body)
    else:
        match = re.search(r"\$\s*(-?\d[\d,]*(?:\.\d+)?)", body)
        if not match:
            match = re.search(r"(-?\d[\d,]*(?:\.\d+)?)", body)
    if not match:
        return None, ""
    raw = match.group(1)
    value = Decimal(raw.replace(",", ""))
    if claim in (1, 3, 4, 8, 9) and value >= 1_000_000:
        value /= Decimal(1_000_000_000)
    if claim in (2, 6, 7, 10) and "%" not in body and abs(value) < 1:
        value *= 100
    return value, raw


def _claim_label_ok(row: str, claim: int) -> bool:
    cells = row.strip().strip("|").split("|")
    body = (cells[0] + " " + cells[1]).lower()
    required = {
        1: ("revenue",), 2: ("revenue", "growth"),
        3: ("operating", "income", "margin"), 4: ("net income",),
        5: ("diluted", "eps"), 6: ("return", "average", "equity"),
        7: ("debt", "equity"), 8: ("free cash flow",),
        9: ("quarter", "revenue"), 10: ("quarter", "revenue", "growth"),
        11: ("quarter", "diluted", "eps"),
    }
    return all(word in body for word in required[claim])


def _source_line_check(row: str, folder: Path) -> tuple[bool, str]:
    # If a row quotes source text, that text must occur in the cited saved line.
    quotes = re.findall(r'["“]([^"”]{4,})["”]', row)
    if not quotes:
        return True, "No literal source quotation in row"
    refs = _cited_lines(row, folder)
    if not refs:
        return False, "Quoted source text has no filing and line reference"
    normal = lambda s: re.sub(r"[^a-z0-9.$]+", " ", s.lower()).strip()
    support = all(any(normal(quote) in normal(text) for _, _, text in refs) for quote in quotes)
    return support, "; ".join(f"{name}:L{number}: {text}" for name, number, text in refs)


def _cited_lines(row: str, folder: Path) -> list[tuple[str, int, str]]:
    source = "EX-99.1" if re.search(r"EX-99\.1|Exhibit\s*99\.1|\brelease\b", row, re.I) and not re.search(r"10-K", row, re.I) else "10-K"
    files = list(folder.glob(f"{source}_*.txt"))
    if len(files) != 1:
        return []
    lines = files[0].read_text(encoding="utf-8").splitlines()
    numbers = set()
    for match in re.finditer(r"\b(?:line\s*|L)(\d+)(?:\s*[-–]\s*L?(\d+))?", row, re.I):
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else start
        numbers.update(range(start, min(end, start + 20) + 1))
    return [(files[0].name, n, lines[n - 1]) for n in sorted(numbers) if 1 <= n <= len(lines)]


def _quoted_arithmetic(row: str, claim: int, reported: Decimal | None) -> tuple[bool, str]:
    body = row.strip().strip("|").split("|")[1]
    amounts = [Decimal(x.replace(",", "")) for x in re.findall(r"\$\s*(\d[\d,]*(?:\.\d+)?)", body)]
    formula = re.search(r"`([^`]*[/+\-][^`]*)`", row)
    formula_numbers = [Decimal(x) for x in re.findall(r"(?<![\w.])\d+(?:\.\d+)?", formula.group(1))] if formula else []
    result = None
    if claim == 2 and len(amounts) >= 2 and amounts[1]:
        result = (amounts[0] / amounts[1] - 1) * 100
    elif claim == 2 and len(formula_numbers) >= 3 and formula_numbers[2]:
        result = (formula_numbers[0] - formula_numbers[1]) / formula_numbers[2] * 100
    elif claim == 3 and len(amounts) >= 2 and amounts[-1]:
        result = amounts[-2] / amounts[-1] * 100
    elif claim == 3 and len(formula_numbers) >= 2 and formula_numbers[1]:
        result = formula_numbers[0] / formula_numbers[1] * 100
    if claim == 3:
        percent = re.search(r"(\d+(?:\.\d+)?)\s*%", body)
        reported = Decimal(percent.group(1)) if percent else None
    if claim == 6 and len(amounts) >= 3 and amounts[1] + amounts[2]:
        result = amounts[0] / ((amounts[1] + amounts[2]) / 2) * 100
    elif claim == 6 and len(formula_numbers) >= 3 and formula_numbers[1] + formula_numbers[2]:
        result = formula_numbers[0] / ((formula_numbers[1] + formula_numbers[2]) / 2) * 100
    if claim == 7 and len(amounts) >= 3 and amounts[2]:
        result = (amounts[0] + amounts[1]) / amounts[2] * 100
    elif claim == 7 and len(formula_numbers) >= 2 and formula_numbers[-1]:
        result = formula_numbers[0] / formula_numbers[-1] * 100
    if claim == 8 and len(amounts) >= 3:
        result = amounts[1] - amounts[2]
    elif claim == 8 and len(formula_numbers) >= 2:
        result = formula_numbers[0] - formula_numbers[1]
        if result >= 1_000_000:
            result /= Decimal(1_000_000_000)
    if claim == 10 and len(amounts) >= 2 and amounts[1]:
        result = (amounts[0] / amounts[1] - 1) * 100
    elif claim == 10 and len(formula_numbers) >= 2 and formula_numbers[1]:
        result = (formula_numbers[0] / formula_numbers[1] - 1) * 100
    if result is None:
        return False, "Quoted inputs or definition are missing"
    match = re.search(r"\d+(?:\.(\d+))?\s*%", body) if claim != 8 else re.search(r"\$\s*\d+(?:\.(\d+))?", body)
    raw = match.group(0) if match else str(reported or "")
    return _near(reported, result, raw), f"Quoted-input arithmetic gives {result}{'%' if claim != 8 else ' billion USD'}"


def _direct_line_value(row: str, claim: int, expected: Decimal | None, folder: Path) -> tuple[bool, str]:
    if claim not in (1, 3, 4, 5, 9, 11) or expected is None:
        return True, ""
    refs = _cited_lines(row, folder)
    if not refs:
        return True, "XBRL source used without a cited text line"
    token = f"{expected:f}" if claim in (5, 11) else f"{int(expected * 1000):,}"
    return any(token in line for _, _, line in refs), "; ".join(f"{name}:L{n}: {line}" for name, n, line in refs)


def _xbrl_metadata(row: str, claim: int, run: dict) -> tuple[bool, str]:
    names = {
        1: ("total_revenue",), 2: ("total_revenue",), 3: ("operating_income", "total_revenue"),
        4: ("net_income",), 5: ("diluted_eps",),
        6: ("net_income", "stockholders_equity"),
        7: ("long_term_debt_including_current", "long_term_debt_noncurrent", "long_term_debt_current", "stockholders_equity"),
        8: ("cash_from_operations", "property_equipment_additions"),
    }.get(claim, ())
    selected = {item["tag"] for name in names for item in run["facts"]["concepts"][name].values() if item}
    cited = {tag for tag in re.findall(r"`([A-Za-z][A-Za-z0-9_]+)`", row)
             if "_" not in tag and any(ch.isupper() for ch in tag[1:])}
    if cited and not cited.issubset(selected):
        return False, f"Cited XBRL tag {sorted(cited - selected)} is not the selected saved fact tag"
    dates = set(re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", row))
    allowed = {run["facts"]["fiscal_year_end"], run["facts"]["prior_year_end"]}
    if claim in (3, 4, 5, 7, 8):
        allowed = {run["facts"]["fiscal_year_end"]}
    if claim in (1, 3, 4, 5, 6, 7, 8) and dates and not dates.issubset(allowed):
        return False, f"Cited period {sorted(dates - allowed)} does not match saved XBRL period"
    return True, "Cited XBRL tag and period match selected saved facts where stated"


def check_report(report: str, saved_run: Path) -> list[dict]:
    run = json.loads((saved_run / "facts.json").read_text(encoding="utf-8"))
    run["_folder"] = str(saved_run)
    expected = _figures(run)
    rows = _rows(report)
    marks = []
    for claim in range(1, 12):
        value, unit, source = expected[claim]
        row = rows.get(claim)
        if row is None:
            marks.append({"id": str(claim), "mark": "unsupported", "reason": "Core claim row missing",
                          "correction": f"{value} {unit}; {source}" if value is not None else None})
            continue
        reported, raw = _reported_value(row, claim)
        label_ok = _claim_label_ok(row, claim)
        quote_ok, quote_evidence = _source_line_check(row, saved_run)
        arithmetic_ok, arithmetic_evidence = (True, "")
        if claim in (2, 3, 6, 7, 8, 10):
            arithmetic_ok, arithmetic_evidence = _quoted_arithmetic(row, claim, reported)
        definition_ok = claim != 6 or bool(re.search(r"average\s+equity|average\s+shareholders", row, re.I))
        line_ok, line_evidence = _direct_line_value(row, claim, value, saved_run)
        metadata_ok, metadata_evidence = _xbrl_metadata(row, claim, run)
        source_ok = bool(re.search(r"10-K|EX-99\.1|Exhibit\s*99\.1|\brelease\b|XBRL|\bClaim\s+1\b|"
                                   r"NetIncomeLoss|StockholdersEquity|LongTermDebt|"
                                   r"NetCashProvidedByUsedInOperatingActivities|PaymentsToAcquirePropertyPlantAndEquipment", row, re.I))
        if value is None:
            mark, reason = "unsupported", "Saved evidence does not establish this figure"
        elif not label_ok:
            mark, reason = "unsupported", "Core claim row has the wrong definition or omits a required measure"
        elif reported is None:
            mark, reason = "unsupported", "No report number found"
        elif not source_ok:
            mark, reason = "unsupported", "No filing line, XBRL tag, or sourced input claim in this row"
        elif not metadata_ok:
            mark, reason = "unsupported", metadata_evidence
        elif not _near(reported, value, raw):
            mark, reason = "wrong", f"Reported {reported} {unit}; saved evidence gives {value} {unit}"
        elif not quote_ok:
            mark, reason = "wrong", "Quoted source text does not match the saved filing line"
        elif not line_ok:
            mark, reason = "wrong", "Cited saved filing line does not contain the reported source value"
        elif not definition_ok:
            mark, reason = "unsupported", "Return on equity does not state an average-equity definition"
        elif not arithmetic_ok:
            mark, reason = "wrong", arithmetic_evidence
        else:
            mark, reason = "correct", "Value matches saved facts or release after report rounding"
        correction = f"{value} {unit}; {source}" if mark != "correct" and value is not None else None
        marks.append({"id": str(claim), "mark": mark, "reported": str(reported) if reported is not None else None,
                      "expected": str(value) if value is not None else None, "unit": unit,
                      "reason": reason, "evidence": quote_evidence if not quote_ok else line_evidence if not line_ok else source,
                      "arithmetic": arithmetic_evidence,
                      "correction": correction})
    # A separate prose growth statement must agree with the two annual revenues it quotes.
    for line_no, line in enumerate(report.splitlines(), 1):
        if "revenue growth" not in line.lower() or line.lstrip().startswith("|"):
            continue
        match = re.search(r"(-?\d+(?:\.\d+)?)\s*%", line)
        amounts = re.findall(r"\$\s*(\d[\d,]*(?:\.\d+)?)", line)
        if not match or len(amounts) < 2:
            continue
        rate = Decimal(match.group(1))
        current, prior = (Decimal(x.replace(",", "")) for x in amounts[:2])
        computed = (current / prior - 1) * 100 if prior else None
        ok = _near(rate, computed, match.group(1)) if computed is not None else False
        marks.append({"id": f"prose-L{line_no}", "mark": "correct" if ok else "wrong",
                      "reported": str(rate), "expected": str(computed) if computed is not None else None,
                      "reason": f"({current} / {prior} - 1) × 100 = {computed}%" if computed is not None else "Prior revenue is zero",
                      "correction": f"{computed}% from quoted annual revenues" if not ok and computed is not None else None})
    # Check peer-table figures against each peer's own saved 10-K facts.
    for ticker, peer in run.get("peers", {}).items():
        peer_rows = [line for line in report.splitlines() if line.startswith("|") and re.search(rf"\b{re.escape(ticker)}\b", line)]
        if not peer_rows:
            continue
        row = peer_rows[0]
        values = [Decimal(x.replace(",", "")) for x in re.findall(r"\$\s*(\d[\d,]*(?:\.\d+)?)", row)]
        percent = re.search(r"(\d+(?:\.\d+)?)\s*%", row)
        if not percent:
            tail = row.strip().strip("|").split("|")[-1]
            decimal_margin = re.search(r"(?<!\d)(0\.\d{3,})(?!\d)", tail)
            margin_reported = Decimal(decimal_margin.group(1)) * 100 if decimal_margin else None
        else:
            margin_reported = Decimal(percent.group(1))
        values = [value / Decimal(1_000_000_000) if value >= 1_000_000 else value for value in values]
        facts = peer["facts"]
        revenue_row = facts["concepts"]["total_revenue"]["current"]
        operating_row = facts["concepts"]["operating_income"]["current"]
        if not revenue_row or not operating_row:
            marks.append({"id": f"peer-{ticker}", "mark": "unsupported", "reason": "Peer XBRL fact missing", "correction": None})
            continue
        revenue_expected = Decimal(str(revenue_row["value"])) / Decimal(1_000_000_000)
        operating_expected = Decimal(str(operating_row["value"])) / Decimal(1_000_000_000)
        margin_expected = operating_expected / revenue_expected * 100
        for label, reported, expected_value in (("revenue", values[0] if values else None, revenue_expected),
                                                ("operating income", values[1] if len(values) > 1 else None, operating_expected),
                                                ("operating margin", margin_reported, margin_expected)):
            raw = str(reported) if reported is not None else ""
            ok = _near(reported, expected_value, raw)
            marks.append({"id": f"peer-{ticker}-{label}", "mark": "correct" if ok else "wrong" if reported is not None else "unsupported",
                          "reported": str(reported) if reported is not None else None, "expected": str(expected_value),
                          "reason": f"Peer 10-K {facts['filing_accession']}, year ended {facts['fiscal_year_end']}; "
                                    f"revenue {revenue_row['tag']}, operating income {operating_row['tag']}",
                          "correction": f"{expected_value} from saved peer facts" if not ok else None})
    price = run.get("input", {}).get("price")
    eps = _fact(run, "diluted_eps")
    if price is not None and eps not in (None, 0):
        for line_no, line in enumerate(report.splitlines(), 1):
            if "P/E" not in line or "Price / annual" not in line:
                continue
            figure = re.search(r"=\s*\*{0,2}(\d+(?:\.\d+)?)\s*[×x]", line)
            expected_pe = Decimal(str(price)) / eps
            reported_pe = Decimal(figure.group(1)) if figure else None
            ok = _near(reported_pe, expected_pe, figure.group(1)) if figure else False
            marks.append({"id": f"historical-P/E-L{line_no}", "mark": "correct" if ok else "wrong" if figure else "unsupported",
                          "reported": str(reported_pe) if reported_pe is not None else None,
                          "expected": str(expected_pe),
                          "reason": f"Saved price input {price} on {run['input'].get('price_date')} / annual diluted EPS {eps} = {expected_pe}; external close source needs human check",
                          "correction": f"{expected_pe} from saved price and EPS" if not ok else None})
            break
    return marks


def render_verified(report: str, marks: list[dict], semantic_status: str) -> str:
    lines = report.splitlines()
    by_id = {item["id"]: item for item in marks}
    corrected_lines = []
    for number, line in enumerate(lines, 1):
        row = re.match(r"^\|\s*(\d{1,2})(?:\.[^|]*)?\s*\|", line)
        item = by_id.get(row.group(1)) if row else by_id.get(f"prose-L{number}")
        if item and item["mark"] == "wrong" and item.get("reported") and item.get("expected"):
            old = str(item["reported"])
            places = len(old.split(".", 1)[1]) if "." in old else 0
            new = f"{Decimal(item['expected']):.{places}f}"
            if row and item["id"] in ("1", "3", "4", "5", "9", "11"):
                line = line.replace("$" + old, "$" + new, 1)
            elif not row:
                line = line.replace(old + "%", new + "%", 1)
            line = re.sub(r'\|\s*(?:10-K|EX-99\.1)\s+line\s+\d+:\s*["“][^"”]+["”]\s*\|',
                          '| Corrected source: saved filing line in mark table |', line)
            line += " <!-- Automated correction; see original report.md -->"
        corrected_lines.append(line)
    lines = corrected_lines
    first = lines[0] if lines else "Filings read: unavailable"
    table = ["", "## Automated verifier marks", "", f"Semantic line review: {semantic_status}.",
             "", "| Claim | Mark | Code check and evidence | Correction from saved evidence |", "|---|---|---|---|"]
    for item in marks:
        esc = lambda v: str(v or "").replace("|", "\\|").replace("\n", " ")
        table.append(f"| {esc(item['id'])} | {esc(item['mark'])} | {esc(item['reason'])}; {esc(item.get('evidence'))} | {esc(item.get('correction'))} |")
    table.extend(["", "Human audit and partner checks: pending; no human mark is implied.", ""])
    return "\n".join([first, *table, *lines[1:]]) + "\n"
