"""Собирает доклад из content.html в две версии.

  python3 build.py        → ../Сколько_стоит_достойная_жизнь_доклад_2026.pdf и web/index.html

PDF печатается через Chromium (путь можно задать переменной CHROME).
Веб-версия — фрагмент страницы для публикации (без <html>/<body>), шрифты из Google Fonts.
"""
import glob
import os
import re
import subprocess

import figures

HERE = os.path.dirname(os.path.abspath(__file__))
COVER_NOTE = ("<b>Редакция 4, октябрь 2026.</b> Текст переписан целиком; все данные заново сверены с источниками, "
              "главные цифры — с первоисточником НИУ ВШЭ. Список изменений — в приложении Б.")
WEB_META = "Редакция 4 · октябрь 2026 · 53 источника"
TITLE = "Сколько стоит достойная жизнь"
SUBTITLE = ("Реформа психоневрологических интернатов: сколько стоит месяц жизни человека в интернате и в квартире, "
            "что показал мировой опыт и что можно сделать в российском регионе на имеющиеся деньги")

# Палитра и шрифты: одна система для PDF и для веб-версии.
TOKENS = """
  /* Длинное чтение: одна колонка текста ~68 знаков, графики и таблицы шире. */
  --paper: #f8f9f7; --ink: #1c2422; --mute: #5e6b67; --rule: #d9dfdc; --grid: #e4e9e6; --panel: #eef2ef;
  --accent: #1f5560;
  --c1: #46637d; --c2: #3a7c5b; --c3: #b8c5ce; --c4: #a8761a; --c5: #a5463a;
  --f-text: 'Literata', 'PT Serif', Georgia, serif;
  --f-ui: 'Golos Text', 'Segoe UI', system-ui, sans-serif;
"""
DARK = """
  --paper: #121615; --ink: #e2e8e5; --mute: #9aa7a2; --rule: #2e3835; --grid: #29322f; --panel: #1a201e;
  --accent: #8cc3cc;
  --c1: #8db0cd; --c2: #7cc29c; --c3: #4b5b66; --c4: #dfb25c; --c5: #e38c7d;
  color-scheme: dark;
"""

SHARED_CSS = """
.k-ink{fill:var(--ink)} .k-mute{fill:var(--mute)} .k-grid{stroke:var(--grid)} .k-gridf{fill:var(--rule)}
.k-inkline{stroke:var(--ink)}
.s1{fill:var(--c1)} .s2{fill:var(--c2)} .s3{fill:var(--c3)} .s4{fill:var(--c4)} .s5{fill:var(--c5)}
.s1-line{stroke:var(--c1);fill:none} .s2-line{stroke:var(--c2);fill:none} .s4-line{stroke:var(--c4);fill:none} .s5-line{stroke:var(--c5);fill:none}
.s1-text{fill:var(--c1)} .s2-text{fill:var(--c2)} .s4-text{fill:var(--c4)} .s5-text{fill:var(--c5)}
figure svg{width:100%;height:auto;display:block}
.eyebrow{font-family:var(--f-ui);font-size:.72em;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600;margin:0 0 .4em}
h2,h3{font-family:var(--f-text);text-wrap:balance;color:var(--ink)}
h2{font-weight:600;letter-spacing:-.01em;line-height:1.15}
h3{font-weight:600;line-height:1.25}
.lede{font-size:1.12em;line-height:1.55;color:var(--ink);font-style:italic}
.dag{color:var(--c4);font-weight:600}
a.ref{font-family:var(--f-ui);font-size:.72em;color:var(--mute);text-decoration:none;vertical-align:.35em;white-space:nowrap}
a.ref:hover{color:var(--accent)}
.tbl{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-family:var(--f-ui);font-size:.82em;line-height:1.4;font-variant-numeric:tabular-nums}
caption{text-align:left;font-weight:600;padding-bottom:.5em;caption-side:top}
th{text-align:left;font-weight:600;border-bottom:1.5px solid var(--ink);background:var(--panel)}
th,td{padding:.5em .65em;vertical-align:top;border-bottom:1px solid var(--rule)}
td.n,th.n{text-align:right;white-space:nowrap}
figure{margin:1.6em 0}
figcaption{font-family:var(--f-ui);font-size:.78em;color:var(--mute);margin-top:.5em;line-height:1.4}
.note{background:var(--panel);border-left:3px solid var(--accent);padding:.9em 1.1em;margin:1.4em 0}
.note.warn{border-left-color:var(--c4)}
.note p:last-child,.note ul:last-child{margin-bottom:0}
.note-t{font-family:var(--f-ui);font-size:.74em;letter-spacing:.1em;text-transform:uppercase;color:var(--mute);font-weight:600;margin:0 0 .4em}
.take{border-top:1px solid var(--rule);padding-top:.7em;margin-top:1em}
.take b{font-family:var(--f-ui);font-size:.82em;letter-spacing:.06em;text-transform:uppercase;color:var(--c2)}
.kpi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.9em;margin:1.2em 0}
.kpi div{border-top:2px solid var(--accent);padding-top:.5em}
.kpi b{display:block;font-family:var(--f-text);font-size:1.7em;font-weight:600;color:var(--accent);line-height:1.1;font-variant-numeric:tabular-nums}
.kpi span{display:block;font-family:var(--f-ui);font-size:.74em;color:var(--mute);line-height:1.35;margin-top:.35em}
.theses li{margin-bottom:.6em}
.coda{font-size:1.08em;font-style:italic;border-top:1px solid var(--rule);padding-top:1em;margin-top:2em}
.src{font-family:var(--f-ui);font-size:.8em;line-height:1.45}
.src li{margin-bottom:.45em;overflow-wrap:anywhere}
code{font-family:'DejaVu Sans Mono',ui-monospace,monospace;font-size:.85em;background:var(--panel);padding:0 .25em}
"""


def load_content():
    html = open(os.path.join(HERE, "content.html"), encoding="utf-8").read()
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)

    def ref(m):
        nums = [n.strip() for n in m.group(1).split(",")]
        return '<a class="ref" href="#src-{0}">[{1}]</a>'.format(nums[0], ", ".join(nums))
    html = re.sub(r"\{(\d+(?:\s*,\s*\d+)*)\}", ref, html)

    def fig(m):
        key = m.group(1)
        return f'<figure data-fig="{key}">{figures.FIGURES[key]()}'
    html = re.sub(r'<figure data-fig="(\w+)">', fig, html)
    return html


def toc(html):
    items = re.findall(r'<section class="(?:part|front|appx)" id="([\w-]+)">\s*<p class="eyebrow">(.*?)</p>\s*<h2>(.*?)</h2>', html)
    return "".join(f'<li><a href="#{i}"><span>{e}</span> {t}</a></li>' for i, e, t in items)


def build_pdf(body):
    fonts = open(os.path.join(HERE, "fonts", "fonts.css"), encoding="utf-8").read()
    css = f"""{fonts}
:root{{{TOKENS}}}
@page{{size:A4;margin:21mm 21mm 22mm 23mm;
  @bottom-center{{content:counter(page);font:8.5pt 'Golos Text',sans-serif;color:#5e6b67}}
  @top-left{{content:"{TITLE}";font:8pt 'Golos Text',sans-serif;color:#97a39f}}}}
@page:first{{margin:0;@bottom-center{{content:none}}@top-left{{content:none}}}}
html{{font-size:10.4pt}}
body{{margin:0;background:#fff;color:var(--ink);font-family:var(--f-text);line-height:1.58;hyphens:auto;-webkit-hyphens:auto}}
{SHARED_CSS}
p{{margin:0 0 .7em;orphans:3;widows:3}} ul,ol{{margin:0 0 .9em;padding-left:1.3em}} li{{margin-bottom:.3em}}
h2{{font-size:2em;margin:0 0 .5em}} h3{{font-size:1.15em;margin:1.4em 0 .45em;page-break-after:avoid}}
section.part,section.appx,section.front{{page-break-before:always}}
section.part>h2{{font-size:2.3em}}
.lede{{margin-bottom:1.2em}}
figure,table,.note,.kpi,.take{{page-break-inside:avoid}}
.cover{{height:296mm;overflow:hidden;box-sizing:border-box;page-break-after:always;background:#183f47;color:#eef3f1;padding:34mm 26mm 26mm;display:flex;flex-direction:column}}
.cover .k{{font-family:var(--f-ui);font-size:9pt;letter-spacing:.14em;text-transform:uppercase;color:#a8c9cf}}
.cover h1{{font-family:var(--f-text);font-size:42pt;font-weight:600;line-height:1.04;margin:16mm 0 9mm;letter-spacing:-.015em}}
.cover p{{font-size:13pt;line-height:1.5;max-width:140mm;color:#d8e6e3}}
.cover .foot{{margin-top:auto;font-family:var(--f-ui);font-size:9pt;color:#a8c9cf;max-width:150mm;line-height:1.5}}
.toc{{list-style:none;padding:0;font-size:1em}} .toc li{{margin:.45em 0}} .toc a{{color:var(--ink);text-decoration:none}}
.toc span{{font-family:var(--f-ui);font-size:.72em;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);display:inline-block;width:42mm}}
a{{color:var(--accent)}}
"""
    html = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{TITLE}</title><style>{css}</style></head><body>
<div class="cover"><div class="k">Семинар «Пространство Новых Идей 2.0» · Минтруд России · Санкт-Петербург, 25–27 августа 2026</div>
<h1>{TITLE}</h1><p>{SUBTITLE}.</p><p>Доклад для руководителей организаций социального обслуживания и региональных министров.</p>
<div class="foot">{COVER_NOTE}</div></div>
<h2 style="margin-top:0">Содержание</h2><ul class="toc">{toc(body)}</ul>
{body}</body></html>"""
    path = os.path.join(HERE, "report_print.html")
    open(path, "w", encoding="utf-8").write(html)
    chrome = os.environ.get("CHROME") or (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome") or ["chromium"])[0]
    out = os.path.join(HERE, "..", "Сколько_стоит_достойная_жизнь_доклад_2026.pdf")
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", "file://" + path], check=True, stderr=subprocess.DEVNULL)


def build_web(body):
    css = f"""
:root{{{TOKENS}}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{DARK}}}}}
:root[data-theme="dark"]{{{DARK}}}
body{{background:var(--paper);color:var(--ink);font-family:var(--f-text);font-size:18px;line-height:1.65;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
{SHARED_CSS}
a{{color:var(--accent)}} a:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.wrap{{max-width:44rem;margin:0 auto;padding-block:3rem 5rem}}
p{{margin:0 0 1em}} ul,ol{{padding-left:1.3em;margin:0 0 1.2em}} li{{margin-bottom:.35em}}
h2{{font-size:clamp(1.7rem,4.5vw,2.4rem);margin:0 0 .6em}} h3{{font-size:1.2rem;margin:2em 0 .5em}}
section{{padding-top:3.5rem;margin-top:3.5rem;border-top:1px solid var(--rule)}}
figure,.tbl{{margin-left:auto;margin-right:auto}}
@media (min-width:62rem){{figure,.tbl{{width:min(58rem,calc(100vw - 4rem));margin-left:50%;transform:translateX(-50%)}}}}
header.hero{{padding-block:2rem 1rem}}
header.hero .k{{font-family:var(--f-ui);font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:600}}
header.hero h1{{font-family:var(--f-text);font-weight:600;font-size:clamp(2.3rem,7vw,3.6rem);line-height:1.04;letter-spacing:-.02em;margin:.5em 0 .4em;text-wrap:balance}}
header.hero p{{font-size:1.15rem;color:var(--mute);margin:0 0 1em}}
header.hero .meta{{font-family:var(--f-ui);font-size:.8rem;color:var(--mute)}}
nav.toc{{font-family:var(--f-ui);font-size:.9rem;margin-top:2rem;border-top:1px solid var(--rule);padding-top:1rem}}
nav.toc ol{{list-style:none;padding:0;margin:0;display:grid;gap:.15rem}}
nav.toc a{{display:flex;gap:.8em;padding:.35em 0;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--grid)}}
nav.toc a:hover{{color:var(--accent)}}
nav.toc span{{flex:0 0 9.5em;color:var(--mute);font-size:.78em;letter-spacing:.08em;text-transform:uppercase;padding-top:.15em}}
@media (max-width:40rem){{body{{font-size:17px}} .kpi{{grid-template-columns:repeat(2,minmax(0,1fr))}} nav.toc span{{flex-basis:7.5em}}}}
@media (prefers-reduced-motion:no-preference){{html{{scroll-behavior:smooth}}}}
"""
    page = f"""<title>{TITLE}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;600&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap">
<style>{css}</style>
<div class="wrap">
<header class="hero">
<div class="k">Семинар «Пространство Новых Идей 2.0» · Минтруд России</div>
<h1>{TITLE}</h1>
<p>{SUBTITLE}.</p>
<div class="meta">{WEB_META} · <a href="https://github.com/qlolp/seminar-mental-health-cost-2026">исходники и PDF</a></div>
<nav class="toc" aria-label="Содержание"><ol>{toc(body)}</ol></nav>
</header>
{body}
</div>
"""
    os.makedirs(os.path.join(HERE, "web"), exist_ok=True)
    open(os.path.join(HERE, "web", "index.html"), "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    body = load_content()
    build_web(body)
    build_pdf(body)
    print("ok")
