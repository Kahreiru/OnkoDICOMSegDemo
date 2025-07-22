import os
from typing import Optional

from PySide6.QtWidgets import QWidget, QApplication, QFileDialog, QPushButton, QVBoxLayout, QLabel, QCheckBox
import pyradise.data as ps_data
import pyradise.fileio as ps_io

class ConvertNiftiToRtss(QWidget):
    def __init__(self, use_3d: bool = True):
        super().__init__()
        self.setWindowTitle("Nifti to RTSS Converter")
        self.layout = QVBoxLayout()

        self.dicom_image_dir_path = QFileDialog.getExistingDirectory(self, "Select DICOM CT Series")
        self.input_dir_path = os.path.join(self.dicom_image_dir_path, 'segmentations')
        self.output_dir_path = self.dicom_image_dir_path
        self.use_3d = use_3d

        # add widgets to layout
        self.label_selected_dir = QLabel("Selected DICOM CT Series")
        self.layout.addWidget(self.label_selected_dir)
        self.label_dir = QLabel(self.dicom_image_dir_path)
        self.layout.addWidget(self.label_dir)
        self.use_3d_checkbox = QCheckBox("Use 3D")
        self.layout.addWidget(self.use_3d_checkbox)
        self.use_3d_checkbox.setChecked(self.use_3d)
        self.run_button = QPushButton("Convert Files")
        self.run_button.clicked.connect(self.convert_subject_to_dicom_rtss)
        self.layout.addWidget(self.run_button)

        self.setLayout(self.layout)

    def convert_subject_to_dicom_rtss(self, use_3d_conversion: bool = True) -> None:

        print(f"Input directory: {self.input_dir_path}")
        print("Files in input dir:")
        for f in os.listdir(self.input_dir_path):
            print(f)

        # Specify a reference modalities
        # This is the modality of the DICOM image series that will be
        # referenced in the DICOM-RTSS.
        reference_modality = 'T1'

        # Create the loader
        loader = ps_io.SubjectLoader()

        # Create the writer and specify the output file name of the
        # DICOM-RTSS files
        writer = ps_io.DicomSeriesSubjectWriter()
        rtss_filename = 'rtss.dcm'

        # (optional)
        # Instantiate a new selection to exclude the original DICOM-RTSS SeriesInfo
        # Note: If this is omitted the original DICOM-RTSS will be copied to the
        # corresponding output directory.
        selection = ps_io.NoRTSSInfoSelector()

        # Create the file crawler for the discrete image files and
        # loop through the subjects

        crawler = ps_io.DatasetFileCrawler(self.input_dir_path,
                                     extension='.nii.gz',
                                     modality_extractor=FileModalityExtractor(),
                                     organ_extractor=FileOrganExtractor(),
                                     annotator_extractor=FileAnnotatorExtractor())

        series_infos = crawler.execute()

        print(f"Found {len(series_infos)} valid files for conversion.")

        if not series_infos:
            print("No valid NIfTI files found. Check naming and extension.")
            return

        for series_info in crawler:

            # Load the subject
            subject = loader.load(series_info)

            # Print the progress
            print(f'Converting subject {subject.get_name()}...')

            # Construct the path to the subject's DICOM images
            dicom_subject_path = os.path.join(self.dicom_image_dir_path, subject.get_name())

            # Construct a DICOM crawler to retrieve the reference
            # DICOM image series info
            dcm_crawler = ps_io.SubjectDicomCrawler(dicom_subject_path,
                                              modality_extractor=FileModalityExtractor())
            dicom_series_info = dcm_crawler.execute()

            # (optional)
            # Keep all SeriesInfo entries that do not describe a DICOM-RTSS for loading
            dicom_series_info = selection.execute(dicom_series_info)

            # (optional)
            # Define the metadata for the DICOM-RTSS
            # Note: For some attributes, the value must follow the value
            # representation of the DICOM standard.
            meta_data = ps_io.RTSSMetaData(patient_size='180',
                                     patient_weight='80',
                                     patient_age='050Y',
                                     series_description='Converted from NIfTI')

            # Convert the segmentations to a DICOM-RTSS with standard smoothing settings.
            # For the conversion we can either use a 2D or a 3D algorithm (see API reference
            # for details).
            # Note: Inappropriate smoothing leads to corrupted structures if their size
            # is too small
            if use_3d_conversion:
                conv_conf = ps_io.RTSSConverter3DConfiguration()
            else:
                conv_conf = ps_io.RTSSConverter2DConfiguration()

            converter = ps_io.SubjectToRTSSConverter(subject,
                                               dicom_series_info,
                                               reference_modality,
                                               conv_conf,
                                               meta_data)
            rtss = converter.convert()

            # Combine the DICOM-RTSS with its output file name
            rtss_combination = ((rtss_filename, rtss),)

            # Write the DICOM-RTSS to a separate subject directory
            # and include the DICOM files crawled before
            # Note: If you want to output just a subset of the
            # original DICOM files you may use additional selectors
            writer.write(rtss_combination, self.output_dir_path,
                         subject.get_name(), dicom_series_info)


class FileModalityExtractor(ps_io.ModalityExtractor):

    def extract_from_dicom(self, path: str) -> Optional[ps_data.Modality]:
        # Extract the necessary attributes from the DICOM file
        tags = (ps_io.Tag((0x0008, 0x0060)),  # Modality
                ps_io.Tag((0x0008, 0x103e)))  # Series Description
        dataset_dict = self._load_dicom_attributes(tags, path)

        # Identify the modality rule-based
        modality = dataset_dict.get('Modality', {}).get('value', None)
        series_desc = dataset_dict.get('Series Description', {}).get('value', '')

        if modality == 'MR':
            if 't1' in series_desc.lower():
                print(f"[Modality] {series_desc} → T1")
                return ps_data.Modality('T1')
            elif 't2' in series_desc.lower():
                print(f"[Modality] {series_desc} → T2")
                return ps_data.Modality('T2')
            else:
                print(f"[Modality] {series_desc} → None")
                return None
        else:
            return None

    def extract_from_path(self, path: str) -> Optional[ps_data.Modality]:
        file_name = os.path.basename(path)

        if 't1' in file_name:
            return ps_data.Modality('T1')
        elif 't2' in file_name:
            return ps_data.Modality('T2')
        else:
            return None

class FileOrganExtractor(ps_io.OrganExtractor):

    def extract(self, path: str) -> Optional[ps_data.Organ]:
        filename = os.path.basename(path)
        if not filename.startswith('seg'):
            print(f"[Organ] {filename} skipped (doesn't start with 'seg')")
            return None
        organ_name = filename.split('_')[-1].split('.')[0]
        print(f"[Organ] {filename} → {organ_name}")
        return ps_data.Organ(organ_name)

    # def extract(self,
    #             path: str
    #             ) -> Optional[ps_data.Organ]:
    #     # Identify the discrete image file's organ rule-based
    #     filename = os.path.basename(path)
    #
    #     # Check if the image contains a seg prefix
    #     # (i.e., it is a segmentation)
    #     if not filename.startswith('seg'):
    #         return None
    #
    #     # Split the filename for extracting the organ name
    #     organ_name = filename.split('_')[-1].split('.')[0]
    #     return ps_data.Organ(organ_name)

class FileAnnotatorExtractor(ps_io.AnnotatorExtractor):

    def extract(self, path: str) -> Optional[ps_data.Annotator]:
        filename = os.path.basename(path)
        if not filename.startswith('seg'):
            print(f"[Annotator] {filename} skipped (doesn't start with 'seg')")
            return None
        parts = filename.split('_')
        if len(parts) >= 3:
            annotator_name = parts[2]
            print(f"[Annotator] {filename} → {annotator_name}")
            return ps_data.Annotator(annotator_name)
        print(f"[Annotator] {filename} → None (not enough parts)")
        return None

    # def extract(self,
    #             path: str
    #             ) -> Optional[ps_data.Annotator]:
    #     # Identify the discrete image file's annotator rule-based
    #     filename = os.path.basename(path)
    #
    #     # Check if the image contains a seg prefix
    #     # (i.e., it is a segmentation)
    #     if not filename.startswith('seg'):
    #         return None
    #
    #     # Split the filename for extracting the annotator name
    #     annotator_name = filename.split('_')[2]
    #     return ps_data.Annotator(annotator_name)

if __name__ == "__main__":
    # import argparse
    #
    # parser = argparse.ArgumentParser(description="Advanced PyRaDiSe NIfTI → DICOM RTSTRUCT converter")
    # parser.add_argument("nifti_dir", help="Folder containing per-subject NIfTI segmentations")
    # parser.add_argument("dicom_dir", help="Folder containing per-subject DICOM series")
    # parser.add_argument("output_dir", help="Directory where RTSTRUCT files will be written")
    # parser.add_argument("--use-3d", action="store_true", help="Use 3D converter instead of 2D")
    # args = parser.parse_args()

    app = QApplication([])
    window = ConvertNiftiToRtss()
    window.show()
    app.exec()
