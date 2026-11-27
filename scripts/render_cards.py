#!/usr/bin/env python3
"""Render animated SVG profile cards for Prathmesh Upadhyay (@prathamxeth)."""

import base64
import html
import io
import json
import os
from datetime import datetime
from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont

STATIC = os.getenv("STATIC", "0") == "1"

THEME = {
    "bg": "#090B10",
    "surface": "#0E121B",
    "surface_alt": "#151A26",
    "border": "#22293A",
    "border_hi": "#323C54",
    "ink": "#F4F5F8",
    "ink_muted": "#949DB2",
    "ink_dim": "#5E677D",
    "indigo": "#6366F1",
    "indigo_soft": "#818CF8",
    "amber": "#F59E0B",
    "emerald": "#10B981",
    "cyan": "#06B6D4",
    "levels": {
        "NONE": "#161B26",
        "FIRST_QUARTILE": "#26295E",
        "SECOND_QUARTILE": "#3E429E",
        "THIRD_QUARTILE": "#6366F1",
        "FOURTH_QUARTILE": "#9396FF",
    },
}

DELAYS = {
    "hero": 0.00,
    "tiles": 0.30,
    "graph": 0.60,
    "monthly": 1.05,
    "repo_0": 1.40,
    "repo_1": 1.62,
    "repo_2": 1.84,
    "repo_3": 2.06,
}

FLAGSHIP_SPECS = [
    {
        "name": "nexus-ide",
        "category": "GRAPH-RAG & AGENTIC AI",
        "accent": "#818CF8",
        "description": "Graph-Native Agentic IDE powered by FalkorDB & FastMCP. Multi-hop AST blast radius (<2ms) & episodic memory.",
        "language": "TypeScript",
        "language_color": "#3178C6",
        "stars": 0,
        "forks": 0,
        "topics": ["FalkorDB", "FastMCP", "Tree-sitter", "Next.js 16"],
    },
    {
        "name": "LiveScript",
        "category": "MACOS AUDIO INTELLIGENCE",
        "accent": "#F59E0B",
        "description": "Dynamic Notch Audio Transcription & Neural Translation for macOS with live waveform visualizers.",
        "language": "Swift",
        "language_color": "#FA7343",
        "stars": 0,
        "forks": 0,
        "topics": ["macOS 14+", "Swift 6.0", "Apple Silicon", "Audio Pipeline"],
    },
    {
        "name": "PALZEE-ANDROID",
        "category": "NATIVE ANDROID PLATFORM",
        "accent": "#10B981",
        "description": "High-throughput privacy-first mobile media platform with zero-latency keyframes & Media3 pipelines.",
        "language": "Kotlin",
        "language_color": "#A97BFF",
        "stars": 0,
        "forks": 0,
        "topics": ["Kotlin 2.0", "Jetpack Compose", "CameraX", "Supabase"],
    },
    {
        "name": "palzee-ios",
        "category": "NATIVE IOS SYSTEM",
        "accent": "#06B6D4",
        "description": "Native iOS client with liquid interface architecture, backdrop blur layers & local-first state sync.",
        "language": "Swift",
        "language_color": "#F05138",
        "stars": 0,
        "forks": 0,
        "topics": ["iOS 17+", "SwiftUI", "Liquid UI", "TypeScript"],
    },
]


def subset_font_to_woff_b64(ttf_path: str, text_corpus: str) -> str | None:
    if not os.path.exists(ttf_path):
        return None
    font = TTFont(ttf_path)
    options = Options()
    options.flavor = "woff"
    options.layout_features = ["*"]
    subsetter = Subsetter(options=options)
    subsetter.populate(text=text_corpus)
    subsetter.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def build_font_css(corpus: str) -> str:
    display_b64 = subset_font_to_woff_b64("fonts/SpaceGrotesk-Bold.ttf", corpus)
    mono_b64 = subset_font_to_woff_b64("fonts/JetBrainsMono-Regular.ttf", corpus)

    rules = []
    if display_b64:
        rules.append(
            f"@font-face {{ font-family: 'BrandDisplay'; "
            f"src: url('data:font/woff;base64,{display_b64}') format('woff'); "
            f"font-weight: 700; font-style: normal; }}"
        )
    if mono_b64:
        rules.append(
            f"@font-face {{ font-family: 'BrandMono'; "
            f"src: url('data:font/woff;base64,{mono_b64}') format('woff'); "
            f"font-weight: 400; font-style: normal; }}"
        )
    return "\n    ".join(rules)


def base_style(font_css: str, extra_css: str = "") -> str:
    static_override = ""
    if STATIC:
        static_override = """
    *, *::before, *::after {
      animation: none !important;
      transition: none !important;
      opacity: 1 !important;
      transform: none !important;
    }"""

    return f"""<style>
    {font_css}
    .font-display {{ font-family: 'BrandDisplay', 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .font-mono {{ font-family: 'BrandMono', 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace; }}

    @keyframes cardEnter {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulseDot {{
      0%, 100% {{ opacity: 1; }}
      50%      {{ opacity: 0.35; }}
    }}
    @keyframes scanRow {{
      from {{ opacity: 0; transform: translateX(-6px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}

    .card-enter {{
      opacity: 0;
      animation: cardEnter 0.55s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    .pulse {{
      animation: pulseDot 2.2s ease-in-out infinite;
    }}
    {extra_css}
    {static_override}

    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        animation: none !important;
        transition: none !important;
        opacity: 1 !important;
        transform: none !important;
      }}
    }}
  </style>"""


def esc(val: object) -> str:
    return html.escape(str(val), quote=True)


def render_hero(font_css: str) -> str:
    d = DELAYS["hero"]
    ascii_banner = [
        " ____  ____     _  _____ _   _    _    __  __ ",
        "|  _ \\|  _ \\   / \\|_   _| | | |  / \\  |  \\/  |",
        "| |_) | |_) | / _ \\ | | | |_| | / _ \\ | |\\/| |",
        "|  __/|  _ < / ___ \\| | |  _  |/ ___ \\| |  | |",
        "|_|   |_| \\_\\_/   \\_\\_| |_| |_/_/   \\_\\_|  |_|",
    ]
    banner_svg = []
    for idx, line in enumerate(ascii_banner):
        row_delay = d + 0.14 + idx * 0.055
        y = 74 + idx * 16
        banner_svg.append(
            f'<text x="588" y="{y}" class="font-mono ascii-row" '
            f'style="animation-delay:{row_delay:.2f}s" '
            f'fill="{THEME["indigo_soft"]}" font-size="9.6" xml:space="preserve">{esc(line)}</text>'
        )

    extra = """
    .ascii-row {
      opacity: 0;
      animation: scanRow 0.35s ease-out forwards;
    }
    """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 226" width="900" height="226" role="img" aria-label="Prathmesh Upadhyay Hero Card">
  {base_style(font_css, extra)}
  <g class="card-enter" style="animation-delay:{d:.2f}s">
    <rect x="0.5" y="0.5" width="899" height="225" rx="14" fill="{THEME['surface']}" stroke="{THEME['border']}" />

    <circle cx="32" cy="34" r="4.5" fill="{THEME['indigo']}" class="pulse" />
    <text x="45" y="38" class="font-mono" fill="{THEME['ink_muted']}" font-size="11" letter-spacing="0.8">
      SYSTEMS &amp; FULL-STACK ENGINEER · CTO @ PALZEE &amp; FINREIN · IIT MADRAS
    </text>

    <text x="30" y="90" class="font-display" fill="{THEME['ink']}" font-size="38" font-weight="700" letter-spacing="-0.8">
      Prathmesh Upadhyay
    </text>

    <text x="30" y="122" class="font-mono" fill="{THEME['ink_muted']}" font-size="12.5">
      Architecting graph-native AI systems, native mobile platforms &amp; macOS notch engines.
    </text>

    <g transform="translate(30, 148)">
      <rect x="0" y="0" width="128" height="26" rx="6" fill="{THEME['surface_alt']}" stroke="{THEME['border_hi']}" />
      <text x="12" y="17" class="font-mono" fill="{THEME['indigo_soft']}" font-size="11">FalkorDB · MCP</text>

      <rect x="136" y="0" width="136" height="26" rx="6" fill="{THEME['surface_alt']}" stroke="{THEME['border_hi']}" />
      <text x="148" y="17" class="font-mono" fill="{THEME['emerald']}" font-size="11">Kotlin · Compose</text>

      <rect x="280" y="0" width="126" height="26" rx="6" fill="{THEME['surface_alt']}" stroke="{THEME['border_hi']}" />
      <text x="292" y="17" class="font-mono" fill="{THEME['amber']}" font-size="11">Swift · macOS</text>

      <rect x="414" y="0" width="126" height="26" rx="6" fill="{THEME['surface_alt']}" stroke="{THEME['border_hi']}" />
      <text x="426" y="17" class="font-mono" fill="{THEME['cyan']}" font-size="11">Next.js · TS</text>
    </g>

    <rect x="574" y="26" width="298" height="174" rx="10" fill="{THEME['bg']}" stroke="{THEME['border_hi']}" />
    <text x="588" y="45" class="font-mono" fill="{THEME['ink_dim']}" font-size="10">prathamxeth@system:~$ neofetch</text>
    {''.join(banner_svg)}
    <text x="588" y="172" class="font-mono" fill="{THEME['ink_muted']}" font-size="9.5">Deterministic Graphs &gt; Probabilistic Guessing</text>
    <text x="588" y="187" class="font-mono" fill="{THEME['indigo']}" font-size="9.5">Kanpur &amp; Lucknow, IN · UTC+5:30</text>
  </g>
</svg>"""


def render_tile(font_css: str, tag: str, title: str, subtitle: str, accent: str, index: int) -> str:
    d = DELAYS["tiles"] + index * 0.11
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 290 112" width="290" height="112" role="img" aria-label="{esc(title)}">
  {base_style(font_css)}
  <g class="card-enter" style="animation-delay:{d:.2f}s">
    <rect x="0.5" y="0.5" width="289" height="111" rx="12" fill="{THEME['surface']}" stroke="{THEME['border']}" />
    <rect x="0.5" y="0.5" width="5" height="111" rx="2.5" fill="{accent}" />

    <text x="20" y="29" class="font-mono" fill="{accent}" font-size="10.5" letter-spacing="1.1">{esc(tag)}</text>
    <text x="270" y="29" class="font-mono" fill="{THEME['ink_dim']}" font-size="13" text-anchor="end">↗</text>

    <text x="20" y="60" class="font-display" fill="{THEME['ink']}" font-size="21" font-weight="700" letter-spacing="-0.3">
      {esc(title)}
    </text>

    <text x="20" y="85" class="font-mono" fill="{THEME['ink_muted']}" font-size="11.5">
      {esc(subtitle)}
    </text>
  </g>
</svg>"""


def render_contribution_graph(data: dict, font_css: str) -> str:
    d = DELAYS["graph"]
    weeks = data.get("weeks", [])[-52:]
    total = data.get("total_contributions", 0)

    cell = 13
    gap = 3.2
    start_x = 30
    start_y = 58

    rects = []
    for w_idx, week in enumerate(weeks):
        x = start_x + w_idx * (cell + gap)
        col_delay = d + 0.15 + (w_idx / max(len(weeks), 1)) * 0.65
        for day_idx, day in enumerate(week.get("contributionDays", [])):
            y = start_y + day_idx * (cell + gap)
            lvl = day.get("contributionLevel", "NONE")
            fill = THEME["levels"].get(lvl, THEME["levels"]["NONE"])
            if STATIC:
                rects.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.8" fill="{fill}" />'
                )
            else:
                rects.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="2.8" fill="{fill}" opacity="0">'
                    f'<animate attributeName="opacity" from="0" to="1" dur="0.28s" begin="{col_delay:.2f}s" fill="freeze" />'
                    f'</rect>'
                )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 198" width="900" height="198" role="img" aria-label="GitHub Contribution Graph">
  {base_style(font_css)}
  <g class="card-enter" style="animation-delay:{d:.2f}s">
    <rect x="0.5" y="0.5" width="899" height="197" rx="14" fill="{THEME['surface']}" stroke="{THEME['border']}" />

    <text x="30" y="34" class="font-mono" fill="{THEME['ink_muted']}" font-size="11.5" letter-spacing="0.8">
      CONTRIBUTION MATRIX · LAST 52 WEEKS
    </text>
    <text x="870" y="34" class="font-mono" fill="{THEME['indigo_soft']}" font-size="12" text-anchor="end">
      {total:,} CONTRIBUTIONS
    </text>

    {''.join(rects)}

    <text x="748" y="182" class="font-mono" fill="{THEME['ink_dim']}" font-size="10">LESS</text>
    <rect x="780" y="173" width="10" height="10" rx="2" fill="{THEME['levels']['NONE']}" />
    <rect x="794" y="173" width="10" height="10" rx="2" fill="{THEME['levels']['FIRST_QUARTILE']}" />
    <rect x="808" y="173" width="10" height="10" rx="2" fill="{THEME['levels']['SECOND_QUARTILE']}" />
    <rect x="822" y="173" width="10" height="10" rx="2" fill="{THEME['levels']['THIRD_QUARTILE']}" />
    <rect x="836" y="173" width="10" height="10" rx="2" fill="{THEME['levels']['FOURTH_QUARTILE']}" />
    <text x="852" y="182" class="font-mono" fill="{THEME['ink_dim']}" font-size="10">MORE</text>
  </g>
</svg>"""


def render_monthly_chart(data: dict, font_css: str) -> str:
    d = DELAYS["monthly"]
    stats = data.get("stats", {})
    months = stats.get("months", [])[-12:]
    max_val = max((m["count"] for m in months), default=1) or 1

    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    active_days = stats.get("active_days", 0)
    busiest = stats.get("busiest_day", {"date": "N/A", "count": 0})
    busiest_label = busiest["date"]
    if busiest_label != "N/A":
        try:
            busiest_label = datetime.strptime(busiest_label, "%Y-%m-%d").strftime("%d %b")
        except ValueError:
            pass

    chart_x = 30
    chart_bottom = 178
    max_bar_h = 92
    bar_w = 34
    bar_gap = 12

    bars = []
    for idx, m in enumerate(months):
        x = chart_x + idx * (bar_w + bar_gap)
        ratio = m["count"] / max_val
        h = max(4, round(ratio * max_bar_h))
        y = chart_bottom - h
        is_peak = m["count"] == max_val and m["count"] > 0
        fill = THEME["indigo"] if is_peak else THEME["border_hi"]
        bar_delay = d + 0.18 + idx * 0.04

        if STATIC:
            bars.append(
                f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" rx="4" fill="{fill}" />'
            )
        else:
            bars.append(
                f'<rect x="{x}" y="{chart_bottom}" width="{bar_w}" height="0" rx="4" fill="{fill}">'
                f'<animate attributeName="y" from="{chart_bottom}" to="{y}" dur="0.45s" begin="{bar_delay:.2f}s" fill="freeze" />'
                f'<animate attributeName="height" from="0" to="{h}" dur="0.45s" begin="{bar_delay:.2f}s" fill="freeze" />'
                f'</rect>'
            )

        bars.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{y - 6}" class="font-mono" fill="{THEME["ink_muted"]}" font-size="9.5" text-anchor="middle">{m["count"]}</text>'
        )
        bars.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{chart_bottom + 16}" class="font-mono" fill="{THEME["ink_dim"]}" font-size="10" text-anchor="middle">{esc(m["label"])}</text>'
        )

    kpi_x = 610
    kpis = [
        ("CURRENT STREAK", f"{streak}d", f"LONGEST {longest}d", THEME["indigo_soft"]),
        ("ACTIVE DAYS", f"{active_days}", "LAST 365 DAYS", THEME["emerald"]),
        ("BUSIEST DAY", f"{busiest['count']} commits", busiest_label.upper(), THEME["amber"]),
    ]
    kpi_svg = []
    for idx, (label, val, sub, color) in enumerate(kpis):
        ky = 56 + idx * 48
        kpi_svg.append(
            f'<rect x="{kpi_x}" y="{ky - 16}" width="260" height="40" rx="8" fill="{THEME["bg"]}" stroke="{THEME["border"]}" />'
            f'<text x="{kpi_x + 12}" y="{ky + 2}" class="font-mono" fill="{THEME["ink_muted"]}" font-size="10">{label}</text>'
            f'<text x="{kpi_x + 12}" y="{ky + 16}" class="font-mono" fill="{THEME["ink_dim"]}" font-size="9.5">{sub}</text>'
            f'<text x="{kpi_x + 248}" y="{ky + 9}" class="font-display" fill="{color}" font-size="16" font-weight="700" text-anchor="end">{esc(val)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 212" width="900" height="212" role="img" aria-label="Monthly Contributions and Streak Stats">
  {base_style(font_css)}
  <g class="card-enter" style="animation-delay:{d:.2f}s">
    <rect x="0.5" y="0.5" width="899" height="211" rx="14" fill="{THEME['surface']}" stroke="{THEME['border']}" />

    <text x="30" y="34" class="font-mono" fill="{THEME['ink_muted']}" font-size="11.5" letter-spacing="0.8">
      MONTHLY VELOCITY · PEAK IN BRAND INDIGO
    </text>

    {''.join(bars)}
    {''.join(kpi_svg)}
  </g>
</svg>"""


def render_repo_card(repo: dict, font_css: str, index: int) -> str:
    d = DELAYS[f"repo_{index}"]
    name = repo.get("name", "Repository")
    category = repo.get("category", f"FLAGSHIP SYSTEM // 0{index + 1}")
    accent = repo.get("accent", THEME["indigo_soft"])
    desc = repo.get("description", "")
    lang = repo.get("language", "")
    lang_color = repo.get("language_color", THEME["indigo"])
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)
    topics = repo.get("topics", [])[:4]

    topic_pills = []
    tx = 30
    for t in topics:
        w = len(t) * 7.2 + 20
        topic_pills.append(
            f'<rect x="{tx}" y="102" width="{w:.1f}" height="22" rx="5" fill="{THEME["bg"]}" stroke="{THEME["border_hi"]}" />'
            f'<text x="{tx + 10}" y="116" class="font-mono" fill="{THEME["ink_muted"]}" font-size="10.5">{esc(t)}</text>'
        )
        tx += w + 8

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 142" width="900" height="142" role="img" aria-label="Featured Repository {esc(name)}">
  {base_style(font_css)}
  <g class="card-enter" style="animation-delay:{d:.2f}s">
    <rect x="0.5" y="0.5" width="899" height="141" rx="14" fill="{THEME['surface']}" stroke="{THEME['border']}" />
    <rect x="0.5" y="0.5" width="5" height="141" rx="2.5" fill="{esc(accent)}" />

    <text x="30" y="34" class="font-mono" fill="{esc(accent)}" font-size="10.5" letter-spacing="1.1">
      0{index + 1} // {esc(category)}
    </text>

    <text x="30" y="64" class="font-display" fill="{THEME['ink']}" font-size="22" font-weight="700">
      prathamxeth/{esc(name)}
    </text>

    <text x="30" y="88" class="font-mono" fill="{THEME['ink_muted']}" font-size="12">
      {esc(desc[:96])}
    </text>

    {''.join(topic_pills)}

    <circle cx="730" cy="58" r="5" fill="{esc(lang_color)}" />
    <text x="742" y="62" class="font-mono" fill="{THEME['ink']}" font-size="12">{esc(lang)}</text>
    <text x="870" y="62" class="font-mono" fill="{THEME['ink_muted']}" font-size="12" text-anchor="end">
      ★ {stars} · ⑂ {forks}
    </text>
    <text x="870" y="116" class="font-mono" fill="{esc(accent)}" font-size="11.5" text-anchor="end">
      EXPLORE REPO ↗
    </text>
  </g>
</svg>"""


def main():
    os.makedirs("cards", exist_ok=True)

    if os.path.exists("data/contributions.json"):
        with open("data/contributions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "total_contributions": 640,
            "weeks": [],
            "stats": {
                "active_days": 148,
                "current_streak": 12,
                "longest_streak": 28,
                "busiest_day": {"date": "2026-10-18", "count": 19},
                "months": [
                    {"label": m, "count": c}
                    for m, c in zip(
                        ["DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"],
                        [32, 45, 38, 51, 60, 48, 55, 42, 67, 74, 82, 46],
                    )
                ],
            },
            "featured_repos": [],
        }

    api_repos = {r["name"].lower(): r for r in data.get("featured_repos", [])}
    repos = []
    for spec in FLAGSHIP_SPECS:
        live = api_repos.get(spec["name"].lower(), {})
        merged = {
            **spec,
            "stars": live.get("stars", spec["stars"]),
            "forks": live.get("forks", spec["forks"]),
            "language": live.get("language") or spec["language"],
            "language_color": live.get("language_color") or spec["language_color"],
            "description": live.get("description") or spec["description"],
            "topics": live.get("topics") or spec["topics"],
        }
        repos.append(merged)

    corpus = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        " ·•@/:_-+*=<>#%~^\\|()[]{}.,!?&★⑂↗$"
    )
    font_css = build_font_css(corpus)

    outputs = {
        "cards/hero.svg": render_hero(font_css),
        "cards/tile-portfolio.svg": render_tile(
            font_css, "01 // PORTFOLIO", "prathamxeth.dev", "Architecture & Case Studies", THEME["indigo_soft"], 0
        ),
        "cards/tile-linkedin.svg": render_tile(
            font_css, "02 // NETWORK", "LinkedIn", "Prathmesh Upadhyay", THEME["emerald"], 1
        ),
        "cards/tile-x.svg": render_tile(
            font_css, "03 // DISPATCH", "X / @0xBlurr", "Systems & AI Notes", THEME["cyan"], 2
        ),
        "cards/graph.svg": render_contribution_graph(data, font_css),
        "cards/monthly.svg": render_monthly_chart(data, font_css),
        "cards/repo-nexus-ide.svg": render_repo_card(repos[0], font_css, 0),
        "cards/repo-livescript.svg": render_repo_card(repos[1], font_css, 1),
        "cards/repo-palzee-android.svg": render_repo_card(repos[2], font_css, 2),
        "cards/repo-palzee-ios.svg": render_repo_card(repos[3], font_css, 3),
    }

    for path, content in outputs.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Rendered {path} (STATIC={int(STATIC)})")


if __name__ == "__main__":
    main()
