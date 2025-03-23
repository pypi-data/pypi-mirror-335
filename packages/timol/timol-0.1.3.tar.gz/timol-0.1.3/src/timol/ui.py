from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Markdown, Static


class Spacer(Static):
    DEFAULT_CSS = """
    Spacer {
        width: 1fr;
        height: 1fr;
    }    
    """


class SimpleMarkdown(Markdown):
    DEFAULT_CSS = """
    SimpleMarkdown {
        height: auto;
        padding: 0 0 0 0;
        layout: vertical;
        color: $foreground;
        background: transparent;
        overflow-y: auto;
        content-align: left top;
    }
    .em {
        text-style: italic;
    }
    .strong {
        text-style: bold;
    }
    .s {
        text-style: strike;
    }
    .code_inline {
        text-style: bold dim;
    }
    """

    def __init__(self, *args):
        super().__init__(*args)


class InfoLabel(Widget):
    value = reactive("N/A")

    def __init__(self, label: str):
        super().__init__()
        self.label = label

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.label, id="infolabel")
            yield Label(self.value, id="info")

    def watch_value(self, value) -> None:
        query = self.query("#info")
        if len(query) == 0:
            # not yet loaded
            return
        info_label = query.first(Label)
        info_label.update(f"{value}")
        self.tooltip = f"{self.label}: {self.value}"
