from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Label, ListItem, ListView, LoadingIndicator


class SeverList(Screen):
    DEFAULT_CSS = """
    Screen {
        align: center middle;
    }

    SeverList {
        width: 30;
        height: auto;
        margin: 2 2;
    }

    Label {
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("Server 1: 127.0.0.1:5000 | 3 running projects")),
            ListItem(Label("Server 2: 192.168.3.111:22222 | 1 running projects")),
            ListItem(Label("Server 3: 10.0.0.3:12121 | 2 running projects")),
        )
        yield Footer()


# class ManageServerPage()
