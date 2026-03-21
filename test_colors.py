import sys
try:
    from textual.css.parse import parse
    rules = parse("", "Button { color: #000000 !important; }")
    print(list(rules))
except Exception as e:
    print(e)
