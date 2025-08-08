
import logging
import platform
import sys

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QGridLayout, QWidget, QVBoxLayout, QStackedWidget, QMainWindow, QHBoxLayout, QSplitter, \
    QLabel, QFileDialog

from StyleSheetReader import StyleSheetReader
from auto_segment_tab import AutoSegmentationTab
from dicom_viewer_tab import DicomViewer


class UIMainWindow(QMainWindow):

    def __init__(self):
        """Initialize the main window.

        Sets up the main window, including stylesheet, minimum size, title, and central widget.
        """
        super().__init__()

        self.stylesheet: StyleSheetReader = StyleSheetReader()
        self.setMinimumSize(1080, 800)
        self.setWindowTitle("AutoSegmentation Demo")
        self.setStyleSheet(self.stylesheet())
        self.dicom_dir: str = QFileDialog.getExistingDirectory(self, "Select DICOM CT Series")

        self.setup_central_widget()

    def setup_central_widget(self):
        """Set up the central widget.

        Creates and configures the central widget, which includes a splitter for the left
        and right panels, and adds the footer.
        """

        # Create central widget for multipanel view
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a QSplitter for horizontal division
        splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.central_widget_layout = QVBoxLayout(central_widget)

        # Left panel contains tabs
        self.left_panel = QtWidgets.QTabWidget()
        self.left_panel.setMinimumWidth(200)
        self.left_panel.setMaximumWidth(400)

        # Right Panel Contains Views
        self.right_panel = QtWidgets.QTabWidget()
        self.right_panel.setMinimumWidth(300)
        self.right_panel.setMaximumWidth(900)
        self.right_panel.setMinimumHeight(600)

        # Add Auto-Segmentation to the left panel
        self.left_panel.addTab(AutoSegmentationTab(self.dicom_dir), "Auto-Segment")

        # Add DicomViewer to the right panel
        self.right_panel.addTab(DicomViewer(self.dicom_dir), "Dicom Viewer")

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)

        # Add the splitter to the central widget's layout
        self.central_widget_layout.addWidget(splitter)

        self.footer = QWidget()
        self.create_footer()

        self.central_widget_layout.addWidget(self.footer)

    # Borrowed from OnkoDicom
    def create_footer(self):
        """Create the footer widget.

        Creates and configures the footer widget, adding a label with version information
        aligned to the right.
        """
        self.footer.setFixedHeight(15)
        layout_footer = QtWidgets.QHBoxLayout(self.footer)
        layout_footer.setContentsMargins(0, 0, 0, 0)

        label_footer = QtWidgets.QLabel("@OnkoDICOM2021 v 6.0.1")
        label_footer.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        layout_footer.addWidget(label_footer)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UIMainWindow()
    window.show()
    sys.exit(app.exec())