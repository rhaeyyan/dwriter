import re

text = """
# Prioritize Urgent Tasks First

From your pending tasks:

1. **Finish Report**
- Open relevant files for #Client:Acme report.
- Review notes from &design-project.

**Test** ``` code block ```
"""

def format_ai_response(text: str) -> str:
    text = text.replace("[", "\\[")
    text = re.sub(r'\*\*(.*?)\*\*', r'[bold #cba6f7]\1[/bold #cba6f7]', text)
    text = re.sub(r'^#+\s+(.*?)$', r'[bold #cba6f7]\1[/bold #cba6f7]', text, flags=re.MULTILINE)
    text = re.sub(r'(?<!\w)#([\w:-]+)', r'[bold #66D0BC]#\1[/bold #66D0BC]', text)
    text = re.sub(r'(?<!\w)&([\w:-]+)', r'[bold #F77F00]&\1[/bold #F77F00]', text)
    text = re.sub(r'`(.*?)`', r'[reverse]\1[/reverse]', text)
    return text

print(format_ai_response(text))
