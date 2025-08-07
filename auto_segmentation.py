import os
import logging
import shutil
import tempfile
from redirect_stdout import ConsoleOutputStream, redirect_output_to_gui, setup_logging

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QThreadPool
from multithread import Worker
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

    def __init__(self, dicom_dir: str, task: str, fast: bool, controller):
        self.task = task
        self.fast = fast
        self.controller = controller
        self.dicom_dir = dicom_dir
        self.temp_dir = tempfile.mkdtemp()
        self.threadpool = QThreadPool()

    def _create_copied_temporary_directory(self):
        if not self.dicom_dir:
            self.controller.update_progress_text("No DICOM directory found.")
            return

        try:
            shutil.copytree(self.dicom_dir, self.temp_dir, ignore=ignore_func, dirs_exist_ok=True)
        except Exception as e:
            self.controller.update_progress_text("Failed to copy DICOM files.")

    def _connect_terminal_stream_to_gui(self):
        output_stream = ConsoleOutputStream()
        output_stream.new_text.connect(self.controller.update_progress_text)
        redirect_output_to_gui(output_stream)
        setup_logging(output_stream)

    def run_segmentation_workflow(self):
        """
        Executes the segmentation workflow.

        This method handles the entire segmentation process, from selecting the DICOM
        directory to running the segmentation task and converting the output to DICOM RTSTRUCT.
        """
        # Clear previous progress text
        self.controller.update_progress_text("Starting segmentation workflow...")

        # Copy contents from selected dir to temp dir (excludes rt*.dcm files)
        self._create_copied_temporary_directory()

        # Connect the terminal stream output to the progress text gui element
        self._connect_terminal_stream_to_gui()

        # Create the output path for Nifti segmentation files
        output_dir = os.path.join(self.dicom_dir, "segmentations")
        os.makedirs(output_dir, exist_ok=True)
        output_rt = os.path.join(self.dicom_dir, "rtss.dcm")

        # Call total segmentator API
        try:
            # Pass the function to execute to worker
            worker = Worker(
                totalsegmentator,
                input=self.temp_dir,
                output=output_dir,
                task=self.task,
                output_type="nifti",  # output to dicom
                device="cpu",  # Run on cpu
                fastest=True
            )

            # Execute the function on worker thread
            self.threadpool.start(worker)

            # Setup and check finished signal from thread
            worker.signals.finished.connect(lambda: self._on_segmentation_finished(output_dir, output_rt))

            output_rt = os.path.join(self.dicom_dir, "rtss.dcm")

        except Exception as e:
            QMessageBox.critical(None, "Segmentation Failed", str(e))
            shutil.rmtree(output_dir)

    def _on_segmentation_finished(self, output_dir, output_rt):
        # Convert the Nifti output to DICOM rtss file
        worker = Worker(nifti_to_rtstruct_conversion, output_dir, self.temp_dir, output_rt)

        # Execute the function on worker thread
        self.threadpool.start(worker)

        # Setup and check finished signal from thread
        worker.signals.finished.connect(lambda: self._on_conversion_finished())

    def _on_conversion_finished(self):
        QMessageBox.information(None, "Success", "Segmentation complete!")
        shutil.rmtree(self.temp_dir)