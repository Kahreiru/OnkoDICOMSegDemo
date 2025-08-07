import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QFileDialog
)

import nifti_converter

class NiftiConverter(QWidget):
    """Widget for converting NIfTI segmentations to DICOM RTStruct.

    Provides a UI for selecting NIfTI and DICOM directories and
    initiating the conversion process.
    """

    def __init__(self):
        """Initialize the NiftiConverter widget.

        Sets up the UI elements, including labels, buttons, and layouts,
        and connects the buttons to their respective functions.
        """
        super().__init__()

        self.nifti_path = None
        self.dicom_folder = None
        self.output_path = self.dicom_folder


        self.setWindowTitle("Nifti Converter")
        self.setGeometry(100, 100, 800, 200)

        # Need to change this to grid layout
        self.layout_vert = QVBoxLayout()
        self.layout_horz = QHBoxLayout()
        self.layout_horz2 = QHBoxLayout()
        self.label_select_nifti = QLabel("Nifti Images Path:")
        self.label_selected_nifti = QLabel()
        self.button_select_nifti = QPushButton("Select Nifti")
        self.button_select_nifti = QPushButton()
        self.button_select_nifti.setFixedSize(100, 50)
        self.label_select_dicom = QLabel("Dicom Series Path:")
        self.button_select_dicom = QPushButton("Select Dicom")
        self.button_select_dicom.setFixedSize(100, 50)
        self.layout_horz.addWidget(self.label_select_nifti)
        self.layout_horz.addWidget(self.button_select_nifti)
        self.layout_vert.addLayout(self.layout_horz)
        self.layout_horz2.addWidget(self.label_select_dicom)
        self.layout_horz2.addWidget(self.button_select_dicom)
        self.layout_vert.addLayout(self.layout_horz2)
        self.button_convert = QPushButton("Convert")
        self.button_convert.setFixedSize(150, 50)
        self.layout_vert.addWidget(self.button_convert, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout_vert)

        self.button_select_nifti.clicked.connect(self.select_nifti_path)
        self.button_select_dicom.clicked.connect(self.select_dicom_path)
        self.button_convert.clicked.connect(self.nifti_to_rtstruct_rtutils)

    def select_nifti_path(self):
        self.nifti_path = QFileDialog.getExistingDirectory(self, "Select a file")

        # Ensure directory selected
        if not self.nifti_path:
            return

        self.label_select_nifti.setText(self.nifti_path)

    def select_dicom_path(self):
        self.dicom_folder = QFileDialog.getExistingDirectory(self, "Select Dicom Path")

        # Ensure directory selected
        if not self.dicom_folder:
            return

        self.label_select_dicom.setText(self.dicom_folder)
        self.output_path = f"{self.dicom_folder}/rtss"


    def nifti_to_rtstruct_rtutils(self):
        nifti_converter.nifti_to_rtstruct_conversion(self.nifti_path, self.dicom_folder, self.output_path)
        print(f"Conversion Successful! File saved to {self.output_path}")


if __name__ == "__main__":
    app = QApplication([])
    window = NiftiConverter()
    window.show()
    app.exec()
