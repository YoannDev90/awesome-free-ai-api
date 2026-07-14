#!/usr/bin/env python3
"""Generate PROVIDERS.md and site index.html from PROVIDERS.json."""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
PROVIDERS_PATH = CONFIG / "PROVIDERS.json"
OUTPUT_MD = CONFIG / "PROVIDERS.md"
OUTPUT_HTML = ROOT / "docs" / "index.html"
STYLE_PATH = ROOT / "docs" / "style.css"
SCRIPT_PATH = ROOT / "docs" / "script.js"
API_KEYS_DEC = Path("/tmp/api-keys.json")
TIMEOUT = 15

def slugify(n):
    return re.sub(r"[^a-z0-9]+","-",n.lower().strip()).strip("-").replace("--","-")

def global_rating(r):
    v=[r.get(k,3) for k in ("stability","model_choice","limits")]
    return round(sum(v)/len(v))

def load_keys():
    if API_KEYS_DEC.exists():
        try: return json.loads(API_KEYS_DEC.read_text())
        except: pass
    return {}

PARSERS={}
def parse_openai(d):
    return [{"id":i.get("id","?"),"context":str(i.get("context_length","?"))} for i in d.get("data",[]) if isinstance(i,dict)]
PARSERS["openai"]=parse_openai

def fetch_models(p):
    c=p.get("models")
    if not c: return []
    ep=c.get("endpoint")
    if not ep: return []
    fmt=c.get("format","openai")
    k=load_keys().get(p.get("api_key_env",""),"")
    h={}
    for a,b in (c.get("headers") or {}).items():
        h[a]=b.replace("{key}",k) if k else b
    if k and not h: h={"Authorization":f"Bearer {k}"}
    out=[]
    pg=1
    while True:
        sep="&" if "?" in ep else "?"
        url=f"{ep}{sep}page={pg}&limit=100"
        try:
            req=Request(url,headers=h)
            with urlopen(req,timeout=TIMEOUT) as r:
                data=json.loads(r.read().decode())
        except: break
        parser=PARSERS.get(fmt)
        if not parser: break
        m=parser(data)
        if not m: break
        out.extend(m)
        if len(m)<100: break
        pg+=1
    return out

def stars(n):
    return "\u2605"*n+"\u2606"*(5-n)

def gen_md(providers):
    lines=["# Provider Directory\n","Free AI inference providers with details.\n"]
    for p in providers:
        ratings=p.get("ratings",{})
        gr=global_rating(ratings)
        slug=slugify(p["name"])
        pricing=p.get("pricing_model","unknown").replace("_"," ")
        limits=p.get("limits") or "Not specified"
        caps=", ".join(p.get("capabilities",[]))
        url=p.get("url","")
        docs=p.get("docs_url") or ""
        tested=p.get("tested",False)
        last=p.get("last_checked","unknown")
        paid=p.get("tested_by")
        tested_s=f"Yes by {paid}" if paid else "Yes"
        if not tested: tested_s="No"
        test_frag=f"{tested_s} ({last})"
        note=p.get("note")
        st=f"{ratings.get('stability',3)}/5"
        mc=f"{ratings.get('model_choice',3)}/5"
        lm=f"{ratings.get('limits',3)}/5"
        com=[]
        if p.get("discord_url"): com.append(f"[Discord]({p['discord_url']})")
        if p.get("telegram_url"): com.append(f"[Telegram]({p['telegram_url']})")
        com_s=" ".join(com) if com else "None"
        models=fetch_models(p) if p.get("models") else []
        mt="| Model ID | Context |\n| --- | --- |\n"
        if models:
            for m in models:
                mt+=f"| {m['id']} | {m.get('context','?')} |\n"
        else:
            mt+="| *Not publicly listed* | *Not publicly listed* |\n"
        note_b=f"\n> {note}\n" if note else ""
        doc_s=f"\n**API docs:** [{docs}]({docs})" if docs else ""
        lines.append(f"""<details id="{slug}">
<summary><strong>{p['name']} {stars(gr)}</strong></summary>

**Global rating:** {gr}/5

| Stability | Model choice | Limits |
|-----------|-------------|--------|
| {st} | {mc} | {lm} |

**URL:** [{url}]({url}){doc_s}
**Tested:** {test_frag}
**Limits:** {limits}
**Capabilities:** {caps}
**Pricing:** {pricing}
**Community:** {com_s}
{note_b}
### Models
{mt}
</details>""")
    return "\n".join(lines)

def gen_html(providers):
    count=len(providers)
    style=STYLE_PATH.read_text() if STYLE_PATH.exists() else ""
    script=SCRIPT_PATH.read_text() if SCRIPT_PATH.exists() else ""
    cards=[]
    for p in providers:
        ratings=p.get("ratings",{})
        gr=global_rating(ratings)
        url=p.get("url","")
        docs=p.get("docs_url") or ""
        pricing=p.get("pricing_model","unknown").replace("_"," ")
        limits=p.get("limits") or "Not specified"
        caps=", ".join(p.get("capabilities",[]))
        tested=p.get("tested",False)
        last=p.get("last_checked","unknown")
        note=p.get("note")
        st=stars(ratings.get("stability",3))
        mc=stars(ratings.get("model_choice",3))
        lm=stars(ratings.get("limits",3))
        com=[]
        if p.get("discord_url"): com.append(f'<a href="{p["discord_url"]}">Discord</a>')
        if p.get("telegram_url"): com.append(f'<a href="{p["telegram_url"]}">Telegram</a>')
        com_s=" ".join(com) if com else "None"
        test_s=f'<span class="ok">Yes</span> {last}' if tested else '<span class="no">No</span>'
        note_html=f"<blockquote><p>{note}</p></blockquote>" if note else ""
        docs_link=f'<a href="{docs}" class="il">API docs</a>' if docs else ""
        models=fetch_models(p) if p.get("models") else []
        if models:
            rows="".join(f"<tr><td>{m['id']}</td><td>{m.get('context','?')}</td></tr>" for m in models)
            models_html=f"""<details class="md"><summary>Models</summary>
<table><thead><tr><th>Model ID</th><th>Context</th></tr></thead>
<tbody>{rows}</tbody></table></details>"""
        else:
            models_html='<details class="md"><summary>Models</summary><p>Not publicly listed.</p></details>'
        cards.append(f"""
<div class="c" data-n="{p['name'].lower()}" data-c="{caps.lower()}">
<div class="ch" onclick="tc(this)">
<div class="ct">{p['name']} <span class="s">{stars(gr)}</span></div>
<div class="sb"><span>Stab {st}</span><span>Choice {mc}</span><span>Limits {lm}</span></div></div>
<div class="cb" style="display:none">
<div class="cm">
<div><b>URL:</b> <a href="{url}">{url}</a> {docs_link}</div>
<div><b>Tested:</b> {test_s}</div>
<div><b>Limits:</b> {limits}</div>
<div><b>Capabilities:</b> {caps}</div>
<div><b>Pricing:</b> {pricing}</div>
<div><b>Community:</b> {com_s}</div></div>
{note_html}{models_html}</div></div>""")
    now=datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Awesome Free AI Inference APIs</title><style>{style}</style></head>
<body><div class="co"><header>
<h1>Awesome Free AI Inference APIs</h1><p class="coun">{count} providers</p>
<input type="text" id="search" class="se" onkeyup="filterCards()" placeholder="Search..." autofocus>
<p id="noResults" style="display:none">No providers found.</p></header>
<main id="list">{''.join(cards)}</main>
<footer><p>Data from <a href="https://github.com/YoannDev90/awesome-free-ai-api">awesome-free-ai-api</a> &mdash; {now}</p></footer></div>
<script>{script}</script></body></html>"""

def main():
    args=set(sys.argv[1:])
    if not PROVIDERS_PATH.exists():
        print(f"Missing {PROVIDERS_PATH}",file=sys.stderr); sys.exit(1)
    providers=json.loads(PROVIDERS_PATH.read_text())["providers"]
    do_md="--site" not in args
    do_html="--site" in args or "--all" in args
    if do_md:
        OUTPUT_MD.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT_MD.write_text(gen_md(providers))
        print(f"MD  -> {OUTPUT_MD}")
    if do_html:
        OUTPUT_HTML.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT_HTML.write_text(gen_html(providers))
        print(f"HTML -> {OUTPUT_HTML}")

if __name__=="__main__":
    main()
