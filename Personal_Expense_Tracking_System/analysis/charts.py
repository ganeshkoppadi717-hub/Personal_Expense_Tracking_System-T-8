"""Lightweight SVG charts for category and monthly expense totals."""
from html import escape
from math import cos, pi, sin

PALETTE = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444",
           "#8b5cf6", "#ec4899", "#14b8a6", "#64748b", "#84cc16"]


def _text(x, y, value, *, size=13, color="#475569", anchor="middle", weight="400"):
    return ('<text x="%s" y="%s" text-anchor="%s" fill="%s" '
            'font-family="Arial, sans-serif" font-size="%s" font-weight="%s">%s</text>'
            % (x, y, anchor, color, size, weight, escape(str(value))))


def _svg(content, width=760, height=460):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" '
            'viewBox="0 0 %s %s"><rect width="100%%" height="100%%" fill="#ffffff"/>%s</svg>'
            % (width, height, width, height, content)).encode("utf-8")


def _empty_chart(message="No data to display"):
    return _svg(_text(380, 235, message, size=16, color="#64748b"))


def category_pie_svg(breakdown):
    """Render category totals and percentages as an accessible SVG pie chart."""
    positive = [item for item in breakdown if float(item["total"]) > 0]
    total = sum(float(item["total"]) for item in positive)
    if total <= 0:
        return _empty_chart()

    content = [_text(380, 34, "Spending by category", size=20, color="#0f172a", weight="600")]
    center_x, center_y, radius = 240, 240, 155
    angle = -pi / 2
    for index, item in enumerate(positive):
        fraction = float(item["total"]) / total
        if fraction >= 1:
            content.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>'
                           % (center_x, center_y, radius, PALETTE[index % len(PALETTE)]))
            continue
        end_angle = angle + fraction * 2 * pi
        start_x = center_x + radius * cos(angle)
        start_y = center_y + radius * sin(angle)
        end_x = center_x + radius * cos(end_angle)
        end_y = center_y + radius * sin(end_angle)
        large_arc = 1 if fraction > 0.5 else 0
        content.append(
            '<path d="M %s %s L %s %s A %s %s 0 %s 1 %s %s Z" fill="%s" '
            'stroke="#ffffff" stroke-width="2"/>'
            % (center_x, center_y, start_x, start_y, radius, radius, large_arc,
               end_x, end_y, PALETTE[index % len(PALETTE)]))
        angle = end_angle

    for index, item in enumerate(positive):
        y = 130 + index * 36
        color = PALETTE[index % len(PALETTE)]
        label = "%s (%.1f%%)" % (item["category"], float(item["percent"]))
        content.append('<rect x="455" y="%s" width="13" height="13" rx="3" fill="%s"/>'
                       % (y - 11, color))
        content.append(_text(478, y, label, anchor="start"))
    return _svg("".join(content))


def monthly_bar_svg(monthly, currency="Rs."):
    """Render monthly expense totals as an SVG bar chart."""
    if not monthly:
        return _empty_chart()

    width, height = 760, 460
    left, top, right, bottom = 90, 72, 30, 95
    chart_width = width - left - right
    chart_height = height - top - bottom
    max_total = max(float(item["total"]) for item in monthly)
    if max_total <= 0:
        return _empty_chart()

    content = [_text(width / 2, 32, "Monthly spending", size=20,
                     color="#0f172a", weight="600"),
               _text(left, 52, "Total (%s)" % currency, anchor="start", size=12),
               '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="#cbd5e1"/>'
               % (left, top + chart_height, width - right, top + chart_height)]
    slot = chart_width / len(monthly)
    bar_width = min(54, slot * 0.62)
    for index, item in enumerate(monthly):
        amount = float(item["total"])
        bar_height = chart_height * amount / max_total
        x = left + slot * index + (slot - bar_width) / 2
        y = top + chart_height - bar_height
        content.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="5" fill="%s"/>'
                       % (x, y, bar_width, bar_height, PALETTE[0]))
        content.append(_text(x + bar_width / 2, max(top - 4, y - 8),
                             "{:,.2f}".format(amount), size=11))
        content.append(_text(x + bar_width / 2, top + chart_height + 24,
                             item["month"], size=11))
    return _svg("".join(content))
