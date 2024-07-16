from __future__ import annotations

import logging
from itertools import cycle

from reactivex.scheduler import ThreadPoolScheduler
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ErrorScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        with Grid(id='dialog'):
            yield Label(
                "Could not connect to server or connection lost.", id="question"
            )
            yield Button("Quit", id="quit")
            yield Button("Reconnect", id="reconnect")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(False)
        else:
            self.dismiss(True)
