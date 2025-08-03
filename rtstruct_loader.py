import numpy as np
from rt_utils import RTStructBuilder

def load_rtstruct_masks(rtstruct_path: str, dicom_series_dir: str) -> dict:
    """
    Load binary masks from a DICOM RTSTRUCT and its corresponding CT series.

    :param rtstruct_path: path to DICOM RTSTRUCT file
    :param dicom_series_dir: path to folder containing the CT series
    :return: dict of {roi_name: np.ndarray (3D binary mask)}
    """
    # Load RTStruct object
    rtstruct = RTStructBuilder.create_from(
        dicom_series_path=dicom_series_dir,
        rt_struct_path=rtstruct_path
    )

    roi_names = rtstruct.get_roi_names()
    print("ROI names:", roi_names)
    masks = {}

    for name in roi_names:
        mask_3d = rtstruct.get_roi_mask_by_name(name)  # shape: (z, y, x)
        masks[name] = mask_3d.astype(np.uint8)

    return masks
