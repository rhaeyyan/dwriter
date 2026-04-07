import re

text = """
# Prioritize Urgent Tasks First

From your pending tasks, focus on completing the urgent ones first:
1. Finish Report
- Open relevant files and folders for #Client:Acme report.
- Break down the task into smaller, manageable chunks if needed.
2. Test
- Identify which test you need to complete (#test or &test)
- Schedule a dedicated time block.

Also check out #cba6f7 tag if we want to break it.
"""

def format_ai_response(text: str) -> str:
    text = text.replace("[", "\\[")
    
    # Do tags and projects first!
    # A tag is # followed by word chars. BUT wait, `# Header` starts with `# `.
    # So a tag should NOT be followed by a space. [\w:-] enforces it's word characters.
    # To prevent matching Markdown headings which are `# ` or `## `, ensure there's no space immediately following `#`.
    # AND to prevent replacing things we just replaced, let's use a unique placeholder, or just do tags -> projects -> headings -> bold.
    text = re.sub(r'(?<!\w)#([\w:-]+)', r'[bold #66D0BC]#\1[/bold #66D0BC]', text)
    text = re.sub(r'(?<!\w)&([\w:-]+)', r'[bold #F77F00]&\1[/bold #F77F00]', text)
    
    # Bold text: **text** -> [bold #cba6f7]text[/bold #cba6f7]
    text = re.sub(r'\*\*(.*?)\*\*', r'[bold #cba6f7]\1[/bold #cba6f7]', text)
    
    # Headings: # Header -> [bold #cba6f7]Header[/bold #cba6f7]
    # Note: earlier we replaced tags, but tags are #tag. Headings are # Header.
    text = re.sub(r'^#+\s+(.*?)$', r'[bold #cba6f7]\1[/bold #cba6f7]', text, flags=re.MULTILINE)
    
    # Inline code: `code` -> [black on white]code[/black on white]
    text = re.sub(r'`(.*?)`', r'[reverse]\1[/reverse]', text)
    
    return text

print(format_ai_response(text))
