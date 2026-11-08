"""Check saved team runs and seeded copies without making API calls."""
import hashlib
import json
from pathlib import Path
import unittest

from desk import ROOT
from team import graph


ORDER = ["01_data_steps", "02_research", "03_financial", "04_advisor", "05_manager", "06_verifier"]


def full_runs() -> list[Path]:
    folders = []
    for folder in (ROOT / "runs").iterdir():
        log = folder / "node_order.log"
        if folder.is_dir() and log.is_file() and (folder / "report.md").is_file():
            if log.read_text(encoding="utf-8").splitlines()[:6] == ORDER:
                folders.append(folder)
    return sorted(folders, key=lambda folder: folder.name)[-2:]


class Checkpoint2EvidenceTests(unittest.TestCase):
    def test_two_full_runs_have_the_same_required_order(self):
        runs = full_runs()
        self.assertEqual(2, len(runs))
        self.assertNotEqual(runs[0], runs[1])
        for folder in runs:
            self.assertEqual(ORDER, (folder / "node_order.log").read_text(encoding="utf-8").splitlines()[:6])
            marks = json.loads((folder / "marks.json").read_text(encoding="utf-8"))
            self.assertTrue(marks["semantic_status"].startswith("completed"))
            core = [item for item in marks["marks"] if item["id"].isdigit()]
            self.assertEqual(11, len(core))
            self.assertTrue(all(item["mark"] == "correct" for item in core))

    def test_seeded_copies_keep_evidence_and_catch_both_errors(self):
        source = full_runs()[0]
        proofs = ROOT / "runs" / "lab04_proofs"
        copies = {label: next(folder for folder in proofs.iterdir()
                              if folder.is_dir() and source.name in folder.name and folder.name.endswith(label))
                  for label in ("seeded_eps", "invented_growth")}
        for folder in copies.values():
            for file in source.iterdir():
                if file.name == "facts.json" or file.suffix == ".txt":
                    self.assertEqual(hashlib.sha256(file.read_bytes()).digest(),
                                     hashlib.sha256((folder / file.name).read_bytes()).digest())
        eps = json.loads((copies["seeded_eps"] / "marks.json").read_text(encoding="utf-8"))["marks"]
        eps_mark = next(item for item in eps if item["id"] == "5")
        self.assertEqual("wrong", eps_mark["mark"])
        self.assertEqual("21.76", eps_mark["reported"])
        self.assertEqual("20.76", eps_mark["expected"])
        self.assertIn("L752", eps_mark["evidence"])
        growth = json.loads((copies["invented_growth"] / "marks.json").read_text(encoding="utf-8"))["marks"]
        growth_mark = next(item for item in growth if item["id"].startswith("prose-L"))
        self.assertEqual("wrong", growth_mark["mark"])
        self.assertEqual("14.14", growth_mark["reported"])
        self.assertIn("303.154 / 275.235", growth_mark["reason"])

    def test_every_completed_graph_path_reaches_verifier(self):
        edges = {}
        for edge in graph().get_graph().edges:
            edges.setdefault(edge.source, []).append(edge.target)
        paths = []
        def visit(node, path):
            if node == "__end__":
                paths.append(path + [node])
                return
            for target in edges.get(node, []):
                if target not in path:
                    visit(target, path + [node])
        visit("__start__", [])
        self.assertTrue(paths)
        self.assertTrue(all("verifier" in path for path in paths))


if __name__ == "__main__":
    unittest.main()
