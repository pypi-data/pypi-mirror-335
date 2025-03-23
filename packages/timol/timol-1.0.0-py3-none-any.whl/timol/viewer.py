from functools import lru_cache
from math import floor
from typing import Dict

import numpy as np
from ase.data.colors import jmol_colors
from numpy.typing import NDArray
from rich.color import Color as RichColor
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import Style
from scipy.spatial.transform import Rotation
from textual import events
from textual.reactive import reactive
from textual.widget import Widget

from timol.reader import MoleculesReader

jmol_colors[0] = (0, 0, 0)


class HDRenderable:
    def __init__(
        self,
        matrix: NDArray,
        colors: NDArray,
        background_color: RichColor = RichColor.from_rgb(0, 0, 0),
    ):
        self.background_color = background_color
        self.matrix = matrix
        self.colors = colors
        self.n_indices = len(colors)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        new_line = Segment.line()

        colors = self.colors

        @lru_cache(maxsize=1024)
        def get_style(i_top, i_bottom) -> Style:
            if i_top >= self.n_indices:
                # unnecessary default, just useful fornot crashing while debugging...
                top_color = RichColor.from_rgb(0, 255, 0)
            elif i_top < 0:
                top_color = self.background_color
            else:
                top_color = RichColor.from_rgb(*colors[i_top] * 255)

            if i_bottom >= self.n_indices:
                # unnecessary default, just useful fornot crashing while debugging...
                bottom_color = RichColor.from_rgb(0, 255, 0)
            elif i_bottom < 0:
                bottom_color = self.background_color
            else:
                bottom_color = RichColor.from_rgb(*colors[i_bottom] * 255)

            return Style(color=top_color, bgcolor=bottom_color)

        x, y = self.matrix.shape
        for i in range(0, x, 2):
            n_same_style = 0
            last_style, style = None, None
            for j in range(y):
                style = get_style(self.matrix[i, j], self.matrix[i + 1, j])
                if style is not last_style:
                    yield Segment("▀" * n_same_style, last_style)
                    n_same_style = 1
                else:
                    n_same_style += 1

                last_style = style

            if (n_same_style > 0) and (style is not None):
                yield Segment("▀" * n_same_style, style)
                style = None

            yield new_line


class Renderable:
    def __init__(
        self,
        matrix: NDArray,
        colors: NDArray,
        background_color: RichColor = RichColor.from_rgb(0, 0, 0),
    ):
        self.background_color = background_color
        self.matrix = matrix
        self.colors = colors
        self.n_indices = len(colors)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        new_line = Segment.line()

        colors = self.colors

        @lru_cache(maxsize=1024)
        def get_style(i_top, i_bottom) -> Style:
            if i_top >= self.n_indices:
                # unnecessary default, just useful fornot crashing while debugging...
                top_color = RichColor.from_rgb(0, 255, 0)
            elif i_top < 0:
                top_color = self.background_color
            else:
                top_color = RichColor.from_rgb(*colors[i_top] * 255)

            if i_bottom >= self.n_indices:
                # unnecessary default, just useful fornot crashing while debugging...
                bottom_color = RichColor.from_rgb(0, 255, 0)
            elif i_bottom < 0:
                bottom_color = self.background_color
            else:
                bottom_color = RichColor.from_rgb(*colors[i_bottom] * 255)

            return Style(bgcolor=bottom_color)

        x, y = self.matrix.shape
        for i in range(0, x, 2):
            n_same_style = 0
            last_style, style = None, None
            for j in range(y):
                style = get_style(self.matrix[i, j], self.matrix[i + 1, j])
                if style is not last_style:
                    yield Segment(" " * n_same_style, last_style)
                    n_same_style = 1
                else:
                    n_same_style += 1

                last_style = style

            if (n_same_style > 0) and (style is not None):
                yield Segment(" " * n_same_style, style)
                style = None

            yield new_line


class MolViewer(Widget):
    index: reactive[int] = reactive(0)
    centering: reactive[bool] = reactive(False)
    radii_scale: reactive[float] = reactive(1)

    coordinates: NDArray
    sizes: NDArray
    colors: NDArray
    yaw: float = 0
    pitch: float = 0
    scale: float = 10
    offset: NDArray = np.zeros(2)
    background_color: RichColor
    _centers_cache: Dict[int, NDArray]

    DEFAULT_CSS = """
    MolViewer{
        width: 1fr;
        height: 1fr;
        background: red;
    }
    """

    def __init__(
        self,
        mols_reader: MoleculesReader,
        background_color: NDArray = np.array((0, 0, 0)),
    ):
        self.set_background_color(background_color)
        self.mols_reader = mols_reader
        self._centers_cache = {}
        super().__init__()

    def set_background_color(self, background_color: NDArray):
        self.background_color = RichColor.from_rgb(*background_color)

    def reset_view(self):
        self.pitch = 0
        self.yaw = 0
        self.scale = 10
        self.offset[:] = 0
        self.radii_scale = 1
        self.refresh()

    def get_system_center(self):
        if self.index not in self._centers_cache:
            self._centers_cache[self.index] = np.mean(
                self.mols_reader.get_positions(self.index), axis=0
            )
            return self.get_system_center()

        return self._centers_cache[self.index]

    def build_matrix(self) -> NDArray:
        h, w = self.size.height * 2, self.size.width
        matrix = -np.ones((h, w)).astype(int)

        R, sizes, distances = self.get_projection()

        sizes = sizes * self.radii_scale

        x_center, y_center = w / 2, h / 2

        # from furthest to closest
        # everything gets converted to pixel space
        for idx in np.argsort(-distances):
            x, y = R[idx] * self.scale
            x += x_center
            y += y_center

            pixel_size = sizes[idx] * self.scale

            x_min = max(0, int(np.round(x - pixel_size)))
            x_max = min(w - 1, int(np.round(x + pixel_size)))

            y_min = max(0, int(np.round(y - pixel_size)))
            y_max = min(h - 1, int(np.round(y + pixel_size)))

            row_idxs, col_idxs = [], []
            for xn in range(x_min, x_max):
                for yn in range(y_min, y_max):
                    if np.sqrt((xn + 0.5 - x) ** 2 + (yn + 0.5 - y) ** 2) > pixel_size:
                        continue

                    col_idxs.append(xn)
                    row_idxs.append(yn)

            matrix[row_idxs, col_idxs] = idx  # 0 is background

        return np.flip(matrix, axis=0)

    def rotate_camera(self, yaw: float = 0, pitch: float = 0):
        self.yaw += yaw
        self.pitch += pitch
        self.refresh()

    def shift_offset(self, x: float = 0, y: float = 0):
        self.offset[0] += x
        self.offset[1] += y
        self.refresh()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if event.button == 1:
            if event.shift:
                self.shift_offset(-0.1 * event.delta_x, 0.1 * event.delta_y)

            else:
                self.rotate_camera(-5 * event.delta_x, 5 * event.delta_y)

        elif event.button == 2:
            return

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        self.zoom_by(-1)

    def _on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        self.zoom_by(1)

    def zoom_by(self, amount: int):
        if self.scale <= 1:
            self.scale = max(0.75, self.scale + 0.05 * amount)
        else:
            self.scale = floor(max(1, self.scale + amount))
        self.refresh()

    def get_projection(self) -> tuple[NDArray, NDArray, NDArray]:
        """Very rudimentary orthographic projection along the x-axis for the sake
        of simplicity and efficiency.

        :return: Coordinates (N, 2), sizes (N), distances (N)
        :rtype: tuple[NDArray, NDArray, NDArray]
        """

        rot = Rotation.from_euler("zyx", [self.yaw, self.pitch, 0], degrees=True)
        R = self.mols_reader.get_positions(self.index)
        if self.centering:
            R -= self.get_system_center()
        R = rot.apply(R)
        return R[:, 1:] - self.offset, self.mols_reader.get_radii(self.index), R[:, 0]

    def build(self) -> list[str]:
        lines = []

        # lines = [f"[@{self.bg}] "*self.width] * self.get_height()
        matrix = self.build_matrix()
        for i in range(matrix.shape[0]):
            line = ""
            # last_idx = -1
            for j in range(matrix.shape[1]):
                idx = matrix[i][j]
                # if idx != last_idx:
                #     line += f"{idx}"
                #     last_idx = idx
                # line += f" "
                if idx > 0:
                    line += f"{idx}"
                else:
                    line += f"[on #000000]{idx}[/on #000000]"
            lines.append(line)

        return lines

    def render(self) -> RenderableType:
        colors = jmol_colors[self.mols_reader.get_atomic_numbers(self.index)]
        return HDRenderable(
            self.build_matrix(), colors, background_color=self.background_color
        )
