from textual.app import App, ComposeResult
from textual.widgets import Button, TabbedContent, TabPane

class TestApp(App):
    CSS = """
    Tab {
        background: transparent;
        color: cyan;
        margin: 0 1 0 0;
        padding: 0 4;
        min-width: 15;
    }
    Tabs {
        height: 1;
    }
    Button { height: 1; min-width: 10; padding: 0 1; }
    Button.-success { background: green; color: black; }
    """
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("[ DASH ]"):
                yield Button("[ YES ]", variant="success")
                yield Button("[ NO ]")

if __name__ == "__main__":
    import os
    os.environ["TEXTUAL_DRIVER"] = "textual.drivers.headless_driver:HeadlessDriver"
    app = TestApp()
    app.run(headless=True, size=(80, 24))
