"""Генерирует SVG-графики доклада. Запуск: python3 figures.py"""
import calc

INK, MUTE, GRID = "#1d2733", "#6b7785", "#e3e7ec"
BLUE, TEAL, AMBER, RED, LIGHT = "#2f5d8a", "#2a8c82", "#d08a1f", "#b5443a", "#9db4cc"
FONT = "Inter, 'DejaVu Sans', sans-serif"


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}" font-size="12" fill="{INK}">{body}</svg>')


def text(x, y, s, size=12, anchor="start", color=INK, weight="400"):
    s = s.replace("&", "&amp;")
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{s}</text>'


def hbars(path, rows, unit, maxv, w=620, label_w=250, bar_h=22, gap=12, note=None):
    """rows: (label, value, color, value_label[, range_to])"""
    h = len(rows) * (bar_h + gap) + 28 + (22 if note else 0)
    plot_w = w - label_w - 70
    b = ""
    for i, r in enumerate(rows):
        label, v, col, vl = r[:4]
        y = 12 + i * (bar_h + gap)
        b += text(label_w - 10, y + bar_h * 0.7, label, anchor="end")
        b += f'<rect x="{label_w}" y="{y}" width="{max(2, v / maxv * plot_w):.1f}" height="{bar_h}" rx="3" fill="{col}"/>'
        if len(r) > 4:  # диапазон
            b += (f'<line x1="{label_w + v / maxv * plot_w:.1f}" x2="{label_w + r[4] / maxv * plot_w:.1f}" '
                  f'y1="{y + bar_h / 2}" y2="{y + bar_h / 2}" stroke="{INK}" stroke-width="2"/>'
                  f'<line x1="{label_w + r[4] / maxv * plot_w:.1f}" x2="{label_w + r[4] / maxv * plot_w:.1f}" '
                  f'y1="{y + 4}" y2="{y + bar_h - 4}" stroke="{INK}" stroke-width="2"/>')
            end = label_w + r[4] / maxv * plot_w
        else:
            end = label_w + v / maxv * plot_w
        b += text(end + 8, y + bar_h * 0.7, vl, weight="600")
    if note:
        b += text(label_w, h - 6, note, size=10.5, color=MUTE)
    open(path, "w", encoding="utf-8").write(svg(w, h, b))


def grouped(path, cats, series, colors, w=620, h=300, maxv=100, note=None, legend=None):
    left, bottom, top = 40, 56, 30
    ph = h - bottom - top
    gw = (w - left - 10) / len(cats)
    b = ""
    for t in range(0, maxv + 1, 20):
        y = top + ph - t / maxv * ph
        b += f'<line x1="{left}" x2="{w-10}" y1="{y}" y2="{y}" stroke="{GRID}"/>' + text(left - 6, y + 4, str(t), 10.5, "end", MUTE)
    n = len(series)
    bw = min(34, (gw - 24) / n)
    for i, c in enumerate(cats):
        cx = left + gw * i + gw / 2
        for j, s in enumerate(series):
            v = s[i]
            x = cx - n * bw / 2 + j * bw
            hh = v / maxv * ph
            b += f'<rect x="{x:.1f}" y="{top + ph - hh:.1f}" width="{bw - 3}" height="{hh:.1f}" rx="2" fill="{colors[j]}"/>'
            b += text(x + (bw - 3) / 2, top + ph - hh - 5, f"{v:g}".replace(".", ","), 10.5, "middle", INK, "600")
        for k, line in enumerate(c.split("\n")):
            b += text(cx, h - bottom + 18 + k * 14, line, 11, "middle")
    if legend:
        x = left
        for j, l in enumerate(legend):
            b += f'<rect x="{x}" y="6" width="12" height="12" rx="2" fill="{colors[j]}"/>' + text(x + 18, 16, l, 11)
            x += 28 + len(l) * 6.6
    if note:
        b += text(left, h - 6, note, 10.5, color=MUTE)
    open(path, "w", encoding="utf-8").write(svg(w, h, b))


def fig_cost():
    hbars("fig_cost.svg", [
        ("ПНИ, в среднем (ВШЭ, 2022)", 44.8, BLUE, "44,8"),
        ("ПНИ, диапазон (Известия, 2026)", 50, LIGHT, "50–120", 120),
        ("Сопровождаемое проживание, проекты (ВШЭ)", 52.9, TEAL, "52,9"),
        ("«Дом как дом», тяжёлые нарушения (2026)", 90, TEAL, "≈90"),
        ("Сопровождаемое проживание, Москва (ВШЭ)", 111.9, AMBER, "111,9"),
    ], "тыс. ₽/мес", 130, label_w=285, note="Текущие расходы на одного человека в месяц, тыс. ₽. Методики расчёта у источников разные: сравнивать бары между собой нужно осторожно.")


def fig_quality():
    grouped("fig_quality.svg",
            ["Здоровье", "Социальное\nблагополучие", "Бытовой\nкомфорт", "Безопасность", "Интегральный\nиндекс"],
            [[69.1, 44.3, 61, 51.6, 56.9], [85.2, 84.7, 79.2, 57.1, 76.9]], [BLUE, TEAL],
            legend=["ПНИ", "Сопровождаемое проживание"], note="Индекс качества жизни по критериям ВОЗ, баллы из 100. НИУ ВШЭ, 2022.")


def fig_staff():
    grouped("fig_staff.svg", ["Весь персонал", "Медики", "Социальные\nработники", "Педагоги"],
            [[49, 26, 1.5, 0.8], [60, 28, 8.6, 1.5]], [LIGHT, BLUE], maxv=80, h=290,
            legend=["2017", "2024"], note="Работников на 100 жителей ПНИ. «Если быть точным» по данным Минтруда; считаются ставки, а не люди.")


def fig_ltc():
    hbars("fig_ltc.svg", [
        ("Нидерланды (2021)", 4.4, BLUE, "4,4"),
        ("Норвегия (2021)", 3.5, BLUE, "3,5"),
        ("Швеция (2021)", 3.4, BLUE, "3,4"),
        ("Дания (2021)", 3.2, BLUE, "3,2"),
        ("Среднее по ОЭСР (2021)", 1.8, TEAL, "1,8"),
        ("Республика Корея (2019, оценка)", 1.0, LIGHT, "≈1,0"),
        ("Греция, Польша, Латвия (2021)", 0.5, LIGHT, "≤0,5"),
        ("Россия (оценка версии 2, †)", 0.1, AMBER, "0,1–0,2", 0.2),
    ], "% ВВП", 5.2, label_w=270, note="Расходы на долговременный уход, % ВВП. ОЭСР, Health at a Glance 2023; Корея — LTCcovid/KEIA; Россия — оценка версии 2 (†).")


def fig_gap():
    hbars("fig_gap.svg", [
        ("Жители ПНИ (2024)", 139.5, BLUE, "139,5"),
        ("Потенциал перехода по Минтруду, до 45 %", 62.8, LIGHT, "≈63"),
        ("«Сопровождаемое проживание» по Минтруду (2024)", 7.0, TEAL, "7,0"),
        ("Постоянное проживание в квартирах (оценка)", 1.8, AMBER, "1,8"),
    ], "тыс. чел.", 160, label_w=310, note="Тысяч человек. «Если быть точным», Минтруд. 62,8 — расчёт: 45 % × 139,5 тыс.")


def fig_sens():
    w, h, l, b, t = 620, 330, 52, 46, 20
    xmax, ymax = 40, 150
    pw, ph = w - l - 14, h - b - t
    X = lambda x: l + x / xmax * pw
    Y = lambda y: t + ph - y / ymax * ph
    s = ""
    for y in range(0, 151, 30):
        s += f'<line x1="{l}" x2="{w-14}" y1="{Y(y)}" y2="{Y(y)}" stroke="{GRID}"/>' + text(l - 6, Y(y) + 4, str(y), 10.5, "end", MUTE)
    for x in range(0, 41, 8):
        s += text(X(x), h - b + 18, str(x), 10.5, "middle", MUTE)
    s += text((l + w) / 2, h - 12, "часов сопровождения в неделю на человека", 11, "middle", MUTE)
    s += text(14, t + 4, "тыс. ₽/мес", 10.5, "start", MUTE)
    for name, p, f, col in (("оптимистично", 350, 22, TEAL), ("база", 475, 30, BLUE), ("пессимистично", 600, 38, RED)):
        pts = " ".join(f"{X(x):.1f},{Y(calc.flat_cost(x, p, f)):.1f}" for x in (0, 40))
        s += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.4"/>'
        yy = calc.flat_cost(40, p, f)
        s += text(X(40) - 4, Y(yy) - 6, name, 11, "end", col, "600")
    s += f'<line x1="{l}" x2="{w-14}" y1="{Y(calc.C_PNI)}" y2="{Y(calc.C_PNI)}" stroke="{INK}" stroke-dasharray="5 4" stroke-width="1.6"/>'
    s += text(l + 6, Y(calc.C_PNI) - 6, "место в ПНИ, 44,8 (ВШЭ)", 11, "start", INK, "600")
    s += f'<line x1="{l}" x2="{w-14}" y1="{Y(calc.C_SP)}" y2="{Y(calc.C_SP)}" stroke="{AMBER}" stroke-dasharray="2 4" stroke-width="1.6"/>'
    s += text(w - 20, Y(calc.C_SP) + 15, "сопровождаемое проживание, 52,9 (ВШЭ)", 11, "end", AMBER, "600")
    open("fig_sens.svg", "w", encoding="utf-8").write(svg(w, h, s))


if __name__ == "__main__":
    for f in (fig_cost, fig_quality, fig_staff, fig_ltc, fig_gap, fig_sens):
        f()
    print("ok")
