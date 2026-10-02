"""Safety checks for JSON fixtures committed to this public repository.

These checks reduce accidental publication risk. They do not certify arbitrary
runtime records as free of PII or secrets.
"""
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"

SENSITIVE_KEY_PARTS = {
    "authorization",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "password",
    "secret",
    "customer_email",
    "customer_phone",
}


def walk(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield path, key, child
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


class PublicFixtureSafetyTests(unittest.TestCase):
    def json_fixtures(self):
        return sorted(EXAMPLES.glob("*.json"))

    def test_json_fixtures_do_not_use_sensitive_field_names(self):
        for fixture in self.json_fixtures():
            document = json.loads(fixture.read_text(encoding="utf-8"))
            for path, key, _ in walk(document):
                normalized = key.lower().replace("-", "_")
                self.assertNotIn(
                    normalized,
                    SENSITIVE_KEY_PARTS,
                    f"{fixture.name} contains sensitive-looking field {path}.{key}",
                )

    def test_raw_refs_are_reference_only(self):
        for fixture in self.json_fixtures():
            document = json.loads(fixture.read_text(encoding="utf-8"))
            for path, key, value in walk(document):
                if key != "raw_ref":
                    continue
                self.assertIsInstance(value, str, f"{fixture.name} {path}.raw_ref must be text")
                self.assertFalse(value.startswith("data:"), f"{fixture.name} embeds data in raw_ref")
                parsed = urlsplit(value)
                self.assertTrue(parsed.scheme, f"{fixture.name} raw_ref must be an explicit reference")
                self.assertFalse(parsed.username or parsed.password, f"{fixture.name} raw_ref contains userinfo")
                self.assertFalse(parsed.query, f"{fixture.name} raw_ref must not contain a query string")
                self.assertFalse(parsed.fragment, f"{fixture.name} raw_ref must not contain a fragment")


if __name__ == "__main__":
    unittest.main()
