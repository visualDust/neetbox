from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Label, ListItem, ListView, LoadingIndicator

import neetbox.config._cliapp as config
from neetbox.cli._client_web_apis import get_list


def fetch_servers(server_list):
    result = []
    for server in server_list:
        address, port = server["address"], server["port"]
        try:
            running_things = get_list(root=f"http://{address}:{port}")
        except Exception as e:
            running_things = e
        result.append((address, port, running_things))
    return result


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
        server_list = config._get("servers")
        servers = fetch_servers(server_list)
        print(servers)
        yield ListView(*[ListItem(Label(f"{server}")) for server in servers])
        yield Footer()


# class ManageServerPage()
