# taken from existing OnkoDicom
import platform
from PathHandler import resource_path

class StyleSheetReader:
    """
    A class to hold the style sheet data to be used in the User Interface classes.
    As this information will need to be used for most of the User Interfaces
    This class is intended to reduce the number of times the style sheet is read
    """
    def __init__(self) -> None:
        """
        Initialising the StyleSheetReader and getting the data from the style sheet
        :rtype: None
        """
        self.style_sheet: str = self._get_layout_data()

    def __call__(self) -> str:
        """
        Returning the style_sheet member if the class is called after initialization
        :rtype: str
        """
        return self.style_sheet

    def _get_platform_stylesheet(self, running_platform: str) -> str:
        """
        Determining which version of the Style sheet to use based on the platform running the program
        :param running_platform:
        :return:
        :rtype: str
        """
        if running_platform == "Darwin":
            path_stylesheet: str = "res/stylesheet.qss"
        else:
            path_stylesheet: str = "res/stylesheet-win-linux.qss"
        return path_stylesheet

    def _get_layout_data(self) -> str:
        """
        Reading the style sheet for the User Interface and loading it into the style_sheet member
        :rtype: str
        """
        path_stylesheet = self._get_platform_stylesheet(platform.system())
        return open(resource_path(path_stylesheet)).read()