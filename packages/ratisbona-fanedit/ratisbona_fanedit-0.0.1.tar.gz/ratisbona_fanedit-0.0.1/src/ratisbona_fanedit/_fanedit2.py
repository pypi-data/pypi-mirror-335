import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton, QFileDialog,
)
from PyQt6.QtGui import QPainter, QColor, QMouseEvent, QPen, QPainterPath, QAction
from PyQt6.QtCore import Qt

import sys

GRID_SIZE_X = 144
GRID_SIZE_Y = 11
TOOLBAR_WIDTH = 40  # Fixed width for the toolbar


@dataclass
class SegmentPosition:
    center_point_x: int
    center_point_y: int
    radius_start: float
    radius_end: float
    angle_start: float
    angle_end: float


@dataclass
class SegmentDerivedPoints:
    inner_start_x: float
    inner_start_y: float
    inner_end_x: float
    inner_end_y: float
    outer_start_x: float
    outer_start_y: float
    outer_end_x: float
    outer_end_y: float


def calculate_segment_points(segment: SegmentPosition) -> SegmentDerivedPoints:
    inner_startx, inner_starty = (
        segment.center_point_x - segment.radius_start * math.sin(segment.angle_start),
        segment.center_point_y + segment.radius_start * math.cos(segment.angle_start),
    )
    inner_end_x, inner_end_y = (
        segment.center_point_x - segment.radius_start * math.sin(segment.angle_end),
        segment.center_point_y + segment.radius_start * math.cos(segment.angle_end),
    )

    # Points for the outer arc
    outer_start_x, outer_start_y = (
        segment.center_point_x - segment.radius_end * math.sin(segment.angle_start),
        segment.center_point_y + segment.radius_end * math.cos(segment.angle_start),
    )
    outer_end_x, outer_end_y = (
        segment.center_point_x - segment.radius_end * math.sin(segment.angle_end),
        segment.center_point_y + segment.radius_end * math.cos(segment.angle_end),
    )
    return SegmentDerivedPoints(
        inner_start_x=inner_startx,
        inner_start_y=inner_starty,
        inner_end_x=inner_end_x,
        inner_end_y=inner_end_y,
        outer_start_x=outer_start_x,
        outer_start_y=outer_start_y,
        outer_end_x=outer_end_x,
        outer_end_y=outer_end_y,
    )


def is_in_bounding_rect(segment: SegmentDerivedPoints, x: int, y: int) -> bool:
    min_x = min(
        segment.inner_start_x,
        segment.inner_end_x,
        segment.outer_start_x,
        segment.outer_end_x,
    )
    min_y = min(
        segment.inner_start_y,
        segment.inner_end_y,
        segment.outer_start_y,
        segment.outer_end_y,
    )
    max_x = max(
        segment.inner_start_x,
        segment.inner_end_x,
        segment.outer_start_x,
        segment.outer_end_x,
    )
    max_y = max(
        segment.inner_start_y,
        segment.inner_end_y,
        segment.outer_start_y,
        segment.outer_end_y,
    )
    return min_x <= x <= max_x and min_y <= y <= max_y


def paint(
    segment_derived_points: SegmentDerivedPoints, painter: QPainter, color: QColor
):
    """Draws the segment with two arcs and two connecting lines."""
    pen = QPen(Qt.GlobalColor.white, 1)
    painter.setPen(pen)
    painter.setBrush(color)

    path = QPainterPath()

    # Move to start of inner arc
    path.moveTo(
        segment_derived_points.outer_start_x, segment_derived_points.outer_start_y
    )
    path.lineTo(segment_derived_points.outer_end_x, segment_derived_points.outer_end_y)
    path.lineTo(segment_derived_points.inner_end_x, segment_derived_points.inner_end_y)
    path.lineTo(
        segment_derived_points.inner_start_x, segment_derived_points.inner_start_y
    )
    path.lineTo(
        segment_derived_points.outer_start_x, segment_derived_points.outer_start_y
    )

    # Draw the final shape
    painter.drawPath(path)


def create_segments(
    num_segments: int,
    num_radial_segments: int,
    inner_radius: float,
    outer_radius: float,
    center_x: int,
    center_y: int,
):
    angle_step = 1.8 * math.pi / num_segments
    radial_step = (outer_radius - inner_radius) / num_radial_segments

    segments_rows = []
    for axial_segment_num in range(num_segments):
        segment_cols = []
        phi_segment_start = (
            axial_segment_num * angle_step + angle_step / 4 + 0.1 * math.pi
        )
        for radial_segment_num in range(num_radial_segments):
            r_segment_start = inner_radius + radial_segment_num * radial_step
            segment = SegmentPosition(
                center_point_x=center_x,
                center_point_y=center_y,
                radius_start=r_segment_start,
                radius_end=r_segment_start + radial_step / 2,
                angle_start=phi_segment_start,
                angle_end=phi_segment_start + angle_step / 2,
            )
            segment_cols.append(segment)
        segments_rows.append(segment_cols)
    return segments_rows


class GridCanvas(QWidget):

    def __init__(self, color_grid: list[list[QColor]]):
        super().__init__()
        self.color_grid = color_grid
        self.selected_color = QColor("black")  # Default color
        self.mouse_down = False  # Track if mouse is pressed
        self.segments = []
        self.derived_points = []
        self.resizeEvent(None)

    def resizeEvent(self, a0):
        self.segments = create_segments(
            num_segments=len(self.color_grid),
            num_radial_segments=len(self.color_grid[0]),
            inner_radius=100,
            outer_radius=min(self.width(), self.height()) / 2 - 50,
            center_x=self.width() // 2,
            center_y=self.height() // 2,
        )
        self.derived_points = [
            [calculate_segment_points(segment) for segment in row]
            for row in self.segments
        ]

    def paintEvent(self, event):
        """Draws the grid dynamically resizing to available space."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for ridx, row in enumerate(self.derived_points):
            for cidx, derived_points in enumerate(row):
                paint(derived_points, painter, self.color_grid[ridx][cidx])

    def mousePressEvent(self, event: QMouseEvent):
        """Starts painting on mouse press."""
        self.mouse_down = True
        self.paint_cell(event.position().x(), event.position().y())

    def mouseMoveEvent(self, event: QMouseEvent):
        """Continues painting while the mouse moves."""
        if self.mouse_down:
            self.paint_cell(event.position().x(), event.position().y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stops painting when mouse is released."""
        self.mouse_down = False

    def paint_cell(self, x, y):
        """Paints the cell under the given mouse position."""
        for ridx, row in enumerate(self.derived_points):
            for cidx, segment in enumerate(row):
                if is_in_bounding_rect(segment, x, y):
                    self.color_grid[ridx][cidx] = self.selected_color
                    self.update()
                    return

    def set_color(self, color):
        """Sets the currently selected color."""
        self.selected_color = color


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Editor with Left Toolbar")
        self.setGeometry(100, 100, 800, 800)
        self.color_grid = [[QColor("black") for _ in range(11)] for _ in range(144)]

        self.canvas = GridCanvas(self.color_grid)

        # Toolbar with color buttons (fixed width)
        toolbar = QWidget()
        toolbar.setFixedWidth(TOOLBAR_WIDTH)
        toolbar_layout = QVBoxLayout()
        toolbar_layout.setSpacing(5)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)

        self.colors = ["red", "yellow", "green", "cyan", "blue", "magenta", "white", "black"]
        self.qcolors = [QColor(color) for color in self.colors]

        for color, qcolor in zip(self.colors, self.qcolors):
            btn = QPushButton()
            btn.setStyleSheet(f"background-color: {color}; border: none;")
            btn.setFixedSize(30, 30)
            btn.clicked.connect(lambda _, q=qcolor: self.canvas.set_color(q))
            toolbar_layout.addWidget(btn)

        toolbar.setLayout(toolbar_layout)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(toolbar)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.create_menu()

    def color_name_by_qcolor(self, qcolor):
        for color, color_qcolor in zip(self.colors, self.qcolors):
            if color_qcolor == qcolor:
                return color
        return "black"

    def qcolor_by_color_name(self, color_name):
        for color, color_qcolor in zip(self.colors, self.qcolors):
            if color == color_name:
                return color_qcolor
        return QColor("black")

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # New Action
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_canvas)
        file_menu.addAction(new_action)

        # Load Action
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_image)
        file_menu.addAction(load_action)

        # Save Action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        # Quit Action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def new_canvas(self):
        for i in range(len(self.color_grid)):
            for j in range(len(self.color_grid[0])):
                self.color_grid[i][j] = QColor("black")

        self.canvas.update()

    def load_image(self):
        options = (
            QFileDialog.Option.DontUseNativeDialog
        )  # Optional: Use Qt's built-in dialog
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Json-Images (*.json);;All Files (*)",
            options=options,
        )

        if not file_name:  # If the user selected a file
            return
        fan_image = json.loads(Path(file_name).read_text())
        for ridx, row in enumerate(fan_image):
            for cidx, entry in enumerate(reversed(row["column"])):
                self.color_grid[ridx][cidx] = (
                    self.qcolor_by_color_name(row["color"])
                    if entry
                    else QColor("black")
                )
        self.canvas.update()

    def save_image(self):

        options = (
            QFileDialog.Option.DontUseNativeDialog
        )  # Optional: Use Qt's built-in dialog
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Json-Images (*.json);;All Files (*)",
            options=options,
        )

        if not file_name:  # If the user selected a file
            return

        print(f"File chosen: {file_name}")

        fan_image = []
        for row in self.color_grid:
            color_names = [self.color_name_by_qcolor(color) for color in reversed(row)]
            stats = defaultdict(int)
            for color_name in color_names:
                if color_name == "black":
                    continue
                stats[color_name] += 1
            dominant_color = max(stats, key=stats.get) if len(stats) > 0 else "black"
            fan_image.append(
                {
                    "column": [1 if color_name != "black" else 0 for color_name in color_names],
                    "color": dominant_color,
                }
            )
        the_json = "[\n" + ",\n".join(json.dumps(entry) for entry in fan_image) + "]"
        Path(file_name).write_text(the_json)

def fanedit_main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
