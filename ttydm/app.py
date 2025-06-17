#!/usr/bin/env python3
import os
import sys
import simplepam

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Button, Select, Static


class TtyDM(App):
    CSS = """
    #container {
      border: double white;
      padding: 1 2;
      width: 33%;         /* one third width */
      height: 33%;        /* one third height */
      background: blue;
      color: #c0c0c0;
      align: center middle; /* horizontal centering */
      layout: vertical;
    }

    #title {
      color: cyan;
      text-style: bold;
      padding-bottom: 1;
      content-align: center middle;
    }

    Input, Select {
      background: black;
      color: white;
      border: ascii gray;
      padding: 0 1;
    }

    Input:focus, Select:focus {
      border: double yellow;
      color: ansi_bright_yellow;
    }
    
    Button {
      background: green;
      color: black;
      padding: 1 3;
      border: ascii green;
    }

    Button:hover {
      background: ansi_bright_green;
      border: double ansi_bright_green;
      color: black;
    }

    #msg {
      color: red;
      padding-top: 1;
      content-align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Welcome to TTYDM", id="title"),
            Input(placeholder="Username", id="user"),
            Input(placeholder="Password", password=True, id="pw"),
            Select(
                options=[
                    ("raw bash", "bash"),
                    ("zellij", "zellij"),
                    ("tmux", "tmux"),
                    ("neovim", "nvim"),
                ],
                id="mux",
            ),
            Input(placeholder="Start Path", id="path"),
            Button("Login", id="btn"),
            Static("", id="msg"),
            id="container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn":
            self.attempt_login()

    def attempt_login(self) -> None:
        user = self.query_one("#user", Input).value.strip()
        pwd = self.query_one("#pw", Input).value
        msgw = self.query_one("#msg", Static)

        # Clear previous message
        msgw.update("")

        if not user or not pwd:
            msgw.update("Username and password required.")
            return

        if not simplepam.authenticate(user, pwd, service="login"):
            msgw.update("ACCESS DENIED")
            # scrub the pw field
            self.query_one("#pw", Input).value = ""
            return

        # Build minimal env
        env = {
            "TERM": os.environ.get("TERM", "linux"),
            "LANG": os.environ.get("LANG", "C.UTF-8"),
            "MUX_CMD": self.query_one("#mux", Select).value,
            "START_PATH": self.query_one("#path", Input).value
            or os.path.expanduser(f"~{user}"),
            "HOME": os.path.expanduser(f"~{user}"),
            "USER": user,
        }

        # preserve PATH or set a safe one
        env["PATH"] = os.environ.get("PATH", "/usr/bin:/bin")
        os.execvpe("login", ["login", "-p", "-f", user], env)


def main():
    if os.geteuid() != 0:
        print("Must be run as root", file=sys.stderr)
        sys.exit(1)
    TtyDM().run()


if __name__ == "__main__":
    main()
