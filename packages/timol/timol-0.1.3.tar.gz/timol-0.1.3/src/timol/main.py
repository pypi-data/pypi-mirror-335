from typing import List, Optional, Union

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.events import MouseEvent
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.validation import Number, Validator
from textual.widget import Widget
from textual.widgets import Header, Input

from timol.reader import MoleculesReader
from timol.sidebar import Sidebar
from timol.viewer import MolViewer


class InputScreen(ModalScreen):
    def __init__(
        self,
        placeholder: str = "",
        input_type: str = "text",
        validators: Optional[List[Validator]] = [],
    ):
        super().__init__()
        self.placeholder = placeholder
        self.input_type = input_type
        self.validators = validators

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder=self.placeholder,
            type=self.input_type,  # type: ignore
            validators=self.validators,
        )

    def on_key(self, event):
        if event.key == "escape":
            self.dismiss(None)

    def on_click(self, event: MouseEvent):
        if event.widget is self:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted):
        val = event.validation_result
        if val is not None and len(val.failures) > 0:
            if len(val.failure_descriptions) > 0:
                s = val.failure_descriptions[0]
            else:
                s = "Failed to validate"

            input = self.query_one(Input)
            input.placeholder = s
            input.clear()
            return

        self.dismiss(event.value)


class MoleculesInterface(Widget):
    index: reactive[int] = reactive(-1)
    centering: reactive[bool] = reactive(False)
    radii_scale: reactive[float] = reactive(1)

    BINDINGS = [
        Binding("h", "toggle_hotkey_menu", "Toggle help menu"),
        Binding("a", "rotate_camera(-45,0)", "Rotate left"),
        Binding("d", "rotate_camera(45,0)", "Rotate right"),
        Binding("w", "rotate_camera(0,45)", "Pivot forwards"),
        Binding("s", "rotate_camera(0,-45)", "Pivot backwards"),
        Binding("q,left", "change_index(-1)", "Next frame (index)"),
        Binding("e,right", "change_index(1)", "Previous frame (index)"),
        Binding("Q,up", "set_index(-1)", "Last frame (index = -1)"),
        Binding("E,down", "set_index(0)", "First frame (index = 0)"),
        Binding("W", "zoom(1)", "Zoom inwards"),
        Binding("S", "zoom(-1)", "Zoom outwards"),
        Binding("r", "reset_view()", "Reset camera rotation, zoom and offset"),
        Binding("R", "radiii_scale_prompt", "Change the scale of the atomic radii"),
        Binding("c", "toggle_centering()", "Center camera"),
        Binding("i", "index_prompt", "Go to specific frame (index)"),
        Binding("x", "toggle_sidebar", "Toggle sidebar visibility"),
    ]

    def __init__(self, mols_reader: MoleculesReader, radii_scale: float = 1):
        super().__init__()
        self.mols_reader = mols_reader
        self.radii_scale = radii_scale
        self.load_molecules()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield (
                Sidebar(mols_reader=self.mols_reader)
                .data_bind(index=MoleculesInterface.index)
                .data_bind(centering=MoleculesInterface.centering)
            )
            yield (
                MolViewer(mols_reader=self.mols_reader)
                .data_bind(index=MoleculesInterface.index)
                .data_bind(centering=MoleculesInterface.centering)
                .data_bind(radii_scale=MoleculesInterface.radii_scale)
            )

    def load_molecules(self) -> None:
        self.index = 0

    def set_index(self, index: Union[None, str, int] = None):
        n_mols = self.mols_reader.get_n_molecules()
        if index is None:
            return
        index = int(index)
        if index < 0:
            self.set_index(index % n_mols)
        if index >= n_mols or index == self.index:
            return

        self.index = index

    def set_radii_scale(self, scale: Union[None, str, float] = None):
        if scale is None:
            return
        scale = float(scale)
        if scale <= 0:
            return
        self.radii_scale = scale

    def action_change_index(self, by: int):
        self.set_index(self.index + by)

    def action_set_index(self, index: int):
        self.set_index(index)

    def action_reset_view(self):
        self.query_one(MolViewer).reset_view()

    def action_toggle_centering(self):
        self.centering = not self.centering

    def action_zoom(self, by: int):
        self.query_one(MolViewer).zoom_by(by)

    def action_index_prompt(self):
        self.app.push_screen(
            screen=InputScreen(
                placeholder="Enter the index of the frame to jump to",
                input_type="integer",
                validators=[
                    Number(minimum=0, maximum=self.mols_reader.get_n_molecules() - 1)
                ],
            ),
            callback=self.set_index,  # type: ignore
        )

    def action_radiii_scale_prompt(self):
        self.app.push_screen(
            screen=InputScreen(
                placeholder=f"Enter the scale of the atomic radii (currently {self.radii_scale})",
                input_type="number",
                validators=[Number(minimum=0)],
            ),
            callback=self.set_radii_scale,  # type: ignore
        )

    def action_toggle_hotkey_menu(self):
        if self.screen.query("HelpPanel"):
            self.app.action_hide_help_panel()
        else:
            self.app.action_show_help_panel()

    def action_rotate_camera(self, yaw: float, pitch: float):
        self.query_one(MolViewer).rotate_camera(yaw, pitch)

    def action_toggle_sidebar(self):
        sidebar = self.query_one(Sidebar)
        width = sidebar.styles.width
        if width is None or width.value == 0:
            sidebar.styles.width = 30
        else:
            sidebar.styles.width = 0


class Timol(App[str]):
    CSS_PATH = "timol.tcss"
    TITLE = "TIMOL"
    SUB_TITLE = "Terminal Interface MOLecular viewer"
    BINDINGS = [
        Binding("ctrl+q,ctrl+c", "quit", "Quit", priority=True),
    ]

    def __init__(self, mols_reader: MoleculesReader, radii_scale: float = 1):
        self.mols_reader = mols_reader
        self.radii_scale = radii_scale
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield MoleculesInterface(self.mols_reader, radii_scale=self.radii_scale)


if __name__ == "__main__":
    from timol.cli.main import cli

    cli()
