from textual.app import App, ComposeResult
from textual.widgets import Tabs, Tab, ContentSwitcher, Label

class TestTabsApp(App):
    def compose(self) -> ComposeResult:
        yield Tabs(
            Tab("[ DASH ]", id="dash"),
            Tab("\\[ DASH \\]", id="dash_escaped")
        )
        with ContentSwitcher(initial="dash"):
            yield Label("Dashboard Content", id="dash")
            yield Label("Escaped Content", id="dash_escaped")

if __name__ == "__main__":
    app = TestTabsApp()
    app.run(headless=True)
