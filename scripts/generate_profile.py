import json, os, urllib.request, urllib.error
from pathlib import Path
from collections import Counter

USER = os.getenv("GITHUB_USER", "Ali-Hassan87")
TOKEN = os.getenv("GITHUB_TOKEN", "")
OUT = Path("assets")
OUT.mkdir(exist_ok=True)
BG, PANEL, TEXT, MUTED, LIME, PURPLE = "#0D0F0C", "#171A14", "#F3F1E8", "#A4A99A", "#D9FF70", "#B9A0FF"

def api(url, method="GET", data=None):
    headers = {"Accept":"application/vnd.github+json", "User-Agent":"profile-assets-generator"}
    if TOKEN: headers["Authorization"] = f"Bearer {TOKEN}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, headers=headers, data=body, method=method)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())

def svg_card(title, subtitle, width=1000, height=240):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'<rect width="{width}" height="{height}" rx="18" fill="{BG}" stroke="#34382D"/>',
            f'<text x="34" y="42" fill="{LIME}" font-family="monospace" font-size="14" letter-spacing="3">{title}</text>',
            f'<text x="34" y="68" fill="{MUTED}" font-family="Arial" font-size="13">{subtitle}</text>']

def save(name, parts):
    parts.append("</svg>")
    (OUT/name).write_text("\n".join(parts), encoding="utf-8")

repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")
repos = [r for r in repos if not r.get("fork")]
stars = sum(r.get("stargazers_count", 0) for r in repos)
forks = sum(r.get("forks_count", 0) for r in repos)
langs = Counter()
for r in repos:
    try:
        data = api(r["languages_url"])
        langs.update(data)
    except Exception:
        pass

# Stats card
p = svg_card("GITHUB / AT A GLANCE", "Public repository data · refreshed automatically")
metrics = [("PUBLIC REPOS", str(len(repos))), ("STARS EARNED", str(stars)), ("FORKS", str(forks)), ("LANGUAGES", str(len(langs)))]
for i,(label,value) in enumerate(metrics):
    x = 40 + i*240
    p += [f'<text x="{x}" y="150" fill="{TEXT}" font-family="Arial" font-size="48" font-weight="700">{value}</text>',
          f'<text x="{x}" y="183" fill="{LIME}" font-family="monospace" font-size="12" letter-spacing="1.5">{label}</text>']
save("stats.svg", p)

# Language card
p = svg_card("THE CODE / LANGUAGE MIX", "Based on byte counts across public, non-fork repositories")
total = sum(langs.values()) or 1
top = langs.most_common(6)
x0, y0, barw, gap = 35, 112, 930, 12
cursor = x0
palette = [LIME, PURPLE, "#F5A66B", "#78C9C1", "#E78CA8", "#8BA9F4"]
for i,(name,size) in enumerate(top):
    w = max(2, barw*size/total)
    p.append(f'<rect x="{cursor:.1f}" y="{y0}" width="{w:.1f}" height="18" rx="5" fill="{palette[i%len(palette)]}"/>')
    cursor += w
cursorx = 38
for i,(name,size) in enumerate(top):
    pct = size/total*100
    col = palette[i%len(palette)]
    p += [f'<circle cx="{cursorx+5}" cy="177" r="5" fill="{col}"/>',
          f'<text x="{cursorx+17}" y="182" fill="{TEXT}" font-family="Arial" font-size="14">{name}</text>',
          f'<text x="{cursorx+17}" y="205" fill="{MUTED}" font-family="monospace" font-size="12">{pct:.1f}%</text>']
    cursorx += 155
save("languages.svg", p)

# Contribution calendar from GraphQL; gracefully show a clear status if unavailable.
weeks = []
try:
    query = """query($login:String!){user(login:$login){contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } }}"""
    result = api("https://api.github.com/graphql", "POST", {"query":query,"variables":{"login":USER}})
    cal = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    total_contrib = cal["totalContributions"]
except Exception:
    total_contrib = None

p = svg_card("THE CONTRIBUTION FIELD", "A live view of the last 12 months · GitHub contribution calendar", 1000, 245)
if weeks:
    weeks = weeks[-52:]
    maxv = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=1) or 1
    for wi,w in enumerate(weeks):
        for di,d in enumerate(w["contributionDays"]):
            n = d["contributionCount"]
            level = 0 if n == 0 else min(4, 1 + int((n/maxv)*3))
            colors = ["#242820", "#53643A", "#7F9D4A", "#AFCB5A", LIME]
            x, y = 35+wi*17.8, 91+di*20
            p.append(f'<rect x="{x:.1f}" y="{y}" width="12" height="12" rx="3" fill="{colors[level]}"><title>{d["date"]}: {n} contributions</title></rect>')
    p.append(f'<text x="965" y="222" text-anchor="end" fill="{LIME}" font-family="monospace" font-size="12">{total_contrib} CONTRIBUTIONS</text>')
else:
    p.append(f'<text x="35" y="145" fill="{TEXT}" font-family="Arial" font-size="18">Contribution calendar unavailable right now.</text>')
    p.append(f'<text x="35" y="175" fill="{MUTED}" font-family="Arial" font-size="13">The workflow will retry automatically on its next run.</text>')
save("contributions.svg", p)

print(f"Generated profile assets for {USER}: {len(repos)} public repositories, {len(langs)} languages.")
