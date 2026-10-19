"""Графики доклада в виде встраиваемого SVG.

Цвета задаются классами (k-ink, k-mute, k-grid, s1…s5), а сами цвета — в CSS страницы,
поэтому один и тот же график читается и в PDF, и в светлой и тёмной темах веб-версии.
"""
import calc

FONT = "font-family:var(--f-ui, 'Golos Text', sans-serif)"


def svg(w, h, body, label):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" style="{FONT};font-size:12px">'
            f'{body}</svg>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def text(x, y, s, size=12, anchor="start", cls="k-ink", weight=400):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" class="{cls}">{esc(s)}</text>')


def hbars(rows, maxv, label, w=640, label_w=270, bar_h=20, gap=12, note=None):
    """rows: (подпись, значение, класс цвета, подпись значения[, конец диапазона]).
    note хранит источник для чтения кода; на рисунке источник даёт подпись figcaption."""
    note = None
    h = len(rows) * (bar_h + gap) + 14 + (24 if note else 0)
    plot_w = w - label_w - 78
    x = lambda v: label_w + v / maxv * plot_w
    b = ""
    for i, r in enumerate(rows):
        lab, v, cls, vl = r[:4]
        y = 8 + i * (bar_h + gap)
        b += text(label_w - 10, y + bar_h * 0.7, lab, anchor="end")
        if len(r) > 4:
            b += f'<rect x="{x(v):.1f}" y="{y}" width="{x(r[4]) - x(v):.1f}" height="{bar_h}" rx="2" class="{cls}"/>'
            b += f'<rect x="{label_w}" y="{y + bar_h / 2 - 0.5}" width="{x(v) - label_w:.1f}" height="1" class="k-gridf"/>'
            end = x(r[4])
        else:
            b += f'<rect x="{label_w}" y="{y}" width="{max(2, x(v) - label_w):.1f}" height="{bar_h}" rx="2" class="{cls}"/>'
            end = x(v)
        b += text(end + 7, y + bar_h * 0.7, vl, weight=600)
    if note:
        b += text(label_w, h - 6, note, 10.5, cls="k-mute")
    return svg(w, h, b, label)


def grouped(cats, series, classes, legend, maxv, label, w=640, h=300, step=20, note=None):
    note = None  # источник даёт подпись figcaption
    left, bottom, top = 40, 52, 34
    ph = h - bottom - top - (16 if note else 0)
    gw = (w - left - 8) / len(cats)
    Y = lambda v: top + ph - v / maxv * ph
    b = ""
    for t in range(0, maxv + 1, step):
        b += f'<line x1="{left}" x2="{w - 8}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" class="k-grid"/>' + text(left - 6, Y(t) + 4, str(t), 10.5, "end", "k-mute")
    n = len(series)
    bw = min(36, (gw - 22) / n)
    for i, c in enumerate(cats):
        cx = left + gw * i + gw / 2
        for j, s in enumerate(series):
            v = s[i]
            xx = cx - n * bw / 2 + j * bw
            b += f'<rect x="{xx:.1f}" y="{Y(v):.1f}" width="{bw - 3:.1f}" height="{top + ph - Y(v):.1f}" rx="2" class="{classes[j]}"/>'
            b += text(xx + (bw - 3) / 2, Y(v) - 5, f"{v:g}".replace(".", ","), 10.5, "middle", weight=600)
        for k, line in enumerate(c.split("\n")):
            b += text(cx, top + ph + 18 + k * 14, line, 11, "middle")
    xl = left
    for j, l in enumerate(legend):
        b += f'<rect x="{xl}" y="6" width="12" height="12" rx="2" class="{classes[j]}"/>' + text(xl + 18, 16, l, 11)
        xl += 34 + len(l) * 6.4
    if note:
        b += text(left, h - 6, note, 10.5, cls="k-mute")
    return svg(w, h, b, label)


def fig_two_costs():
    return hbars([
        ("Текущие: ПНИ", 44.8, "s1", "44,8"),
        ("Текущие: сопровождаемое проживание", 52.9, "s2", "52,9"),
        ("Капитальные: новый ПНИ или реновация", 8, "s3", "8–24", 24),
        ("Капитальные: ПНИ в арендованном здании", 5, "s3", "5–17,5", 17.5),
        ("Капитальные: покупка квартир для СП", 2, "s3", "2–6", 6),
    ], 60, "Текущие и капитальные затраты на человека в месяц", label_w=300,
        note="Тыс. ₽ на человека в месяц. Капитальные — в пересчёте на месяц с учётом амортизации. НИУ ВШЭ, 2022.")


def fig_cost_range():
    return hbars([
        ("ПНИ, среднее (ВШЭ)", 44.8, "s1", "44,8"),
        ("ПНИ, диапазон оценок 2021–2022", 50, "s3", "50–120", 120),
        ("Сопровождаемое проживание, регионы (ВШЭ)", 52.9, "s2", "52,9"),
        ("«Дом как дом», тяжёлые нарушения", 90, "s2", "≈90"),
        ("Сопровождаемое проживание, Москва (ВШЭ)", 111.9, "s4", "111,9"),
    ], 130, "Оценки текущих расходов на человека в месяц", label_w=300,
        note="Тыс. ₽ в месяц. Методики у источников разные; сравнивать бары напрямую нельзя.")


def fig_hours():
    return hbars([
        ("ПНИ: все сотрудники", 3.5, "s1", "3,5 ч"),
        ("ПНИ: основной персонал (уход, сопровождение)", 1.5, "s3", "1,5 ч"),
        ("Проекты сопровождаемого проживания", 8.2, "s2", "8,2 ч"),
    ], 10, "Оплаченные часы персонала на одного человека в сутки", label_w=320,
        note="Оплаченных часов работы персонала на одного получателя в сутки. НИУ ВШЭ, 2022.")


def fig_quality():
    return grouped(["Здоровье", "Социальное\nблагополучие", "Бытовой\nкомфорт", "Безопасность", "Интегральный\nиндекс"],
                   [[69.1, 44.3, 61, 51.6, 56.9], [85.2, 84.7, 79.2, 57.1, 76.9]], ["s1", "s2"],
                   ["ПНИ", "Сопровождаемое проживание"], 100, "Индекс качества жизни",
                   note="Баллы из 100, индекс по критериям ВОЗ. НИУ ВШЭ, 2022.")


def fig_staff():
    return grouped(["Весь персонал", "Медики", "Социальные\nработники", "Педагоги"],
                   [[49, 26, 1.5, 0.8], [60, 28, 8.6, 1.5]], ["s3", "s1"], ["2017", "2024"], 80,
                   "Персонал ПНИ на 100 жителей", h=290,
                   note="Работников на 100 жителей ПНИ; учитываются ставки, а не люди. «Если быть точным».")


def fig_ltc():
    return hbars([
        ("Нидерланды", 4.4, "s1", "4,4"),
        ("Норвегия", 3.5, "s1", "3,5"),
        ("Швеция", 3.4, "s1", "3,4"),
        ("Дания", 3.2, "s1", "3,2"),
        ("Среднее по ОЭСР", 1.8, "s2", "1,8"),
        ("Республика Корея (2019)", 1.0, "s3", "≈1,0"),
        ("Греция, Польша, Латвия", 0.5, "s3", "≤0,5"),
        ("Россия, только ПНИ (оценка)", 0.04, "s4", "≈0,04"),
    ], 5.2, "Расходы на долговременный уход, процент ВВП", label_w=250,
        note="% ВВП, 2021, если не указано иное. ОЭСР; Корея — KEIA/LTCcovid; Россия — расчёт автора, только ПНИ.")


def fig_gap():
    return hbars([
        ("Жители ПНИ, 2024", 139.5, "s1", "139,5"),
        ("Потенциал перехода, до 45 %", 62.8, "s3", "≈63"),
        ("Сопровождаемое проживание по Минтруду, 2025", 8.0, "s2", "8,0"),
        ("Постоянное проживание, оценка", 1.8, "s4", "1,8"),
    ], 160, "Жители ПНИ, потенциал и охват", label_w=310,
        note="Тысяч человек. «Если быть точным», «Ведомости», Минтруд; 63 = 45 % × 139,5.")


def fig_sens():
    w, h, l, b, t = 640, 330, 50, 46, 22
    xmax, ymax = 40, 150
    pw, ph = w - l - 14, h - b - t
    X = lambda x: l + x / xmax * pw
    Y = lambda y: t + ph - y / ymax * ph
    s = ""
    for y in range(0, 151, 30):
        s += f'<line x1="{l}" x2="{w - 14}" y1="{Y(y):.1f}" y2="{Y(y):.1f}" class="k-grid"/>' + text(l - 6, Y(y) + 4, str(y), 10.5, "end", "k-mute")
    for x in range(0, 41, 8):
        s += text(X(x), h - b + 18, str(x), 10.5, "middle", "k-mute")
    s += text((l + w) / 2, h - 10, "часов сопровождения в неделю на человека", 11, "middle", "k-mute")
    s += text(l, 12, "тыс. ₽ в месяц", 10.5, "start", "k-mute")
    for name, p, f, cls in (("оптимистично", 350, 22, "s2"), ("база", 475, 30, "s1"), ("пессимистично", 600, 38, "s5")):
        s += (f'<line x1="{X(0):.1f}" y1="{Y(calc.flat_cost(0, p, f)):.1f}" x2="{X(40):.1f}" '
              f'y2="{Y(calc.flat_cost(40, p, f)):.1f}" class="{cls}-line" stroke-width="2.4"/>')
        s += text(X(40) - 4, Y(calc.flat_cost(40, p, f)) - 7, name, 11, "end", f"{cls}-text", 600)
    s += f'<line x1="{l}" x2="{w - 14}" y1="{Y(calc.C_PNI):.1f}" y2="{Y(calc.C_PNI):.1f}" class="k-inkline" stroke-dasharray="5 4" stroke-width="1.6"/>'
    s += text(l + 6, Y(calc.C_PNI) - 6, "место в ПНИ, 44,8", 11, "start", weight=600)
    s += f'<line x1="{l}" x2="{w - 14}" y1="{Y(calc.C_SP):.1f}" y2="{Y(calc.C_SP):.1f}" class="s4-line" stroke-dasharray="2 4" stroke-width="1.6"/>'
    s += text(w - 20, Y(calc.C_SP) + 16, "сопровождаемое проживание, 52,9", 11, "end", "s4-text", 600)
    return svg(w, h, s, "Стоимость жизни в квартире в зависимости от часов сопровождения")


FIGURES = {
    "two_costs": fig_two_costs, "cost_range": fig_cost_range, "hours": fig_hours,
    "quality": fig_quality, "staff": fig_staff, "ltc": fig_ltc, "gap": fig_gap, "sens": fig_sens,
}

if __name__ == "__main__":
    for k, f in FIGURES.items():
        print(k, len(f()))
