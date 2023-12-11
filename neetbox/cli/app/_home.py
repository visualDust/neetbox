from pathlib import Path
from typing import Iterable

from textual import events
from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, DirectoryTree, Footer, Header, Placeholder, Static

from ._manage_server import SeverList


class WorkspaceBanner(Widget):
    """Display a greeting."""

    DEFAULT_CSS = """
    WorkspaceBanner{
        background: $primary;
        color: green;
        height: 3;
        padding: 1 1;
        background: $panel;
        border: $secondary tall;
        content-align: center middle;
    }
    """

    def render(self) -> RenderResult:
        return "In workspace : [b]ID[/b]"


class HomePage(Static):
    DEFAULT_CSS = """
        Button {
            width: 20;
            margin: 1;
        }
    """

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""

        yield WorkspaceBanner()
        yield Horizontal(
            VerticalScroll(
                Button("open local...", variant="primary", id="open_local"),
                Button("connect server", variant="success", id="connect_server"),
                Button("settings", variant="default", id="settings"),
            )
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.notify(f"{event.button.id}")
        if event.button.id == "connect_server":
            self.app.push_screen(SeverList())
