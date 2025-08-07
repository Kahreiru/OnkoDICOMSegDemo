import logging
import sys

from PySide6.QtGui import QTextCursor

from redirect_stdout import ConsoleOutputStream
from auto_segmentation_controller import AutoSegmentationController

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QComboBox,
    QTextEdit
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OnkoSegmentationGUI(QWidget):
    def __init__(self):
        """Initialize the OnkoSegmentationGUI.

        Sets up the UI elements, including the task selector, run button, and output display,
        and connects the run button to the segmentation workflow.
        """

        super().__init__()
        self.setWindowTitle("OnkoDICOM + Auto Segmentation")
        self.setGeometry(100, 100, 400, 200)
        self.controller = AutoSegmentationController(self)

        self.layout = QVBoxLayout()

        # Task dropdown
        self.layout.addWidget(QLabel("Select Segmentation Type:"))
        self.task_selector = QComboBox()
        self.task_selector.addItems([
            "total", "total_mr", "lung_vessels", "body", "body_mr",
            "vertebrae_mr", "hip_implant", "pleural_pericard_effusion", "cerebral_bleed",
            "head_glands_cavities", "head_muscles", "headneck_bones_vessels",
            "headneck_muscles", "liver_vessels", "oculomotor_muscles",
            "lung_nodules", "kidney_cysts", "breasts", "liver_segments",
            "liver_segments_mr", "craniofacial_structures",  "abdominal_muscles"
        ])

        self.task_selector.setCurrentText("total")
        self.layout.addWidget(self.task_selector)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        # Run button
        self.run_button = QPushButton("Run Segmentation")
        self.run_button.clicked.connect(self._run_button_clicked)
        self.layout.addWidget(self.run_button)

        self.setLayout(self.layout)

    def _run_button_clicked(self):
        dicom_dir = QFileDialog.getExistingDirectory(self, "Select DICOM CT Series")
        #     if not dicom_dir:
        #         return
        self.controller.run_task(dicom_dir, self.task_selector.currentText(), fast=True)

    def set_progress_text(self, text: str) -> None:
        """Updates the progress text area.

        Appends the given text to the text edit and scrolls to the bottom
        to ensure the latest updates are visible.
        """
        self.text_edit.append(text)
        cursor = self.text_edit.textCursor() # Get cursor from text_edit
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor) # Set cursor for text_edit
        self.text_edit.ensureCursorVisible() # Ensure cursor is visible for text_edit

if __name__ == "__main__":
    app = QApplication([])
    sys.stdout = ConsoleOutputStream()
    window = OnkoSegmentationGUI()
    window.show()
    app.exec()