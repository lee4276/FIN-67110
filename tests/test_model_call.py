import unittest
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch

from app import model_call
from desk import ROOT
from team import verify_folder


class RejectedKey(Exception):
    status_code = 401


class FakeResponses:
    def create(self, **kwargs):
        raise RejectedKey("secret test value")


class FakeClient:
    responses = FakeResponses()


class ModelCallTests(unittest.TestCase):
    def test_authentication_error_does_not_repeat_provider_text(self):
        with self.assertRaises(RuntimeError) as result:
            model_call(FakeClient(), "test-model", "instructions", "task", {}, "output")
        self.assertIn("401", str(result.exception))
        self.assertNotIn("secret test value", str(result.exception))

    def test_verify_only_keeps_code_marks_when_model_is_rate_limited(self):
        source = next(folder for folder in sorted((ROOT / "runs").iterdir())
                      if folder.is_dir() and (folder / "report.md").is_file() and (folder / "facts.json").is_file())
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            folder = Path(temporary)
            for file in source.iterdir():
                if file.name in {"facts.json", "report.md"} or file.suffix == ".txt":
                    shutil.copy2(file, folder / file.name)
            with patch("team.model_call", side_effect=RuntimeError("OpenAI API returned HTTP 429")):
                marks = verify_folder(folder, object(), "test-model", verify_only=True)
            self.assertEqual(set(map(str, range(1, 12))), {item["id"] for item in marks if item["id"].isdigit()})
            self.assertIn("pending: OpenAI returned HTTP 429", (folder / "verified_report.md").read_text(encoding="utf-8"))
            self.assertTrue((folder / "verify_only.log").is_file())
            self.assertFalse((folder / "node_order.log").exists())


if __name__ == "__main__":
    unittest.main()
