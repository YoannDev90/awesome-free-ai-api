#!/usr/bin/env python3
"""Generate PROVIDERS.md and site index.html from PROVIDERS.json."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
PROVIDERS_PATH = CONFIG / "PROVIDERS.json"
OUTPUT_MD = CONFIG / "PROVIDERS.md"
OUTPUT_HTML = ROOT / "docs" / "index.html"
STYLE_PATH = ROOT / "docs" / "style.css"
SCRIPT_PATH = ROOT / "docs" / "script.js"
API_KEYS_DEC_PATH = Path("/tmp/api-keys.json")
TIMEOUT = 15


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    return s.strip("-").replace("--", "-")


def global_rating(ratings: dict) -> int:
    vals = [ratings.get(k, 3) for k in ("stability", "model_choice", "limits")]
    return round(sum(vals) / len(vals))


def load_api_keys() -> dict:
    if API_KEYS_DEC_PATH.exists():
        try:
            return json.loads(API_KEYS_DEC_PATH.read_text())
        except Exception:
            return {}
    return {}


PARSERS = {}


def parse_openai(data: dict) -> list:
    return [
        {"id": item.get("id", "unknown"), "context": str(item.get("context_length", "?"))}
        for item in data.get("data", [])
        if isinstance(item, dict)
    ]


PARSERS["openai"] = parse_openai


def fetch_models(prov: dict) -> list:
    cfg = prov.get("models")
    if not cfg:
        return []
    endpoint = cfg.get("endpoint")
    if not endpoint:
        return []
    fmt = cfg.get("format", "openai")
    api_keys = load_api_keys()
    api_key = api_keys.get(prov.get("api_key_env", ""), "")
    headers = {}
    raw_headers = cfg.get("headers") or {}
    for k, v in raw_headers.items():
        headers[k] = v.replace("{key}", api_key) if api_key else v
    if api_key and not headers:
        headers = {"Authorization": f"Bearer {api_key}"}
    all_models = []
    page = 1
    while True:
        sep = "&" if "?" in endpoint else "?"
        url = f"{endpoint}{sep}page={page}&limit=100"
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=TIMEOUT) as r:
                result = json.loads(r.read().decode())
        except Exception:
            break
        parser = PARSERS.get(fmt)
        if not parser:
            break
        models = parser(result)
        if not models:
            break
        all_models.extend(models)
        if len(models) < 100:
            break
        page += 1
    return all_models


def stars_str(n: int) -> str:
    s = chr(0x2605) * n + chr(0x2606) * (5 - n)
    return s


# ---------- MD ----------

def gen_md_provider(text: str, prov: dict) -> str:
    ratings = prov.get("ratings", {})
    gr = global_rating(ratings)
    slug = slugify(prov["name"])
    pricing = prov.get("pricing_model", "unknown").replace("_", " ")
    limits = prov.get("limits") or "Not specified"
    capabilities = ", ".join(prov.get("capabilities", []))
    url = prov.get("url", "")
    docs = prov.get("docs_url") or ""
    tested = prov.get("tested", False)
    last_checked = prov.get("last_checked", "unknown")
    paid_by = prov.get("tested_by")
    tested_str = f"Yes by {paid_by}" if paid_by else "Yes"
    if not tested:
        tested_str = "No"
    test_fragment = f"{tested_str} ({last_checked})"
    note = prov.get("note")
    stability = f"{ratings.get('stability', 3)}/5"
    model_choice = f"{ratings.get('model_choice', 3)}/5"
    lim = f"{ratings.get('limits', 3)}/5"

    community = []
    if prov.get("discord_url"):
        community.append(f"[Discord]({prov['discord_url']})")
    if prov.get("telegram_url"):
        community.append(f"[Telegram]({prov['telegram_url']})")
    com = " ".join(community) if community else "None"

    models = fetch_models(prov) if prov.get("models") else []

    model_table = "| Model ID | Context |\n| --- | --- |\n"
    if models:
        for m in models:
            model_table += f"| {m['id']} | {m.get('context', '?')} |\n"
    else:
        model_table += "| *Not publicly listed* | *Not publicly listed* |\n"

    note_block = f"\n> {note}\n" if note else ""

    return f"""<details id="{slug}">
<summary><strong>{prov['name']} {stars_str(gr)}</strong></summary>

**Global rating:** {gr}/5

| Stability | Model choice | Limits |
|-----------|-------------|--------|
| {stability} | {model_choice} | {lim} |

**URL:** [{url}]({url})
**API docs:** [{docs}]({docs})
**Tested:** {test_fragment}
**Limits:** {limits}
**Capabilities:** {capabilities}
**Pricing:** {pricing}
**Community:** {com}
{note_block}
### Models
{model_table}
</details>"""


def gen_md(providers: list) -> str:
    lines = ["# Provider Directory\n", "Free AI inference providers with details.\n"]
    for p in providers:
        lines.append(gen_md_provider(p))
    return "\n".join(lines)


# ---------- HTML ----------

def gen_html_provider(prov: dict) -> str:
    name = prov["name"]
    ratings = prov.get("ratings", {})
    gr = global_rating(ratings)
    caps = ", ".join(prov.get("capabilities", []))
    url = prov.get("url", "")
    docs = prov.get("docs_url") or ""
    pricing = prov.get("pricing_model", "unknown").replace("_", " ")
    limits = prov.get("limits") or "Not specified"
    tested = prov.get("tested", False)
    last_checked = prov.get("last_checked", "unknown")
    note = prov.get("note")

    stability = ratings.get("stability", 3)
    mchoice = ratings.get("model_choice", 3)
    lim = ratings.get("limits", 3)

    st_str = stars_str(stability)
    md_str = stars_str(mchoice)
    lim_str = stars_str(lim)

    community = []
    if prov.get("discord_url"):
        community.append(f'<a href="{prov["discord_url"]}">Discord</a>')
    if prov.get("telegram_url"):
        community.append(f'<a href="{prov["telegram_url"]}">Telegram</a>')
    com = " ".join(community) if community else "None"

    tested_str = f'<span class="ok">Yes</span> {last_checked}' if tested else '<span class="no">No</span>'

    models = fetch_models(prov) if prov.get("models") else []
    models_html = ""
    if models:
        rows = "".join(f"<tr><td>{m['id']}</td><td>{m.get('context', '?')}</td></tr>" for m in models)
        models_html = f"""\n      <details class="md">
        <summary>Models</summary>
        <table><thead><tr><th>Model ID</th><th>Context</th></tr></thead>
        <tbody>{rows}</tbody></table>
      </details>"""
    else:
        models_html = """\n      <details class="md">
        <summary>Models</summary>
        <p>Not publicly listed.</p>
      </details>"""

    note_html = f"<blockquote><p>{note}</p></blockquote>" if note else ""

    docs_link = f'<a href="{docs}" class="il">API docs</a>' if docs else ""

    return f"""
    <div class="c" data-n="{name.lower()}" data-c="{caps.lower()}">
      <div class="ch" onclick="tc(this)">
        <div class="ct">{name} <span class="s">{stars_str(gr)}</span></div>
        <div class="sb">
          <span>Stab {st_str}</span>
          <span>Choice {md_str}</span>
          <span>Limits {lim_str}</span>
        </div>
      </div>
      <div class="cb" style="display:none">
        <div class="cm">
          <div><b>URL:</b> <a href="{url}">{url}</a> {docs_link}</div>
          <div><b>Tested:</b> {tested_str}</div>
          <div><b>Limits:</b> {limits}</div>
          <div><b>Capabilities:</b> {caps}</div>
          <div><b>Pricing:</b> {pricing}</div>
          <div><b>Community:</b> {com}</div>
        </div>
        {note_html}
        {models_html}
      </div>
    </div>"""


def gen_html(providers: list) -> str:
    count = len(providers)

    style = STYLE_PATH.read_text() if STYLE_PATH.exists() else "/* no style */"
    script = SCRIPT_PATH.read_text() if SCRIPT_PATH.exists() else "function tc(e){var b=e.nextElementSibling;b.style.display=b.style.display==='none'?'block':'none'}function filterCards(){var q=document.getElementById('search').value.toLowerCase();var cards=document.querySelectorAll('.c');var visible=0;cards.forEach(function(c){if(c.dataset.n.indexOf(q)>-1||c.dataset.c.indexOf(q)>-1){c.style.display='';visible++}else{c.style.display='none'}});document.getElementById('noResults').style.display=visible>0?'none':'block'}document.addEventListener('DOMContentLoaded',function(){var params=new URLSearchParams(window.location.search);var p=params.get('provider');if(p){var el=document.querySelector('.c[data-n*=\"'+p.toLowerCase()+'\"]');if(el){el.querySelector('.ch').click();el.scrollIntoView({behavior:'smooth'})}}})"

    cards = "\n".join(gen_html_provider(p) for p in providers)
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Awesome Free AI Inference APIs</title>
<style>{style}</style>
</head>
<body>
<div class="co">
<header>
<h1>Awesome Free AI Inference APIs</h1>
<p class="coun">{count} providers</p>
<input type="text" id="search" class="se" onkeyup="filterCards()" placeholder="Search..." autofocus>
<p id="noResults" style="display:none">No providers found.</p>
</header>
<main id="list">{cards}</main>
<footer>
<p>Data from <a href="https://github.com/YoannDev90/awesome-free-ai-api">awesome-free-ai-api</a> &mdash; {now}</p>
</footer>
</div>
<script>{script}</script>
</body>
</html>"""


# ---------- MAIN ----------

def main() -> None:
    args = set(sys.argv[1:])

    if not PROVIDERS_PATH.exists():
        print(f"Missing {PROVIDERS_PATH}", file=sys.stderr)
        sys.exit(1)

    providers = json.loads(PROVIDERS_PATH.read_text())["providers"]

    do_md = "--site" not in args
    do_html = "--site" in args or "--all" in args

    if do_md:
        OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_MD.write_text(gen_md(providers))
        print(f"MD  -> {OUTPUT_MD}")

    if do_html:
        OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_HTML.write_text(gen_html(providers))
        print(f"HTML -> {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
