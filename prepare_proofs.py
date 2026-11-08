"""Copy one saved run and seed the two Lab 04 errors without editing its evidence."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import re
import shutil
import sys


def main(source: Path) -> None:
    if not (source / "facts.json").is_file() or not (source / "report.md").is_file():
        raise ValueError("Source must be a saved run with facts.json and report.md")
    text = (source / "report.md").read_text(encoding="utf-8")
    run = json.loads((source / "facts.json").read_text(encoding="utf-8"))
    concepts = run["facts"]["concepts"]
    eps = Decimal(str(concepts["diluted_eps"]["current"]["value"]))
    revenue = Decimal(str(concepts["total_revenue"]["current"]["value"])) / Decimal(1_000_000_000)
    prior = Decimal(str(concepts["total_revenue"]["prior"]["value"])) / Decimal(1_000_000_000)
    reported_growth = ((revenue / prior - 1) * 100).quantize(Decimal("0.01"))
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S%z")
    base = source.parent / "lab04_proofs"
    base.mkdir(exist_ok=True)
    for label in ("seeded_eps", "invented_growth"):
        target = base / f"{source.name}_{stamp}_{label}"
        target.mkdir(exist_ok=False)
        for file in source.iterdir():
            if file.name == "facts.json" or file.suffix == ".txt":
                shutil.copy2(file, target / file.name)
        if label == "seeded_eps":
            lines = text.splitlines()
            matches = [i for i, line in enumerate(lines) if re.match(r"^\|\s*5(?:\.|\s*\|)", line)]
            if len(matches) != 1:
                raise ValueError("Expected exactly one annual diluted EPS claim row")
            i = matches[0]
            old = f"${eps:.2f}"
            new = f"${eps + 1:.2f}"
            if old not in lines[i]:
                raise ValueError("Saved EPS row does not contain the XBRL EPS")
            lines[i] = lines[i].replace(old, new, 1)
            cited = re.search(r"\bline\s+(\d+)|\bL\s*(\d+)(?:\s*[-–]\s*(\d+))?", lines[i], re.I)
            if not cited:
                raise ValueError("Saved EPS row has no 10-K line")
            line_number = cited.group(3) or cited.group(2) or cited.group(1)
            lines[i] = lines[i].rstrip(" |") + f' | 10-K line {line_number}: "GAAP diluted EPS {new}" |'
            changed = "\n".join(lines) + "\n"
        else:
            invented = reported_growth + 4
            sentence = f"Revenue growth was {invented:.2f}% from ${revenue:.3f} billion in the latest fiscal year and ${prior:.3f} billion in the prior fiscal year."
            anchor = "## Future Developments and Strategic Recommendations"
            if anchor not in text:
                raise ValueError("Expected report section in saved report")
            changed = text.replace(anchor, sentence + "\n\n" + anchor, 1)
        (target / "report.md").write_text(changed, encoding="utf-8")
        print(target)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
