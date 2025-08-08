# Auto-Segmentation Prototype

## Description
This is a prototype of the functionality which has been proposed to be added
to the program [OnkoDicom](https://onkodicom.com.au/) an open source medical 
research software which has been used in a wide variety of areas including 
areas in Africa, intended to improve the ability for radio-oncologists to develop 
methodologies to help patients.

This specific functionality which is being prototyped is the ability for the user
to be able to create segmentations of areas of the human body which is of interest
to the user to be further focused on without the need for the user to manually draw 
and isolate the specific body part.

## Requirements
- Python version 3.12: [link](https://www.python.org/)
- Poetry: [link](https://python-poetry.org/)

## Dependencies
- PySide6: [link](https://doc.qt.io/qtforpython-6/)
- TotalSegmentator: [link](https://github.com/wasserth/TotalSegmentator)
- pydicom: [link](https://pydicom.github.io/)
- platipy: [link](https://github.com/pyplati/platipy)
- acvl-utils: [link](https://github.com/MIC-DKFZ/acvl_utils)

## Installation
1. Extract the folder from the zip
2. Open Terminal in folder location
3. Input `poetry install` into console
4. Wait for the installation to complete

## Usage
Included in the Zip file is an anonymised dicom file for the purposes of demonstration
1. Open Terminal in the folder location
2. In the console, Input `poetry run main.md`
3. wait for the program to open
4. When the file selection prompt opens select the `Demo` file
5. You will then be directed to the prototype user interface
6. Select the appropriate body part from the drop down menu you would like to segment
7. Select if you want the process to go faster (lower resolution)
   - Quickest results will be obtained by selecting `Task: 'total'` with the option `Fast` selected
8. Click Start
9. Wait for processing to complete as this may take several minutes
10. Once complete, click 'Load Segmentations'
11. Open the Segmentation Folder
12. Select Desired Segmentations to display (for this demo, lung segmentations will show)
13. View segmentations on each axis by dragging the sliders up and down on the image views
14. To disable the segmentations on the views
15. Go to the segmentations section of the window (this may need to be dragged up to make it more visible)
16. Then uncheck the check box corresponding to the appropriate segmentation
