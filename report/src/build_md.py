"""Собирает PDF и веб-версию доклада из Markdown (редакция 6 и далее).

  python3 build_md.py
    → ../Сколько_стоит_достойная_жизнь_доклад_2026.pdf и web/index.html

Нужны pandoc и Chromium. Оформление и шрифты берутся из build.py, графики — из figures.py.
Ссылки [n], [n, m] и [n–m] становятся ссылками на пункты списка источников (приложение Г).
"""
import html
import os
import re
import subprocess

import build
import figures

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_MD = os.path.join(HERE, "..", "..", "reports", "Сколько стоит достойная жизнь полная версия.md")

# После какого заголовка (подстрока заголовка h2 или h3) вставить какой график и с какой подписью.
FIGURES_AFTER = [
    ("Часть 2", "two_costs", "Текущие и капитальные затраты на человека в месяц, тыс. ₽, в ценах данных ВШЭ."),
    ("Часть 2", "hours", "Оплаченные часы работы персонала на одного человека в сутки (ВШЭ, 2022)."),
    ("Часть 2", "quality", "Индекс качества жизни, баллы из 100 (ВШЭ, по пересказу АСИ †)."),
    ("Часть 1", "staff", "Персонал ПНИ на 100 жителей, 2017 и 2024 годы («Если быть точным»)."),
    ("Калькулятор", "sens", "Стоимость жизни в квартире в зависимости от часов сопровождения (модель составителя); "
                            "горизонтальные линии — цена места в ПНИ как у ВШЭ и в ценах 2025 года."),
]


def md_to_html(md):
    return subprocess.run(["pandoc", "-f", "gfm", "-t", "html", "--wrap=none"], input=md,
                          capture_output=True, text=True, check=True).stdout


def link_refs(body):
    """[12] → ссылка; [3, 5] и [177–178] → ссылки на каждый номер. Внутри списка источников не трогаем."""
    def one(n):
        return f'<a class="ref" href="#src-{n}">{n}</a>'

    def repl(m):
        parts = re.split(r"(,\s*|\s*[–-]\s*)", m.group(1))
        out = "".join(one(p) if p.strip().isdigit() else p for p in parts)
        return f"<span class=\"refs\">[{out}]</span>"
    pieces = re.split(r"(<pre.*?</pre>)", body, flags=re.S)
    return "".join(p if p.startswith("<pre") else
                   re.sub(r"\[(\d{1,3}(?:(?:,\s*|\s*[–-]\s*)\d{1,3})*)\]", repl, p) for p in pieces)


def sectionize(body):
    """Каждый h2 открывает <section>; номер части или приложения уходит в «надзаголовок»."""
    chunks = re.split(r"(?=<h2[ >])", body)
    out = [chunks[0]] if not chunks[0].lstrip().startswith("<h2") else []
    for i, ch in enumerate(c for c in chunks if c.lstrip().startswith("<h2")):
        m = re.match(r"<h2[^>]*>(.*?)</h2>", ch, re.S)
        title = m.group(1)
        rest = ch[m.end():]
        mm = re.match(r"(Часть \d+|Приложение [А-ЯЁ])\.\s*(.*)", html.unescape(re.sub(r"<[^>]+>", "", title)))
        if mm:
            kind = "appx" if mm.group(1).startswith("Приложение") else "part"
            eyebrow, h = mm.group(1), mm.group(2)
        else:
            kind, eyebrow, h = "front", "Доклад", re.sub(r"<[^>]+>", "", title)
        out.append(f'<section class="{kind}" id="sec-{i}">\n<p class="eyebrow">{eyebrow}</p>\n<h2>{h}</h2>{rest}</section>\n')
    return "".join(out)


def add_source_ids(body):
    """Нумерованный список в приложении Г получает id="src-n" у каждого пункта."""
    m = re.search(r'<p class="eyebrow">Приложение Г</p>', body)
    if not m:
        return body
    start = m.end()
    end = body.find("</section>", start)
    seg = body[start:end]

    def fix_ol(om):
        first = int(re.search(r'start="(\d+)"', om.group(1)).group(1)) if "start=" in om.group(1) else 1
        items = re.split(r"(<li>)", om.group(2))
        n, res = first, []
        for it in items:
            if it == "<li>":
                res.append(f'<li id="src-{n}">')
                n += 1
            else:
                res.append(it)
        return f"<ol{om.group(1)} class=\"src\">{''.join(res)}</ol>"
    seg = re.sub(r"<ol([^>]*)>(.*?)</ol>", fix_ol, seg, flags=re.S)
    return body[:start] + seg + body[end:]


def insert_figures(body):
    for key_heading, fig, caption in reversed(FIGURES_AFTER):
        m = re.search(r"<h2>[^<]*" + re.escape(key_heading) + r"[^<]*</h2>|<p class=\"eyebrow\">"
                      + re.escape(key_heading) + r"</p>\s*<h2>.*?</h2>", body, re.S)
        if not m:
            m = re.search(r"<h[23][^>]*>[^<]*" + re.escape(key_heading) + r"[^<]*</h[23]>", body)
        if not m:
            print("нет места для графика:", fig)
            continue
        # после первого абзаца, идущего за заголовком
        p_end = body.find("</p>", m.end())
        pos = p_end + 4 if p_end != -1 else m.end()
        fig_html = f'<figure>{figures.FIGURES[fig]()}<figcaption>{caption}</figcaption></figure>'
        body = body[:pos] + fig_html + body[pos:]
    return body


def main():
    md = open(SRC_MD, encoding="utf-8").read()
    md = re.sub(r"\A# [^\n]*\n", "", md)  # заголовок доклада рисуется обложкой
    body = md_to_html(md)
    body = sectionize(body)
    body = add_source_ids(body)
    body = link_refs(body)
    body = insert_figures(body)
    body = body.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    build.COVER_NOTE = ("<b>Редакция 6, октябрь 2026.</b> Калькулятор пересчитан в ценах одного года, резюме приведено "
                        "в соответствие с текстом, страновые главы вынесены в приложения. Текст подготовлен ИИ и прочитан "
                        "отдельными ИИ-сессиями; это не рецензия людей. Список изменений — в приложении Б.")
    build.WEB_META = "Редакция 6 · октябрь 2026"
    build.build_web(body)
    build.build_pdf(body)
    print("ok")


if __name__ == "__main__":
    main()
