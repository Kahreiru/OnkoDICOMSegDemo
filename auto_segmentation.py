import os
import logging
import shutil
import tempfile

from multithread import SegmentationWorkerSignals

from redirect_stdout import ConsoleOutputStream, redirect_output_to_gui, setup_logging
from ignore_files_in_dir import ignore_func
from totalsegmentator.python_api import totalsegmentator
from nifti_converter import nifti_to_rtstruct_conversion

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AutoSegmentation:
    """Handles the automatic segmentation process.

    This class manages the workflow for running TotalSegmentator, including
    copying DICOM files, setting up the segmentation task, and converting the
    output to DICOM RTSTRUCT format.
    """

    def __init__(self, controller):
        self.controller = controller
        self.temp_dir = tempfile.mkdtemp()
        self.signals = SegmentationWorkerSignals()

        # Connect worker signals to controller slots
        self.signals.progress_updated.connect(self.controller.update_progress_text)
        self.signals.finished.connect(self.controller.on_segmentation_finished)
        self.signals.error.connect(self.controller.on_segmentation_error)

    def _create_copied_temporary_directory(self, dicom_dir):
        if not dicom_dir:
            self.signals.error.emit('No dicom directory found')
            return

        try:
            shutil.copytree(dicom_dir, self.temp_dir, ignore=ignore_func, dirs_exist_ok=True)
        except Exception as e:
            logger.exception("Failed to copy DICOM files.")
            self.signals.error.emit("Failed to copy DICOM files.")

    def _connect_terminal_stream_to_gui(self):
        output_stream = ConsoleOutputStream()
        output_stream.new_text.connect(self.controller.update_progress_text)
        redirect_output_to_gui(output_stream)
        setup_logging(output_stream)

    def run_segmentation_workflow(self, dicom_dir, task, fast):
        """
        Executes the segmentation workflow.

        This method handles the entire segmentation process, from selecting the DICOM
        directory to running the segmentation task and converting the output to DICOM RTSTRUCT.
        """
        # Clear previous progress text
        self.signals.progress_updated.emit("Starting segmentation workflow...")

        # Copy contents from selected dir to temp dir (excludes rt*.dcm files)
        self._create_copied_temporary_directory(dicom_dir)

        # Connect the terminal stream output to the progress text gui element
        self._connect_terminal_stream_to_gui()

        # Create the output path for Nifti segmentation files
        output_dir = os.path.join(dicom_dir, "segmentations")
        os.makedirs(output_dir, exist_ok=True)
        output_rt = os.path.join(dicom_dir, "rtss.dcm")

        # Call total segmentator API
        try:
            totalsegmentator(
                input=self.temp_dir,
                output=output_dir,
                task=task,
                output_type="nifti",  # output to dicom
                device="cpu",  # Run on cpu
                fastest=fast
            )

            output_rt = os.path.join(dicom_dir, "rtss.dcm")

        except Exception as e:
            self.signals.error.emit("Failed to run segmentation workflow.")
            logger.exception(e)
            shutil.rmtree(output_dir)

        try:
            # Convert the Nifti output to DICOM rtss file
            nifti_to_rtstruct_conversion(output_dir, self.temp_dir, output_rt)

            self.signals.progress_updated.emit("Conversion successful.")
            self.signals.finished.emit()
            shutil.rmtree(self.temp_dir)

        except Exception as e:
            self.signals.error.emit("Failed to convert files to RTSTRUCT format.")
            logger.exception(e)
            shutil.rmtree(output_dir)