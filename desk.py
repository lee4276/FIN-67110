"""Seven SEC data steps for a ticker-based equity research desk.

No model calls are made here. Run ``uv run desk.py --help`` for usage.
"""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import time
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "runs"
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
ARCHIVE = "https://www.sec.gov/Archives/edgar/data"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        os.environ.setdefault(key, value)


class SecClient:
    def __init__(self, user_agent: str):
        if not user_agent or "@" not in user_agent:
            raise ValueError("Set SEC_USER_AGENT in .env to your name and email.")
        self.user_agent = user_agent
        self.last_request = 0.0

    def get(self, url: str) -> bytes:
        if not url.startswith(("https://www.sec.gov/", "https://data.sec.gov/")):
            raise ValueError(f"Refusing non-SEC URL: {url}")
        delay = 0.25 - (time.monotonic() - self.last_request)
        if delay > 0:
            time.sleep(delay)
        request = Request(
            url,
            headers={"User-Agent": self.user_agent, "Accept-Encoding": "identity"},
        )
        try:
            with urlopen(request, timeout=35) as response:
                result = response.read()
        except (HTTPError, URLError) as error:
            raise RuntimeError(f"SEC request failed for {url}: {error}") from error
        finally:
            self.last_request = time.monotonic()
        return result

    def json(self, url: str) -> dict:
        return json.loads(self.get(url))


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag in {"script", "style"}:
            self.skip += 1
        elif tag in {"br", "p", "div", "tr", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append(" | ")

    def handle_endtag(self, tag: str):
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1
        elif tag in {"p", "div", "tr", "li", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str):
        if not self.skip:
            self.parts.append(data)


class RowParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[list[dict[str, str]]] = []
        self.row: list[dict[str, str]] | None = None
        self.cell: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = {"text": "", "href": ""}
        elif tag == "a" and self.cell is not None:
            self.cell["href"] = dict(attrs).get("href") or ""

    def handle_data(self, data: str):
        if self.cell is not None:
            self.cell["text"] += data

    def handle_endtag(self, tag: str):
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            self.cell["text"] = " ".join(self.cell["text"].split())
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def to_text(content: bytes, name: str) -> str:
    if content[:4] == b"%PDF":
        raise ValueError(f"{name} is PDF; use a text or HTML filing document.")
    try:
        raw = content.decode("utf-8")
    except UnicodeDecodeError:
        raw = content.decode("cp1252", errors="replace")
    if "<html" in raw[:3000].lower() or "<table" in raw[:3000].lower():
        parser = TextParser()
        parser.feed(raw)
        raw = "".join(parser.parts)
    raw = html.unescape(raw).replace("\xa0", " ")
    return "\n".join(
        " ".join(line.split()) for line in raw.splitlines() if line.strip()
    )


def resolve_ticker(client: SecClient, ticker: str) -> dict:
    table = client.json(TICKERS_URL)
    found = next(
        (entry for entry in table.values() if entry["ticker"].upper() == ticker.upper()),
        None,
    )
    if found is None:
        raise ValueError(f"Ticker {ticker!r} is absent from SEC company_tickers.json.")
    return {"ticker": ticker.upper(), "cik": int(found["cik_str"]), "name": found["title"]}


def filing_rows(client: SecClient, cik: int) -> list[dict]:
    data = client.json(SUBMISSIONS_URL.format(cik=cik))
    recent = data["filings"]["recent"]
    rows = [dict(zip(recent, values)) for values in zip(*(recent[k] for k in recent))]
    # The current file usually suffices; old files matter for infrequent filers.
    if not any(r.get("form") == "10-K" for r in rows):
        for item in data["filings"].get("files", []):
            older = client.json("https://data.sec.gov/submissions/" + item["name"])
            rows.extend(dict(zip(older, values)) for values in zip(*(older[k] for k in older)))
            if any(r.get("form") == "10-K" for r in rows):
                break
    return sorted(rows, key=lambda r: (r.get("filingDate", ""), r.get("acceptanceDateTime", "")), reverse=True)


def archive_base(cik: int, accession: str) -> str:
    return f"{ARCHIVE}/{cik}/{accession.replace('-', '')}/"


def index_url(cik: int, accession: str) -> str:
    return f"{ARCHIVE}/{cik}/{accession.replace('-', '')}/{accession}-index.htm"


def filing_index(client: SecClient, cik: int, filing: dict) -> tuple[str, list[list[dict[str, str]]]]:
    url = index_url(cik, filing["accessionNumber"])
    page = client.get(url).decode("utf-8", errors="replace")
    text_parser = TextParser()
    text_parser.feed(page)
    plain = " ".join("".join(text_parser.parts).split())
    match = re.search(r"Accepted\s*(?:[:|]\s*)?(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", plain, re.I)
    if not match:
        match = re.search(r"Accepted\s*(?:[:|]\s*)?(\d{14})", plain, re.I)
    accepted = match.group(1) if match else "NOT FOUND ON INDEX"
    rows = RowParser()
    rows.feed(page)
    return accepted, rows.rows


def select_filings(client: SecClient, cik: int) -> dict[str, dict]:
    rows = filing_rows(client, cik)
    selected: dict[str, dict] = {}
    for form in ("10-K", "10-Q"):
        selected[form] = next((row for row in rows if row.get("form") == form), None)
        if selected[form] is None:
            raise ValueError(f"No {form} found for CIK {cik}.")
    for row in rows:
        if row.get("form") not in {"8-K", "8-K/A"}:
            continue
        items = row.get("items") or ""
        if re.search(r"\b2\.02\b", items):
            selected["8-K"] = row
            break
        # Some older submissions omit the items field. Inspect the filing itself.
        if not items:
            url = urljoin(archive_base(cik, row["accessionNumber"]), row["primaryDocument"])
            if re.search(r"Item\s*2[.\s]*02\b", to_text(client.get(url), url), re.I):
                selected["8-K"] = row
                break
    if "8-K" not in selected:
        raise ValueError("No earnings 8-K reporting Item 2.02 was found.")
    for row in selected.values():
        row["accepted_from_index"], row["index_rows"] = filing_index(client, cik, row)
        row["index_url"] = index_url(cik, row["accessionNumber"])
    return selected


def exhibit_name(rows: list[list[dict[str, str]]]) -> str:
    for row in rows:
        if any(re.fullmatch(r"EX[- ]?99[. ]?1", cell["text"], re.I) for cell in row):
            link = next((cell["href"] for cell in row if cell["href"]), "")
            if link:
                return link
    for row in rows:
        if any(re.search(r"(?:exhibit|ex)[ _.-]*99[. _-]*1", cell["text"], re.I) for cell in row):
            link = next((cell["href"] for cell in row if cell["href"]), "")
            if link:
                return link
    raise ValueError("The 8-K index has no identifiable Exhibit 99.1; inspect it by hand.")


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")[:80]


def download_documents(client: SecClient, cik: int, filings: dict, folder: Path) -> dict:
    documents = {}
    for form in ("10-K", "10-Q", "8-K"):
        filing = filings[form]
        url = urljoin(archive_base(cik, filing["accessionNumber"]), filing["primaryDocument"])
        text = to_text(client.get(url), url)
        name = f"{form}_{filing['accessionNumber']}.txt"
        (folder / name).write_text(text, encoding="utf-8")
        documents[form] = {"url": url, "path": name, "text": text}
    release_href = exhibit_name(filings["8-K"]["index_rows"])
    release_url = urljoin(archive_base(cik, filings["8-K"]["accessionNumber"]), release_href)
    release_text = to_text(client.get(release_url), release_url)
    name = f"EX-99.1_{filings['8-K']['accessionNumber']}.txt"
    (folder / name).write_text(release_text, encoding="utf-8")
    documents["EX-99.1"] = {"url": release_url, "path": name, "text": release_text}
    return documents


CONCEPTS = {
    "total_revenue": ("USD", False, ["Revenues", "RevenueFromContractWithCustomerIncludingAssessedTax", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]),
    "operating_income": ("USD", False, ["OperatingIncomeLoss"]),
    "net_income": ("USD", False, ["NetIncomeLoss", "ProfitLoss", "NetIncomeLossAvailableToCommonStockholdersBasic"]),
    "diluted_eps": ("USD/shares", False, ["EarningsPerShareDiluted"]),
    "stockholders_equity": ("USD", True, ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]),
    "long_term_debt_noncurrent": ("USD", True, ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations", "LongTermDebt"]),
    "long_term_debt_current": ("USD", True, ["LongTermDebtCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent", "CurrentPortionOfLongTermDebt"]),
    "long_term_debt_including_current": ("USD", True, ["LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities", "LongTermDebtAndFinanceLeaseObligationsIncludingCurrentMaturities"]),
    "cash_from_operations": ("USD", False, ["NetCashProvidedByUsedInOperatingActivities"]),
    "property_equipment_additions": ("USD", False, ["PaymentsToAcquirePropertyPlantAndEquipment"]),
}


def annual_record(row: dict, end: str, accession: str, instant: bool) -> bool:
    if row.get("accn") != accession or row.get("form") != "10-K" or row.get("end") != end:
        return False
    if instant:
        return "start" not in row
    if "start" not in row:
        return False
    return 300 <= (date.fromisoformat(end) - date.fromisoformat(row["start"])).days <= 400


def pick_fact(facts: dict, concept: str, end: str, accession: str) -> dict | None:
    unit, instant, tags = CONCEPTS[concept]
    candidates = []
    for priority, tag in enumerate(tags):
        data = facts.get("facts", {}).get("us-gaap", {}).get(tag)
        if not data:
            continue
        for row in data.get("units", {}).get(unit, []):
            if annual_record(row, end, accession, instant):
                candidates.append((priority, row.get("filed", ""), tag, row))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=False)
    priority = candidates[0][0]
    best = max((c for c in candidates if c[0] == priority), key=lambda x: x[1])
    row = best[3]
    return {"value": row["val"], "unit": unit, "tag": best[2], "period_start": row.get("start"), "period_end": row["end"], "accession": row["accn"], "filed": row.get("filed")}


def company_facts(client: SecClient, cik: int, annual_filing: dict) -> dict:
    facts = client.json(FACTS_URL.format(cik=cik))
    accession = annual_filing["accessionNumber"]
    fiscal_end = annual_filing["reportDate"]
    revenue_unit, _, revenue_tags = CONCEPTS["total_revenue"]
    revenue_choices = []
    for priority, tag in enumerate(revenue_tags):
        for row in facts.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {}).get(revenue_unit, []):
            if row.get("accn") == accession and row.get("form") == "10-K" and row.get("start") and annual_record(row, row["end"], accession, False):
                revenue_choices.append((row["end"], -priority, tag))
    if not revenue_choices:
        raise ValueError(f"No full-year revenue fact in latest 10-K {accession}.")
    newest_end = max(revenue_choices)[0]
    if newest_end != fiscal_end:
        raise ValueError(f"Revenue year {newest_end} differs from latest 10-K fiscal end {fiscal_end}.")
    prior_end = max((d for d, _, _ in revenue_choices if d < fiscal_end), default=None)
    if prior_end is None:
        prior_end = date(date.fromisoformat(fiscal_end).year - 1, date.fromisoformat(fiscal_end).month, min(date.fromisoformat(fiscal_end).day, 28)).isoformat()
    result = {"fiscal_year_end": fiscal_end, "prior_year_end": prior_end, "filing_accession": accession, "concepts": {}}
    for concept in CONCEPTS:
        result["concepts"][concept] = {
            "current": pick_fact(facts, concept, fiscal_end, accession),
            "prior": pick_fact(facts, concept, prior_end, accession),
        }
    return result


def value(facts: dict, concept: str, period: str = "current") -> float | None:
    row = facts["concepts"][concept][period]
    return None if row is None else row["value"]


def calculate(facts: dict, price: float | None) -> dict:
    def ratio(name: str, numerator: float | None, denominator: float | None, expression: str):
        if numerator is None or denominator in (None, 0):
            result[name] = {"value": None, "arithmetic": "unavailable: required fact missing"}
        else:
            result[name] = {"value": numerator / denominator, "arithmetic": expression}

    result: dict[str, dict] = {}
    revenue = value(facts, "total_revenue")
    prior_revenue = value(facts, "total_revenue", "prior")
    op_income = value(facts, "operating_income")
    net_income = value(facts, "net_income")
    equity = value(facts, "stockholders_equity")
    prior_equity = value(facts, "stockholders_equity", "prior")
    debt_all = value(facts, "long_term_debt_including_current")
    debt_long = value(facts, "long_term_debt_noncurrent")
    debt_current = value(facts, "long_term_debt_current")
    if debt_all is None and debt_long is not None and debt_current is not None:
        debt_all = debt_long + debt_current
    ratio("revenue_growth", None if revenue is None or prior_revenue is None else revenue - prior_revenue, prior_revenue, f"({revenue} - {prior_revenue}) / {prior_revenue}")
    ratio("operating_margin", op_income, revenue, f"{op_income} / {revenue}")
    average_equity = (equity + prior_equity) / 2 if equity is not None and prior_equity is not None else None
    ratio("return_on_average_equity", net_income, average_equity, f"{net_income} / (({equity} + {prior_equity}) / 2)")
    ratio("debt_to_equity", debt_all, equity, f"{debt_all} / {equity}; debt includes current portion")
    cfo = value(facts, "cash_from_operations")
    capex = value(facts, "property_equipment_additions")
    result["free_cash_flow"] = {"value": cfo - capex if cfo is not None and capex is not None else None, "arithmetic": f"{cfo} - {capex}" if cfo is not None and capex is not None else "unavailable: required fact missing"}
    eps = value(facts, "diluted_eps")
    ratio("price_to_earnings", price, eps, f"{price} / {eps}; price date must be recorded separately")
    return result


def release_lines(text: str) -> dict:
    lines = text.splitlines()
    revenue = [{"line": i, "text": line} for i, line in enumerate(lines, 1) if re.search(r"\b(total\s+)?(net\s+)?revenues?\b|\bnet sales\b", line, re.I)]
    eps = [{"line": i, "text": line} for i, line in enumerate(lines, 1) if re.search(r"diluted.*(earnings|net income|per share|EPS)|earnings.*diluted|diluted\s*EPS", line, re.I)]
    quarter_growth = None
    ordered_revenue = sorted(revenue, key=lambda row: (0 if re.match(r"\|?\s*total\s+revenues?\b", row["text"], re.I) else 2 if re.match(r"\|?\s*net\s+sales\b", row["text"], re.I) else 1, row["line"]))
    for row in ordered_revenue:
        label = row["text"].strip(" |")
        if "|" in label:
            label = label.split("|", 1)[0].strip()
        label = re.sub(r"\s*\(\d+\)$", "", label)
        if not re.fullmatch(r"(?:total\s+)?(?:net\s+)?revenues?|total\s+net\s+sales", label, re.I):
            continue
        row_text = " ".join(lines[row["line"] - 1:row["line"] + 2])
        inline = [float(n.replace(",", "")) for n in re.findall(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?", row_text)]
        if len(inline) >= 2 and inline[1] != 0:
            quarter_growth = {"current": inline[0], "prior": inline[1], "value": inline[0] / inline[1] - 1, "arithmetic": f"({inline[0]} / {inline[1]}) - 1", "source_line": row["line"], "current_line": row["line"], "prior_line": row["line"], "unit": "as displayed in release table"}
            break
        # SEC HTML tables can put each cell on its own text line. Inspect only
        # the revenue row up to the next named statement row, not the narrative.
        following = lines[row["line"]:row["line"] + 30]
        cell_lines = []
        for offset, cell in enumerate(following, row["line"] + 1):
            if offset > row["line"] + 2 and re.search(r"^(?:operating income|cost of revenue|cost of sales|gross profit|net income|research and development)\b", cell.strip(" |"), re.I):
                break
            cell_lines.append((offset, cell))
        amounts = []
        for line_number, cell in cell_lines:
            for match in re.finditer(r"\$\s*(\d{1,3}(?:,\d{3})+(?:\.\d+)?)", cell):
                amounts.append((float(match.group(1).replace(",", "")), line_number))
        if len(amounts) >= 2 and amounts[1][0] != 0:
            current, prior = amounts[:2]
            quarter_growth = {"current": current[0], "prior": prior[0], "value": current[0] / prior[0] - 1, "arithmetic": f"({current[0]} / {prior[0]}) - 1", "source_line": row["line"], "current_line": current[1], "prior_line": prior[1], "unit": "as displayed in release table"}
            break
    return {"revenue_candidates": revenue[:12], "diluted_eps_candidates": eps[:12], "quarter_revenue_growth": quarter_growth}


def public_filing_data(filings: dict) -> dict:
    return {form: {key: row.get(key) for key in ("form", "filingDate", "reportDate", "accessionNumber", "primaryDocument", "items", "accepted_from_index", "index_url")} for form, row in filings.items()}


def print_facts(facts: dict) -> None:
    print(f"Fiscal year end: {facts['fiscal_year_end']} | 10-K: {facts['filing_accession']}")
    for name, pair in facts["concepts"].items():
        for label in ("current", "prior"):
            row = pair[label]
            if row:
                print(f"  {name} {label}: {row['value']} {row['unit']} | {row['tag']} | end {row['period_end']} | filing {row['accession']}")
            else:
                print(f"  {name} {label}: NOT FOUND for this 10-K and fiscal year")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seven ticker-to-filing SEC data steps")
    parser.add_argument("ticker")
    parser.add_argument("--peers", default="", help="Comma-separated ticker list")
    parser.add_argument("--price", type=float, help="Share close before release; record its date separately")
    parser.add_argument("--price-date", help="Date of the supplied close, YYYY-MM-DD")
    parser.add_argument("--step", type=int, choices=range(1, 8), help="Run one numbered step")
    args = parser.parse_args()
    if args.price is not None and args.price <= 0:
        parser.error("--price must be positive")
    load_env(ROOT / ".env")
    client = SecClient(os.getenv("SEC_USER_AGENT", ""))
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S%z")
    if args.price_date:
        date.fromisoformat(args.price_date)
    run: dict = {"run_time": datetime.now().astimezone().isoformat(), "input": {"ticker": args.ticker.upper(), "peers": args.peers, "price": args.price, "price_date": args.price_date}}
    show = lambda n: args.step is None or args.step == n

    company = resolve_ticker(client, args.ticker)
    run["company"] = company
    folder = DATA_ROOT / f"{safe_name(company['name'])}_{stamp}"
    folder.mkdir(parents=True, exist_ok=False)
    if show(1):
        print(f"STEP 1 | {company['ticker']} -> CIK {company['cik']:010d} | {company['name']}", flush=True)

    filings = None
    if args.step is None or args.step >= 2:
        filings = select_filings(client, company["cik"])
        run["filings"] = public_filing_data(filings)
        if show(2):
            print("STEP 2 | Latest filings", flush=True)
            for form, row in filings.items():
                print(f"  {form}: {row['accessionNumber']} | Accepted {row['accepted_from_index']} | {row['index_url']}")

    documents = None
    if args.step is None or args.step in {3, 6}:
        documents = download_documents(client, company["cik"], filings, folder)
        run["documents"] = {key: {"url": doc["url"], "path": doc["path"]} for key, doc in documents.items()}
        if show(3):
            print("STEP 3 | Saved filing and release texts", flush=True)
            for name, doc in documents.items():
                print(f"  {name}: {folder / doc['path']}")

    facts = None
    if args.step is None or args.step in {4, 5}:
        facts = company_facts(client, company["cik"], filings["10-K"])
        run["facts"] = facts
        if show(4):
            print("STEP 4 | Latest fiscal year and prior year XBRL facts", flush=True)
            print_facts(facts)

    if show(5):
        run["ratios"] = calculate(facts, args.price)
        print("STEP 5 | Calculator", flush=True)
        for name, item in run["ratios"].items():
            print(f"  {name}: {item['value']} | {item['arithmetic']}")

    if show(6):
        run["release_lines"] = release_lines(documents["EX-99.1"]["text"])
        print("STEP 6 | Release lines (verify the quarter and GAAP definition)", flush=True)
        for label, lines in run["release_lines"].items():
            print(f"  {label}:")
            if isinstance(lines, list):
                for line in lines:
                    print(f"    L{line['line']}: {line['text']}")
            elif lines:
                print(f"    {lines}")

    if show(7):
        print("STEP 7 | Peer facts and operating margins", flush=True)
        run["peers"] = {}
        for ticker in [t.strip().upper() for t in args.peers.split(",") if t.strip()]:
            peer = resolve_ticker(client, ticker)
            peer_filings = select_filings(client, peer["cik"])
            peer_facts = company_facts(client, peer["cik"], peer_filings["10-K"])
            margin = calculate(peer_facts, None)["operating_margin"]
            run["peers"][ticker] = {"company": peer, "filings": public_filing_data(peer_filings), "facts": peer_facts, "operating_margin": margin}
            print(f"  {ticker} | fiscal end {peer_facts['fiscal_year_end']} | margin {margin['value']} | {margin['arithmetic']}")
            print_facts(peer_facts)

    (folder / "facts.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
    print(f"Saved facts: {folder / 'facts.json'}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
