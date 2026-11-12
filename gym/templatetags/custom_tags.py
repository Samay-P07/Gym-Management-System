from django import template

register = template.Library()

@register.filter(name='currency')
def currency(value):
    try:
        val = float(str(value).replace('$', '').replace('₹', '').replace(',', '').strip())
        return f"₹{int(val):,}" if val.is_integer() else f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return value

@register.filter(name='status_badge')
def status_badge(status):
    if status == 3:
        return "badge-success"
    elif status == 2:
        return "badge-warning"
    return "badge-danger"
