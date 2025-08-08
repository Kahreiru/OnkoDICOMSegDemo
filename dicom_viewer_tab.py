import os
import numpy as np
import SimpleITK as sitk
from PySide6.QtGui import QImage, QPixmap, QPolygonF, QColor, QPainter, QPen, QBrush
from skimage import measure
from scipy.ndimage import gaussian_filter1d
from StyleSheetReader import StyleSheetReader
from rtstruct_loader import load_rtstruct_masks
import logging

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QSlider, QCheckBox, QScrollArea, QGroupBox, QGridLayout, QSplitter, QFrame,
    QLabel
)

from PySide6.QtCore import Qt, QSize, QPointF

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import random

# Helper function to generate contour colors
def generate_random_rgba(alpha=120):
    return tuple(random.randint(0, 255) for _ in range(3)) + (alpha,)

class DicomViewer(QWidget):
    def __init__(self, dicom_dir: str) -> None:
        super().__init__()
        self.setWindowTitle("DICOM Segmentation Viewer")
        self.dicom_dir = dicom_dir
        self.nifti_dir = os.path.join(self.dicom_dir, "segmentations")
        self.style_sheet: StyleSheetReader = StyleSheetReader()

        # UI Elements
        # Axial View Elements
        self.canvas_axial = QLabel()
        self.canvas_axial.setMinimumSize(QSize(128, 128))
        # self.ax = self.canvas_axial.figure.add_subplot()
        self.axial_slider = QSlider()
        self.axial_slider.setStyleSheet(self.style_sheet())

        # Coronal View Elements
        # self.canvas_coronal = FigureCanvas(plt.Figure())
        # self.ax_coronal = self.canvas_coronal.figure.add_subplot()
        self.canvas_coronal = QLabel()
        self.canvas_coronal.setMinimumSize(QSize(128, 128))
        self.coronal_slider = QSlider()
        self.coronal_slider.setStyleSheet(self.style_sheet())

        # Sagittal View Elements
        # self.canvas_sagittal = FigureCanvas(plt.Figure())
        # self.ax_sagittal = self.canvas_sagittal.figure.add_subplot()
        self.canvas_sagittal = QLabel()
        self.canvas_sagittal.setMinimumSize(QSize(128, 128))
        self.sagittal_slider = QSlider()
        self.sagittal_slider.setStyleSheet(self.style_sheet())

        # Connect slider signals
        self.axial_slider.valueChanged.connect(self.update_display)
        self.coronal_slider.valueChanged.connect(self.update_display)
        self.sagittal_slider.valueChanged.connect(self.update_display)

        self.overlay_checkboxes = []
        self.overlay_visibility = []

        # Setup check box group and scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet(self.style_sheet())
        self.checkbox_container = QVBoxLayout()
        self.scroll_area.setWidgetResizable(True)
        checkbox_group = QGroupBox("Segmentations")
        checkbox_group.setStyleSheet(self.style_sheet())
        checkbox_group.setLayout(self.checkbox_container)
        self.scroll_area.setWidget(checkbox_group)

        # Data holders
        self.ct_array = None
        # self.seg_colors = []
        self.seg_colors = [
            (255, 0, 0, 120),    # Red
            (0, 255, 0, 120),    # Green
            (0, 0, 255, 120),    # Blue
            (255, 255, 0, 120),  # Yellow
            (255, 0, 255, 120),  # Magenta
            (0, 255, 255, 120),  # Cyan
        ]
        self.seg_arrays = []
        self.seg_names = []
        self.spacing = []

        # Layouts
        main_layout = QVBoxLayout()
        views_layout = QGridLayout()

        # Axial View Layout
        axial_view_layout = QHBoxLayout()
        axial_view_layout.addWidget(self.canvas_axial)
        axial_view_layout.addWidget(self.axial_slider)

        # Coronal View Layout
        coronal_view_layout = QHBoxLayout()
        coronal_view_layout.addWidget(self.canvas_coronal)
        coronal_view_layout.addWidget(self.coronal_slider)

        # Sagittal View Layout
        sagittal_view_layout = QHBoxLayout()
        sagittal_view_layout.addWidget(self.canvas_sagittal)
        sagittal_view_layout.addWidget(self.sagittal_slider)

        views_layout.addLayout(axial_view_layout, 0, 0)
        views_layout.addLayout(coronal_view_layout, 0, 1)
        views_layout.addLayout(sagittal_view_layout, 1, 0)

        # Put views into QFrame to allow splitter
        views_layout_frame = QFrame()
        views_layout_frame.setLayout(views_layout)

        # Use splitter to allow resize of check box scroll area
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(views_layout_frame)
        splitter.addWidget(self.scroll_area)
        main_layout.addWidget(splitter)

        # Load button layout
        btn_layout = QHBoxLayout()
        self.btn_load_seg = QPushButton("Load Segmentations")
        self.btn_load_seg.setStyleSheet(self.style_sheet())
        self.btn_load_seg.clicked.connect(self.load_segmentations)
        btn_layout.addWidget(self.btn_load_seg)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Load dicom image set
        self.load_dicom()

    def load_dicom(self):
        """
        Function loads the image set from the selected dicom directory.
        :return: None
        """
        folder = self.dicom_dir
        if not folder:
            logger.error("No DICOM directory specified")
            return

        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(folder)
        reader.SetFileNames(dicom_names)
        image = reader.Execute()

        self.spacing = image.GetSpacing()
        image = sitk.DICOMOrient(image, 'LPS')
        self.ct_array = sitk.GetArrayFromImage(image)  # (z, y, x) format

        self.update_display()
        # self.load_rtstruct()

        # Generate colors array
        self.seg_colors = [generate_random_rgba() for _ in range(len(self.ct_array))]

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

        # Iterate over the segmentation files load, add check box, and display
        for i, file_path in enumerate(files):
            seg_image = sitk.ReadImage(file_path)
            seg_image = sitk.DICOMOrient(seg_image, 'LPS')
            seg_array = sitk.GetArrayFromImage(seg_image).astype(bool)
            self.seg_arrays.append(seg_array)
            self.seg_names.append(os.path.basename(file_path))
            # self.seg_colors.append(base_colors(i))

            checkbox = QCheckBox(os.path.basename(file_path))
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_display)
            self.overlay_checkboxes.append(checkbox)
            self.overlay_visibility.append(True)
            self.checkbox_container.addWidget(checkbox)

        self.update_display()

    def load_rtstruct(self):
        # rtstruct_path, _ = QFileDialog.getOpenFileName(self, "Select RTSTRUCT File", filter="*.dcm")
        # if not rtstruct_path:
        #     return
        #
        # dicom_dir = QFileDialog.getExistingDirectory(self, "Select CT DICOM Folder")
        # if not dicom_dir:
        #     return

        rtstruct_path = os.path.join(self.dicom_dir, "rtss.dcm")

        mask_dict = load_rtstruct_masks(rtstruct_path, self.dicom_dir)

        self.seg_arrays.clear()
        self.seg_names.clear()
        self.seg_colors.clear()
        self.overlay_visibility.clear()

        # Clear old checkboxes
        for i in reversed(range(self.checkbox_container.count())):
            self.checkbox_container.itemAt(i).widget().deleteLater()

        # base_colors = plt.colormaps['tab20']

        for i, (name, mask) in enumerate(mask_dict.items()):
            self.seg_arrays.append(mask.astype(bool))
            self.seg_names.append(name)
            # self.seg_colors.append(base_colors(i))

            checkbox = QCheckBox(name)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_display)
            self.overlay_checkboxes.append(checkbox)
            self.overlay_visibility.append(True)
            self.checkbox_container.addWidget(checkbox)

        self.update_display()

    def update_display(self):

        if self.ct_array is None:
            logger.warning("No image data present!")
            return

        # Set slice/index maximums for each axis
        axial_max_idx = self.ct_array.shape[0] - 1
        coronal_max_idx = self.ct_array.shape[1] - 1
        sagittal_max_idx = self.ct_array.shape[2] - 1

        # Set max slice/index for each slider
        self.axial_slider.setMaximum(axial_max_idx)
        self.coronal_slider.setMaximum(coronal_max_idx)
        self.sagittal_slider.setMaximum(sagittal_max_idx)

        # Get axial base slice and aspect ratio
        axial_base_slice = self.ct_array[self.axial_slider.value(), :, :]
        # aspect refers to spacing between rows / spacing between columns
        axial_pix_aspect = self.spacing[1] / self.spacing[0]

        # Clip negative values in array, normalise, and create pixel array (0 - 255)
        axial_norm = np.clip(axial_base_slice, 0, np.percentile(axial_base_slice, 99))
        axial_norm = ((axial_norm - axial_norm.min()) / (axial_norm.ptp()) * 255).astype(np.uint8)

        # Get axial data for pixmap conversion
        axial_height, axial_width = axial_norm.shape
        bytes_per_line = axial_width

        # Convert image to QPixmap
        axial_q_image = QImage(axial_norm.data, axial_width, axial_height, bytes_per_line, QImage.Format.Format_Grayscale8)
        axial_pixmap = QPixmap.fromImage(axial_q_image)

        # Get Coronal base slice and aspect ratio
        coronal_base_slice = np.rot90(self.ct_array[:, self.coronal_slider.value(), :], 2)
        coronal_pix_aspect = self.spacing[2] / self.spacing[0]

        # Clip negative values in array, normalise, and create pixel array (0 - 255)
        coronal_norm = np.clip(coronal_base_slice, 0, np.percentile(coronal_base_slice, 99))
        coronal_norm = ((coronal_norm - coronal_norm.min()) / (coronal_norm.ptp()) * 255).astype(np.uint8)

        # Get QImage Data
        coronal_height, coronal_width = coronal_norm.shape
        bytes_per_line = coronal_width

        # Convert image to QPixmap
        coronal_q_image = QImage(coronal_norm.data, coronal_width, coronal_height, bytes_per_line,
                               QImage.Format.Format_Grayscale8)
        coronal_pixmap = QPixmap.fromImage(coronal_q_image)

        # Get Sagittal base slice and aspect ratio
        sagittal_base_slice = np.rot90(self.ct_array[:, :, self.sagittal_slider.value()], 2)
        sagittal_pix_aspect = self.spacing[2] / self.spacing[1]

        sagittal_norm = np.clip(sagittal_base_slice, 0, np.percentile(sagittal_base_slice, 99))
        sagittal_norm = ((sagittal_norm - sagittal_norm.min()) / (sagittal_norm.ptp()) * 255).astype(np.uint8)

        # Get axial data for pixmap conversion
        sagittal_height, sagittal_width = sagittal_norm.shape
        bytes_per_line = sagittal_width

        # Convert image to QPixmap
        sagittal_q_image = QImage(sagittal_norm.data, sagittal_width, sagittal_height, bytes_per_line,
                               QImage.Format.Format_Grayscale8)
        sagittal_pixmap = QPixmap.fromImage(sagittal_q_image)


        for i, seg_array in enumerate(self.seg_arrays):
            visible = self.overlay_checkboxes[i].isChecked()
            if not visible:
                continue

            # rgba_colors = self.seg_colors[i]  # (R, G, B, A)

            mask_slice_axial = seg_array[self.axial_slider.value(), :, :].astype(float)
            mask_slice_coronal = np.rot90(seg_array[:, self.coronal_slider.value(), :].astype(float), 2)
            mask_slice_sagittal = np.rot90(seg_array[:, :, self.sagittal_slider.value()].astype(float), 2)

            # Find contours at mask boundary 0.5
            axial_contours = measure.find_contours(mask_slice_axial, 0.5)
            coronal_contours = measure.find_contours(mask_slice_coronal, 0.5)
            sagittal_contours = measure.find_contours(mask_slice_sagittal, 0.5)

            # Start painting on top of axial pixmap
            painter = QPainter(axial_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Smooth and then draw/display axial contour
            for contour in axial_contours:
                # Smooth contour coordinates
                x = contour[:, 1]
                y = contour[:, 0]

                # Gaussian smoothing
                x_smooth = gaussian_filter1d(x, sigma=0.8)
                y_smooth = gaussian_filter1d(y, sigma=1.3)

                # Draw filled polygon with transparency
                axial_poly = QPolygonF()
                for px, py in zip(x_smooth, y_smooth):
                    axial_poly.append(QPointF(px, py))

                # Draw filled polygon with transparency
                color = QColor(255, 0, 0, 120)
                painter.setPen(QPen(color, 1.0))
                painter.setBrush(QBrush(color))
                painter.drawPolygon(axial_poly)

            painter.end()

            # Start painting on top of coronal pixmap
            painter = QPainter(coronal_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            for contour in coronal_contours:
                # Smooth contour coordinates
                x = contour[:, 1]
                y = contour[:, 0]

                # Gaussian smoothing
                x_smooth = gaussian_filter1d(x, sigma=0.8)
                y_smooth = gaussian_filter1d(y, sigma=1.3)

                # Draw filled polygon with transparency
                coronal_poly = QPolygonF()
                for px, py in zip(x_smooth, y_smooth):
                    coronal_poly.append(QPointF(px, py))

                # Draw filled polygon with transparency
                color = QColor(255, 0, 0, 120)
                painter.setPen(QPen(color, 1.0))
                painter.setBrush(QBrush(color))
                painter.drawPolygon(coronal_poly)

            painter.end()

            # Start painting on top of coronal pixmap
            painter = QPainter(sagittal_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            for contour in sagittal_contours:
                # Smooth contour coordinates
                x = contour[:, 1]
                y = contour[:, 0]

                # Gaussian smoothing
                x_smooth = gaussian_filter1d(x, sigma=0.8)
                y_smooth = gaussian_filter1d(y, sigma=1.3)

                # Draw filled polygon with transparency
                sagittal_poly = QPolygonF()
                for px, py in zip(x_smooth, y_smooth):
                    sagittal_poly.append(QPointF(px, py))

                # Draw filled polygon with transparency
                color = QColor(255, 0, 0, 120)
                painter.setPen(QPen(color, 1.0))
                painter.setBrush(QBrush(color))
                painter.drawPolygon(sagittal_poly)

            painter.end()

        # Display final painted pixmap
        self.canvas_axial.setPixmap(axial_pixmap.scaled(
            self.canvas_axial.width(), self.canvas_axial.height(),
            aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio, mode=Qt.SmoothTransformation
        ))

        self.canvas_coronal.setPixmap(coronal_pixmap.scaled(
            self.canvas_coronal.width(), self.canvas_coronal.height(),
            aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio, mode=Qt.SmoothTransformation
        ))

        self.canvas_sagittal.setPixmap(sagittal_pixmap.scaled(
            self.canvas_sagittal.width(), self.canvas_sagittal.height(),
            aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio, mode=Qt.SmoothTransformation
        ))


# if __name__ == "__main__":
#     import sys
#     from PySide6.QtCore import Qt
#
#     app = QApplication(sys.argv)
#     viewer = DicomViewer('/Users/timglasgow/Downloads/3229478DC190B24900C6F3A1C514AF18/3229478DC190B24900C6F3A1C514AF18.CT.FU')
#     viewer.resize(1000, 800)
#     viewer.show()
#     sys.exit(app.exec())