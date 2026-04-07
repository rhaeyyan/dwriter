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

Also check out #my-tag and &my-project.
"""

def format_ai_response(text: str) -> str:
    # Escape brackets manually to avoid rich markup conflicts
    # But wait, AI might return [link](http://...), if we escape [, links break
    # However we are not rendering Markdown links anyway.
    text = text.replace("[", "\\[")
    
    # Bold text: **text** -> [bold #cba6f7]text[/bold #cba6f7]
    text = re.sub(r'\*\*(.*?)\*\*', r'[bold #cba6f7]\1[/bold #cba6f7]', text)
    
    # Headings: # Header -> [bold #cba6f7]Header[/bold #cba6f7]
    # We must ensure it's at start of line
    text = re.sub(r'^#+\s+(.*?)$', r'[bold #cba6f7]\1[/bold #cba6f7]', text, flags=re.MULTILINE)
    
    # Tags: #tag -> [bold #66D0BC]#tag[/bold #66D0BC]
    text = re.sub(r'(?<![\w\[\\]])(#[\w:-]+)', r'[bold #66D0BC]\1[/bold #66D0BC]', text)
    
    # Projects: &project -> [bold #F77F00]&project[/bold #F77F00]
    text = re.sub(r'(?<![\w\[\\]])(&[\w:-]+)', r'[bold #F77F00]\1[/bold #F77F00]', text)
    
    # Inline code: `code` -> [black on white]code[/black on white]
    text = re.sub(r'`(.*?)`', r'[reverse]\1[/reverse]', text)
    
    return text

import sys
sys.stdout.write(format_ai_response(text))
