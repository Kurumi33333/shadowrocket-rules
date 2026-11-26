"""Generate the Mihomo classical rule list from the Shadowrocket module."""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "direct.sgmodule"
TARGET = ROOT / "clash" / "direct.list"
DOMAIN = re.compile(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
HEADER = "# Generated from direct.sgmodule by sync_direct.py; do not edit.\n# Mihomo / Clash Verge: classical rule-provider, behavior: classical.\n\n"


def render(source):
    in_rules = False
    found = False
    rules = []
    seen = set()
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(("#", ";", "//")):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_rules = line.lower() == "[rule]"
            found = found or in_rules
            continue
        if not in_rules:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Line {number}: unsupported rule: {line}")
        kind, host, policy = parts
        if kind.upper() not in ("DOMAIN", "DOMAIN-SUFFIX") or policy.upper() != "DIRECT" or not DOMAIN.fullmatch(host):
            raise ValueError(f"Line {number}: expected a domain DIRECT rule: {line}")
        rule = f"{kind.upper()},{host.lower()}"
        if rule not in seen:
            seen.add(rule)
            rules.append(rule)
    if not found or not rules:
        raise ValueError("Missing or empty [Rule] section; refusing to overwrite the list")
    return HEADER + "\n".join(rules) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if the generated list differs")
    args = parser.parse_args()
    expected = render(SOURCE.read_text(encoding="utf-8-sig")).encode("utf-8")
    current = TARGET.read_bytes() if TARGET.exists() else b""
    if current == expected:
        print("Clash DIRECT list is up to date")
    elif args.check:
        raise SystemExit("Clash DIRECT list is out of sync; run python3 sync_direct.py")
    else:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(expected)
        print("Updated clash/direct.list")


if __name__ == "__main__":
    main()
