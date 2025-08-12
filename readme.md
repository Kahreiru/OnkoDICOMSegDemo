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
- rt_utils: [link](https://github.com/qurit/rt-utils)   
- SimpleITK: [link](https://simpleitk.readthedocs.io/en/master/gettingStarted.html)

## Installation
1. Ensure you have Python installed on your machine (see Requirements)
2. Extract the folder from the zip
3. Open Terminal console and navigate to the folder/project location
e.g. cd C:\path\to\your\project
4. Setup a virtual environment by typing the following into the console:
- Windows: python -m venv venv
- MacOS: python3 -m venv venv
N.B. Windows uses python.exe while Mac uses python3.
5. Activate the virtual environment by typing the following (depending on OS)
into the console:
- MacOS: source venv/bin/activate
- Windows: venv\Scripts\activate
- Windows (PowerShell): .\venv\Scripts\Activate.ps1
6. Install poetry in your virtual environment by entering the following into
console:
pip install poetry
7. Install poetry dependencies by typing the following into console:
poetry install
8. Wait for the installation to complete

## Usage
Included in the Zip file is an anonymised Dicom directory (Demo) for the purposes of
demonstration
1. Open Terminal console in the folder/project location
2. To run the application, enter the following into the console:
- Windows: python main.py
- MacOS: python3 main.py
3. Wait for the program to open – this may take a couple of minutes.
4. When the file selection prompt opens select the “Demo” directory

5. You will then be directed to the prototype user interface
6. Select the appropriate body part from the drop-down menu you would like to
segment
7. Select if you want the process to go faster (lower resolution)
o Quickest results will be obtained by selecting Task: &#39;total&#39; with the
option Fast selected

8. Click Start
9. Wait for processing to complete, as depending on task selection and your
computers specifications, the processing may take quite some time
10. Once complete, click &#39;Load Segmentations&#39;
11. Open the segmentations folder saved in the Demo directory
12. Select desired segmentations to display (for this image set it is advised to
select lung segmentations, as the scans are of the chest area)
13. View segmentations on each axis by dragging the sliders up and down on the
image views
14. To disable a segmentation or multiple segmentations in the view panels,
uncheck the corresponding checkbox in the segmentations panel
15. After closing the application, back in the terminal console type “deactivate” at
the prompt to close the virtual environment.
