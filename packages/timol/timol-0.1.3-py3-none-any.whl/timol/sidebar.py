import os

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from timol.reader import MoleculesReader
from timol.ui import InfoLabel, SimpleMarkdown, Spacer

HELPING_MESSAGE_MARKDOWN = """
## Cheat sheet
- Drag: rotate
- Shift-drag: pan
- h: Hotkey menu
"""


class Sidebar(Widget, can_focus=True):
    index: reactive[int] = reactive(-1)
    centering: reactive[bool] = reactive(False)

    chemical_formula: reactive[str] = reactive("")
    n_atoms: reactive[int] = reactive(0)
    index_string: reactive[str] = reactive("?/?")
    file_name: reactive[str] = reactive("?")

    def __init__(self, mols_reader: MoleculesReader) -> None:
        super().__init__()
        self.mols_reader = mols_reader
        self.file_name = os.path.basename(mols_reader.path)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield SimpleMarkdown("## System")
            yield InfoLabel("File").data_bind(value=Sidebar.file_name)
            yield InfoLabel("Index").data_bind(value=Sidebar.index_string)
            yield InfoLabel("Chemical").data_bind(value=Sidebar.chemical_formula)
            yield InfoLabel("Atoms").data_bind(value=Sidebar.n_atoms)

            yield Label("")  # spacer
            yield SimpleMarkdown("## Info")
            yield InfoLabel("Centering").data_bind(value=Sidebar.centering)

            yield Spacer()
            yield SimpleMarkdown(
                HELPING_MESSAGE_MARKDOWN,
            )

    def watch_index(self, index):
        if index < 0:
            return
        self.n_atoms = self.mols_reader.get_n_atoms(index)
        self.chemical_formula = self.mols_reader.get_chemical_formula(index)
        self.index_string = f"{self.index}/{self.mols_reader.get_n_molecules() - 1}"
