"""LangGraph team: code owns node order and the one correction slot."""
from __future__ import annotations

import argparse
from datetime import date, datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app import PARTS, make_context, missing_parts, model_call
from desk import ROOT, DATA_ROOT, load_env
from verifier import _claim_label_ok, _rows, check_report, render_verified


class TeamState(TypedDict, total=False):
    ticker: str
    peers: str
    price: float | None
    price_date: str | None
    model: str
    client: object
    folder: str
    run: dict
    contexts: dict
    outputs: dict
    report: str
    retry_role: str
    counts: dict
    verified_report: str
    manager_issues: list[str]


ROLE_FILES = {
    "Research Analyst": "research_analyst.md",
    "Financial Analyst": "financial_analyst.md",
    "Investment Advisor": "investment_advisor.md",
    "Strategy Manager": "strategy_manager.md",
    "Verifier": "verifier.md",
}
ROLE_HEADINGS = {
    "Research Analyst": [PARTS[0], PARTS[1], PARTS[3]],
    "Financial Analyst": [PARTS[2]],
    "Investment Advisor": [PARTS[4]],
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def record(folder: Path, name: str, request: dict, response: object, log_name: str = "node_order.log") -> None:
    with (folder / log_name).open("a", encoding="utf-8") as log:
        log.write(name + "\n")
    write_json(folder / f"{name}_input.json", request)
    if isinstance(response, str):
        (folder / f"{name}_output.md").write_text(response, encoding="utf-8")
    else:
        write_json(folder / f"{name}_output.json", response)


def instructions(name: str) -> str:
    return (ROOT / "roles" / ROLE_FILES[name]).read_text(encoding="utf-8")


def steps(state: TeamState) -> dict:
    print("Data steps 1-7", flush=True)
    existing = set(DATA_ROOT.iterdir()) if DATA_ROOT.exists() else set()
    command = [sys.executable, str(ROOT / "desk.py"), state["ticker"]]
    if state["peers"]:
        command += ["--peers", state["peers"]]
    if state["price"] is not None:
        command += ["--price", str(state["price"])]
    if state["price_date"]:
        command += ["--price-date", state["price_date"]]
    subprocess.run(command, cwd=ROOT, check=True)
    created = set(DATA_ROOT.iterdir()) - existing
    if len(created) != 1:
        raise RuntimeError("Could not identify one new SEC data run")
    folder = created.pop()
    run = json.loads((folder / "facts.json").read_text(encoding="utf-8"))
    contexts = make_context(run, folder)
    record(folder, "01_data_steps", {"ticker": state["ticker"], "peers": state["peers"],
                                      "price": state["price"], "price_date": state["price_date"]},
           {"facts_file": "facts.json", "documents": run["documents"], "role_inputs": contexts})
    return {"folder": str(folder), "run": run, "contexts": contexts, "outputs": {}, "counts": {}}


def role_request(state: TeamState, name: str, revision: bool = False) -> dict:
    if name == "Research Analyst":
        context = state["contexts"]["research"]
    elif name == "Financial Analyst":
        context = state["contexts"]["financial"]
    else:
        context = {"research_analyst": state["outputs"]["Research Analyst"],
                   "financial_analyst": state["outputs"]["Financial Analyst"]}
    if revision:
        context = {"assigned_context": context, "prior_output": state["outputs"][name],
                   "manager_issues": state.get("manager_issues", [])}
    return {"task": f"{'Revise' if revision else 'Write'} the {name} part from assigned evidence",
            "context": context, "expected_output": "Markdown with assigned headings and sourced numbers"}


def role_node(name: str, serial: str, revision: bool = False):
    def run_role(state: TeamState) -> dict:
        print(name + (" correction" if revision else ""), flush=True)
        folder = Path(state["folder"])
        request = role_request(state, name, revision)
        result = model_call(state["client"], state["model"], instructions(name),
                            request["task"], request["context"], request["expected_output"])
        record(folder, serial, request, result)
        outputs = {**state["outputs"], name: result}
        counts = {**state["counts"], name: state["counts"].get(name, 0) + 1}
        if counts[name] > 2:
            raise RuntimeError(f"{name} ran more than twice")
        return {"outputs": outputs, "counts": counts}
    return run_role


def manager_node(serial: str, revision: bool = False):
    def run_manager(state: TeamState) -> dict:
        print("Strategy Manager" + (" correction" if revision else ""), flush=True)
        folder = Path(state["folder"])
        request = {"task": "Compile the five report parts and check consistency",
                   "context": {"role_outputs": state["outputs"], "required_sections": PARTS,
                               **({"prior_report": state["report"], "manager_issues": state.get("manager_issues", [])} if revision else {})},
                   "expected_output": "Five-part Markdown report with an 11-row core-claims table"}
        result = model_call(state["client"], state["model"], instructions("Strategy Manager"),
                            request["task"], request["context"], request["expected_output"])
        record(folder, serial, request, result)
        counts = {**state["counts"], "Strategy Manager": state["counts"].get("Strategy Manager", 0) + 1}
        if counts["Strategy Manager"] > 2:
            raise RuntimeError("Strategy Manager ran more than twice")
        missing = missing_parts(result, PARTS)
        for name, headings in ROLE_HEADINGS.items():
            missing.extend(missing_parts(state["outputs"][name], headings))
        missing.extend(f"core claim {n}" for n in range(1, 12)
                       if not re.search(rf"(?m)^\|\s*{n}(?:\.|\s*\|)", result))
        core_rows = _rows(result)
        missing.extend(f"core claim {n} definition" for n, row in core_rows.items() if not _claim_label_ok(row, n))
        found = [match.group(1) for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", result)
                 if match.group(1) in PARTS]
        if found != PARTS:
            missing.append("section order or duplicate section")
        write_json(folder / f"{serial}_checks.json", {"missing_or_inconsistent": missing})
        retry_role = ""
        if missing and not revision:
            first = missing[0]
            if first.startswith("core claim"):
                retry_role = "Financial Analyst"
            elif first == "section order or duplicate section":
                retry_role = "Research Analyst"
            else:
                retry_role = next(name for name, headings in ROLE_HEADINGS.items() if first in headings)
        first = "Filings read: " + "; ".join(f"{form} {item['accessionNumber']}" for form, item in state["run"]["filings"].items())
        first += f"; earnings release EX-99.1 from 8-K {state['run']['filings']['8-K']['accessionNumber']}"
        report = first + "\n" + f"Run time: {state['run']['run_time']}" + "\n\n" + result.strip() + "\n"
        (folder / "report.md").write_text(report, encoding="utf-8")
        return {"report": report, "counts": counts, "retry_role": retry_role, "manager_issues": missing}
    return run_manager


def cited_lines(report: str, folder: Path) -> dict:
    snippets = {}
    source_lines: dict[str, set[int]] = {name: set() for name in ("10-K", "10-Q", "8-K", "EX-99.1")}
    for row in report.splitlines():
        targets = []
        if re.search(r"\b10-K\b", row, re.I):
            targets.append("10-K")
        if re.search(r"\b10-Q\b", row, re.I):
            targets.append("10-Q")
        if re.search(r"\b(?:EX-99\.1|Exhibit\s*99\.1|release)\b", row, re.I):
            targets.append("EX-99.1")
        if not targets:
            continue
        for match in re.finditer(r"\b(?:L|line(?:s)?\s*)(\d+)(?:\s*[-–]\s*L?(\d+))?", row, re.I):
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            for name in targets:
                source_lines[name].update(range(start, min(end, start + 25) + 1))
    for source in ("10-K", "10-Q", "8-K", "EX-99.1"):
        files = list(folder.glob(f"{source}_*.txt"))
        if len(files) != 1:
            continue
        lines = files[0].read_text(encoding="utf-8").splitlines()
        snippets[files[0].name] = {str(n): lines[n - 1] for n in sorted(source_lines[source]) if 1 <= n <= len(lines)}
    return snippets


def verify_folder(folder: Path, client=None, model: str | None = None, verify_only: bool = False) -> list[dict]:
    print("Verifier", flush=True)
    report_path = folder / "report.md"
    report = report_path.read_text(encoding="utf-8")
    marks = check_report(report, folder)
    facts = json.loads((folder / "facts.json").read_text(encoding="utf-8"))
    request = {"task": "Check the cited lines for the stated number, period, and definition",
               "context": {"report": report, "saved_facts": facts, "saved_filing_lines": cited_lines(report, folder),
                           "code_marks": marks},
               "expected_output": "JSON object with checks: [{id, supported, reason}]"}
    semantic = "pending: no usable OpenAI API key"
    response = {"status": semantic}
    if client is not None and model is not None:
        try:
            raw = model_call(client, model, instructions("Verifier"), request["task"], request["context"], request["expected_output"])
        except RuntimeError as error:
            if "HTTP 429" not in str(error):
                raise
            semantic = "pending: OpenAI returned HTTP 429"
            response = {"status": semantic}
        else:
            try:
                parsed = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip()))
                checks = {str(x["id"]): x for x in parsed["checks"]}
            except (ValueError, KeyError, TypeError) as error:
                raise RuntimeError("Verifier model returned invalid JSON") from error
            for item in marks:
                check = checks.get(item["id"])
                if item["mark"] == "correct" and (check is None or check.get("supported") is not True):
                    item["mark"] = "unsupported"
                    item["reason"] = "Model did not support the cited period and definition: " + str((check or {}).get("reason", "no model mark"))
                item["semantic_check"] = check or {"supported": None, "reason": "Model gave no mark"}
            semantic = "completed for model-returned cited lines; inspect the verifier node output"
            response = parsed
    name = "verify_only_" + datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S%z") if verify_only else "06_verifier"
    record(folder, name, request, response, "verify_only.log" if verify_only else "node_order.log")
    write_json(folder / "marks.json", {"type": "automated", "semantic_status": semantic, "marks": marks})
    (folder / "verified_report.md").write_text(render_verified(report, marks, semantic), encoding="utf-8")
    print(f"Verified report: {folder / 'verified_report.md'}", flush=True)
    return marks


def verifier_node(state: TeamState) -> dict:
    folder = Path(state["folder"])
    verify_folder(folder, state["client"], state["model"])
    return {"verified_report": str(folder / "verified_report.md")}


def graph():
    builder = StateGraph(TeamState)
    builder.add_node("data_steps", steps)
    builder.add_node("research", role_node("Research Analyst", "02_research"))
    builder.add_node("financial", role_node("Financial Analyst", "03_financial"))
    builder.add_node("advisor", role_node("Investment Advisor", "04_advisor"))
    builder.add_node("manager", manager_node("05_manager"))
    for name, file_name in (("Research Analyst", "research_retry"), ("Financial Analyst", "financial_retry"),
                            ("Investment Advisor", "advisor_retry")):
        builder.add_node(file_name, role_node(name, "05_" + file_name, True))
        builder.add_edge(file_name, "manager_revision")
    builder.add_node("manager_revision", manager_node("05_manager_revision", True))
    builder.add_node("verifier", verifier_node)
    for left, right in ((START, "data_steps"), ("data_steps", "research"), ("research", "financial"),
                        ("financial", "advisor"), ("advisor", "manager"),
                        ("manager_revision", "verifier"), ("verifier", END)):
        builder.add_edge(left, right)
    builder.add_conditional_edges("manager", lambda state: {
        "Research Analyst": "research_retry", "Financial Analyst": "financial_retry",
        "Investment Advisor": "advisor_retry", "": "verifier"}[state["retry_role"]],
        ["research_retry", "financial_retry", "advisor_retry", "verifier"])
    return builder.compile()


def check_openai_access(client) -> None:
    """Check authentication before a full run downloads SEC data."""
    try:
        client.models.list()
    except Exception as error:
        status = getattr(error, "status_code", None)
        if status == 401:
            raise RuntimeError("OpenAI rejected API_KEY in .env (401). No key text is shown.") from None
        if status is not None:
            raise RuntimeError(f"OpenAI credential check returned HTTP {status}. No provider error text is shown.") from None
        raise RuntimeError("Could not reach OpenAI for the credential check. No provider error text is shown.") from None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the fixed LangGraph SEC agent team")
    parser.add_argument("ticker", nargs="?")
    parser.add_argument("--peers", default="")
    parser.add_argument("--price", type=float)
    parser.add_argument("--price-date")
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--verify-only", type=Path, metavar="PATH")
    args = parser.parse_args()
    if args.price_date:
        date.fromisoformat(args.price_date)
    load_env(ROOT / ".env")
    key = os.getenv("API_KEY", "").strip()
    client = None
    if key.startswith("sk-") and len(key) >= 23:
        from openai import OpenAI
        client = OpenAI(api_key=key)
    if args.verify_only:
        folder = args.verify_only if args.verify_only.is_dir() else args.verify_only.parent
        if not (folder / "facts.json").exists() or not (folder / "report.md").exists():
            parser.error("--verify-only needs a saved run with facts.json and report.md")
        verify_folder(folder, client, args.model if client else None, verify_only=True)
        return 0
    if not args.ticker:
        parser.error("ticker is required for a full run")
    if client is None:
        parser.error("A usable OpenAI developer API_KEY is required for a full run; no run was started")
    if args.price is not None and args.price <= 0:
        parser.error("--price must be positive")
    check_openai_access(client)
    result = graph().invoke({"ticker": args.ticker, "peers": args.peers, "price": args.price,
                             "price_date": args.price_date, "model": args.model, "client": client})
    print(result["verified_report"])
    return 0
