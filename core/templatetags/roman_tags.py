from django import template

register = template.Library()

@register.filter
def to_roman(value):
    """
    Converts an integer to a Roman numeral.
    """
    try:
        n = int(value)
    except (ValueError, TypeError):
        return value

    if not 0 < n < 4000:
        return n

    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num
