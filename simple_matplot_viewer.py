import os
import numpy as np
import SimpleITK as sitk
from skimage import measure
from scipy.ndimage import gaussian_filter1d

from rtstruct_loader import load_rtstruct_masks


from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QSlider, QComboBox, QCheckBox, QScrollArea, QGroupBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class DicomNiftiViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DICOM + NIfTI Segmentation Viewer")

        # UI Elements
        self.canvas = FigureCanvas(plt.Figure())
        self.ax = self.canvas.figure.add_subplot(111)
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.update_display)

        self.view_selector = QComboBox()
        self.view_selector.addItems(["Axial", "Coronal", "Sagittal"])
        self.view_selector.currentIndexChanged.connect(self.update_display)

        self.overlay_checkboxes = []
        self.overlay_visibility = []

        self.scroll_area = QScrollArea()
        self.checkbox_container = QVBoxLayout()
        self.scroll_area.setWidgetResizable(True)
        checkbox_group = QGroupBox("Segmentations")
        checkbox_group.setLayout(self.checkbox_container)
        self.scroll_area.setWidget(checkbox_group)

        # Data holders
        self.ct_array = None
        self.seg_arrays = []
        self.seg_names = []
        self.seg_colors = []
        self.spacing = []

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.view_selector)
        layout.addWidget(self.slider)
        layout.addWidget(self.scroll_area)

        btn_layout = QHBoxLayout()
        self.btn_load_dicom = QPushButton("Load DICOM Series")
        self.btn_load_seg = QPushButton("Load NIfTI Segmentations")
        self.btn_load_rtstruct = QPushButton("Load RTSTRUCT")
        self.btn_load_dicom.clicked.connect(self.load_dicom)
        self.btn_load_seg.clicked.connect(self.load_segmentations)
        self.btn_load_rtstruct.clicked.connect(self.load_rtstruct)
        btn_layout.addWidget(self.btn_load_dicom)
        btn_layout.addWidget(self.btn_load_seg)
        btn_layout.addWidget(self.btn_load_rtstruct)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_dicom(self):
        folder = QFileDialog.getExistingDirectory(self, "Select DICOM Folder")
        if not folder:
            return

        # self.spacing = sitk.ReadImage(files[0]).GetSpacing()
        # print(self.spacing)

        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(folder)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()
        self.spacing = image.GetSpacing()
        print(self.spacing)
        image = sitk.DICOMOrient(image, 'LPS')
        self.ct_array = sitk.GetArrayFromImage(image)  # (z, y, x)
        self.slider.setMaximum(self.ct_array.shape[0] - 1)
        self.update_display()

    def load_segmentations(self) -> None:
        """
        Load NIfTI segmentation files.

        Opens a file dialog to select multiple NIfTI segmentation files,
        reads them using SimpleITK, and stores them for display.
        It also creates checkboxes for each segmentation file to control visibility.

        """

        files, _ = QFileDialog.getOpenFileNames(self, "Select NIfTI Segmentations", filter="*.nii.gz")
        if not files:
            return

        # Clear all previous data
        self.seg_arrays.clear()
        self.seg_names.clear()
        self.seg_colors.clear()
        self.overlay_visibility.clear()

        for i in reversed(range(self.checkbox_container.count())):
            self.checkbox_container.itemAt(i).widget().deleteLater()

        base_colors = plt.colormaps['tab20']

        # Iterate over the segmentation files load, add check box, and display
        for i, file_path in enumerate(files):
            seg_image = sitk.ReadImage(file_path)
            seg_image = sitk.DICOMOrient(seg_image, 'LPS')
            seg_array = sitk.GetArrayFromImage(seg_image).astype(bool)
            self.seg_arrays.append(seg_array)
            self.seg_names.append(os.path.basename(file_path))
            self.seg_colors.append(base_colors(i))

            checkbox = QCheckBox(os.path.basename(file_path))
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_display)
            self.overlay_checkboxes.append(checkbox)
            self.overlay_visibility.append(True)
            self.checkbox_container.addWidget(checkbox)

        self.update_display()

    def load_rtstruct(self):
        rtstruct_path, _ = QFileDialog.getOpenFileName(self, "Select RTSTRUCT File", filter="*.dcm")
        if not rtstruct_path:
            return

        dicom_dir = QFileDialog.getExistingDirectory(self, "Select CT DICOM Folder")
        if not dicom_dir:
            return

        mask_dict = load_rtstruct_masks(rtstruct_path, dicom_dir)

        self.seg_arrays.clear()
        self.seg_names.clear()
        self.seg_colors.clear()
        self.overlay_visibility.clear()

        # Clear old checkboxes
        for i in reversed(range(self.checkbox_container.count())):
            self.checkbox_container.itemAt(i).widget().deleteLater()

        base_colors = plt.colormaps['tab20']

        for i, (name, mask) in enumerate(mask_dict.items()):
            self.seg_arrays.append(mask.astype(bool))
            self.seg_names.append(name)
            self.seg_colors.append(base_colors(i))

            checkbox = QCheckBox(name)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_display)
            self.overlay_checkboxes.append(checkbox)
            self.overlay_visibility.append(True)
            self.checkbox_container.addWidget(checkbox)

        self.slider.setMaximum(self.ct_array.shape[0] - 1)
        self.update_display()

    def update_display(self):
        self.ax.clear()
        if self.ct_array is None:
            return

        view = self.view_selector.currentText()
        axis = {"Axial": 0, "Coronal": 1, "Sagittal": 2}[view]

        if axis == 0:
            max_idx = self.ct_array.shape[0] - 1
            print(max_idx)
        elif axis == 1:
            max_idx = self.ct_array.shape[1] - 1
            print(max_idx)
        else:
            max_idx = self.ct_array.shape[2] - 1
            print(max_idx)

        self.slider.setMaximum(max_idx)
        idx = self.slider.value()

        if axis == 0: # axial
            base_slice = self.ct_array[idx, :, :]
            pix_aspect = self.spacing[0]
        elif axis == 1: # coronal
            base_slice = self.ct_array[:, idx, :]
            pix_aspect = self.spacing[2]
        else: # sagittal
            base_slice = self.ct_array[:, :, idx]
            pix_aspect = self.spacing[2]

        self.ax.imshow(base_slice, cmap='gray', aspect=pix_aspect, interpolation='nearest')

        for i, seg_array in enumerate(self.seg_arrays):
            visible = self.overlay_checkboxes[i].isChecked()
            if not visible:
                continue

            if idx < seg_array.shape[axis]:
                if axis == 0:
                    mask_slice = seg_array[idx, :, :].astype(float)
                elif axis == 1:
                    mask_slice = seg_array[:, idx, :].astype(float)
                else:
                    mask_slice = seg_array[:, :, idx].astype(float)

                # Find contours at mask boundary 0.5
                contours = measure.find_contours(mask_slice, 0.5)
                rgba = self.seg_colors[i]

                for contour in contours:
                    # Smooth contour coordinates
                    x = contour[:, 1]
                    y = contour[:, 0]

                    # Gaussian smoothing
                    x_smooth = gaussian_filter1d(x, sigma=0.8)
                    y_smooth = gaussian_filter1d(y, sigma=1.3)

                    # Plot filled polygon with transparency
                    self.ax.fill(x_smooth, y_smooth, color=rgba, alpha=0.3)

                    # Optionally plot the contour edge
                    # self.ax.plot(x_smooth, y_smooth, color=rgba, linewidth=1.0)

        self.ax.set_title(f"{view} View - Slice {idx}")
        self.canvas.draw()


if __name__ == "__main__":
    import sys
    from PySide6.QtCore import Qt

    app = QApplication(sys.argv)
    viewer = DicomNiftiViewer()
    viewer.resize(1000, 800)
    viewer.show()
    sys.exit(app.exec())