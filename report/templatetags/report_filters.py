from django import template

register = template.Library()


@register.filter
def compact_currency(value):
    if value is None:
        return "0"

    value = float(value)

    if value >= 1_000_000_000:
        result = value / 1_000_000_000
        suffix = "B"

    elif value >= 1_000_000:
        result = value / 1_000_000
        suffix = "M"

    elif value >= 1_000:
        result = value / 1_000
        suffix = "K"

    else:
        return f"{value:,.0f}"

    if result.is_integer():
        return f"{int(result)}{suffix}"

    return f"{result:.2f}".rstrip("0").rstrip(".") + suffix