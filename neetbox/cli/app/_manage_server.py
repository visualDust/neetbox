from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Label, ListItem, ListView, LoadingIndicator

import neetbox.config._cli_user_config as cliconfig
from neetbox.cli._client_web_apis import get_list


def fetch_servers(server_list):
    result = []
    for server in server_list:
        address, port = server["address"], server["port"]
        try:
            running_things = get_list(root=f"http://{address}:{port}/")
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
        server_list = cliconfig._get("servers")
        servers = fetch_servers(server_list)
        list_items = []
        for server in servers:
            address = server[0]
            port = server[1]
            if isinstance(server[2], Exception):
                stat = "OFFLINE"
            else:
                num_projects = len(server[2])
                stat = f"({num_projects} projects)"
            list_items.append(ListItem(Label(f"{address}:{port} {stat}")))
        yield ListView(*list_items)
        yield Footer()


# class ManageServerPage()
