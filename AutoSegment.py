import os
import glob
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QComboBox, QMessageBox
)
from totalsegmentator.python_api import totalsegmentator
from platipy.dicom.io import nifti_to_rtstruct


class OnkoSegmentationGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OnkoDICOM + TotalSegmentator")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        # Task dropdown
        self.layout.addWidget(QLabel("Select Segmentation Type:"))
        self.task_selector = QComboBox()
        self.task_selector.addItems([
            "total", "organs", "bones", "muscles", "vasculature",
            "lung_vessels", "pleural", "heartchambers", "cerebral_bleed"
        ])
        self.task_selector.setCurrentText("total")
        self.layout.addWidget(self.task_selector)

        # Run button
        self.run_button = QPushButton("Run Segmentation")
        self.run_button.clicked.connect(self.run_segmentation_workflow)
        self.layout.addWidget(self.run_button)

        self.setLayout(self.layout)

    def run_segmentation_workflow(self):
        dicom_dir = QFileDialog.getExistingDirectory(self, "Select DICOM CT Series")
        if not dicom_dir:
            return

        # Saves the nifti segmentations into segmentations folder in same dir
        output_dir = os.path.join(dicom_dir, "segmentations")
        os.makedirs(output_dir, exist_ok=True)

        selected_task = self.task_selector.currentText()

        try:
            totalsegmentator(
                input=dicom_dir,
                output=output_dir,
                task=selected_task,
                device="cpu",
                fast=True
            )

            mask_file = glob.glob(os.path.join(output_dir, selected_task, "*mask.nii.gz"))
            output_rt = os.path.join(dicom_dir, "rtss.dcm")

            # Convert the Nifiti output to DICOM rtss file
            nifti_to_rtstruct.convert_nifti(
                dcm_path=dicom_dir,
                mask_input=mask_file,
                output_file=output_rt
            )

            QMessageBox.information(self, "Success",
                                    f"Segmentation complete for '{selected_task}'\nOutput: {output_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Segmentation Failed", str(e))


if __name__ == "__main__":
    app = QApplication([])
    window = OnkoSegmentationGUI()
    window.show()
    app.exec()