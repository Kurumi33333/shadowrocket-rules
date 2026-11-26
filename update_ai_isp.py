"""Generate the Shadowrocket ISP module using MetaCubeX domain lists."""

import re
from pathlib import Path
from urllib.request import urlopen

UPSTREAM = "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite"
SERVICES = (
    ("openai", "OpenAI / Codex", "chatgpt.com"),
    ("google-gemini", "Google AI", "gemini.google.com"),
    ("meta", "Meta / Muse", "muse.ai"),
    ("anthropic", "Anthropic / Claude", "claude.ai"),
)
DOMAIN = re.compile(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")


def load_rules(name, required_domain):
    with urlopen(f"{UPSTREAM}/{name}.list", timeout=30) as response:
        lines = response.read().decode("utf-8-sig").splitlines()
    rules = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        suffix = line.startswith("+.")
        domain = line[2:] if suffix else line
        if not DOMAIN.fullmatch(domain):
            raise ValueError(f"{name}: unsupported domain rule {line!r}")
        kind = "DOMAIN-SUFFIX" if suffix else "DOMAIN"
        rules.append((kind, domain))
    if not any(
        required_domain == domain
        or (kind == "DOMAIN-SUFFIX" and required_domain.endswith("." + domain))
        for kind, domain in rules
    ):
        raise ValueError(f"{name}: expected domain {required_domain} is missing")
    return rules


def main():
    output = [
        "#!name=AI 走 ISP",
        "#!desc=OpenAI、Google AI、Meta 和 Anthropic 走 YouProxy-US",
        "",
        "# Source: https://github.com/MetaCubeX/meta-rules-dat",
        "# Converted to Shadowrocket format. See ai-isp.LICENSE.",
        "[Rule]",
    ]
    custom_domains = Path(__file__).with_name("clash").joinpath("isp-custom.list").read_text(encoding="utf-8").splitlines()
    output.extend(("", "# Custom ISP domains"))
    for domain in custom_domains:
        if not domain.startswith("+.") or not DOMAIN.fullmatch(domain[2:]):
            raise ValueError(f"Unsupported custom domain rule: {domain!r}")
        output.append(f"DOMAIN-SUFFIX,{domain[2:]},YouProxy-US")
    for name, title, domain in SERVICES:
        output.extend(("", f"# {title}"))
        output.extend(f"{kind},{host},YouProxy-US" for kind, host in load_rules(name, domain))
    target = Path(__file__).with_name("ai-isp.sgmodule")
    generated = ("\n".join(output) + "\n").encode("utf-8")
    if not target.exists() or target.read_bytes() != generated:
        target.write_bytes(generated)
        print(f"Updated {target.name}")
    else:
        print(f"{target.name} is up to date")


if __name__ == "__main__":
    main()
