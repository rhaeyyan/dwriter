from rich.console import Console
from rich.markdown import Markdown

c = Console()
m = Markdown("# Hello World\n**Bold Text**")
for element in m.elements:
    print(element)
