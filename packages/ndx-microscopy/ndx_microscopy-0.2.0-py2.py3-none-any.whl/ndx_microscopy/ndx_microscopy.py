from hdmf.utils import docval, popargs
from pynwb import get_class, register_class
from pynwb.core import MultiContainerInterface
from ndx_ophys_devices import ExcitationSource, Photodetector, Indicator
import numpy as np

extension_name = "ndx-microscopy"


# Segmentation2D API functions

Segmentation2D = get_class("Segmentation2D", extension_name)


@docval(
    {
        "name": "pixel_mask",
        "type": "array_data",
        "default": None,
        "doc": "pixel mask for 2D ROIs: [(x1, y1, weight1), (x2, y2, weight2), ...]",
        "shape": (None, 3),
    },
    {
        "name": "image_mask",
        "type": "array_data",
        "default": None,
        "doc": "image with the same size of image where positive values mark this ROI",
        "shape": [[None] * 2],
    },
    {"name": "id", "type": int, "doc": "the ID for the ROI", "default": None},
    allow_extra=True,
)
def add_roi(self, **kwargs):
    """Add a Region Of Interest (ROI) data to this Segmentation2D.

    Parameters
    ----------
    pixel_mask : array_data, optional
        Pixel mask for 2D ROIs in format [(x1, y1, weight1), (x2, y2, weight2), ...].
        Each row contains x,y coordinates and weight value for a pixel.
    image_mask : array_data, optional
        2D image where positive values mark this ROI.
    id : int, optional
        The ID for the ROI. If not provided, will be auto-generated.
    **kwargs : dict
        Additional keyword arguments passed to add_row.

    Raises
    ------
    ValueError
        If neither pixel_mask nor image_mask is provided.
    """
    pixel_mask, image_mask = popargs("pixel_mask", "image_mask", kwargs)
    if image_mask is None and pixel_mask is None:
        raise ValueError("Must provide 'image_mask' and/or 'pixel_mask'")
    rkwargs = dict(kwargs)
    if image_mask is not None:
        rkwargs["image_mask"] = image_mask
        # TODO: should we check that image_masks shape matches the shape of the FOV in the imaging space?
    if pixel_mask is not None:
        rkwargs["pixel_mask"] = pixel_mask
    return super(Segmentation2D, self).add_row(**rkwargs)


@staticmethod
def pixel_to_image(pixel_mask, image_shape=None):
    """Convert a 2D pixel_mask of a ROI into an image_mask.

    Parameters
    ----------
    pixel_mask : array-like
        Array of shape (N, 3) where each row contains (x, y, weight) coordinates.
        The x, y coordinates specify the pixel position and weight specifies the value
        to fill in the output image mask.
    image_shape : tuple, optional
        Shape of the output image (height, width). If not provided, will be determined
        from the maximum x,y coordinates in pixel_mask.

    Returns
    -------
    image_matrix : numpy.ndarray
        2D array where non-zero values indicate the ROI pixels with their corresponding weights.

    Raises
    ------
    ValueError
        If pixel_mask does not have shape (N, 3).
    """
    npmask = np.asarray(pixel_mask)
    if npmask.shape[1] != 3:
        raise ValueError("pixel_mask must have shape (N, 3) where each row is (x, y, weight)")

    x_coords = npmask[:, 0].astype(np.int32)
    y_coords = npmask[:, 1].astype(np.int32)
    weights = npmask[:, -1]

    # Determine dimensions from max coordinates
    if image_shape is None:
        image_shape = (np.max(x_coords) + 1, np.max(y_coords) + 1)
    image_matrix = np.zeros(image_shape)
    image_matrix[x_coords, y_coords] = weights

    return image_matrix


@staticmethod
def image_to_pixel(image_mask):
    """Convert a 2D image_mask of a ROI into a pixel_mask.

    Parameters
    ----------
    image_mask : numpy.ndarray
        2D array where non-zero values indicate ROI pixels.

    Returns
    -------
    list
        List of [x, y, weight] coordinates for each non-zero pixel in the image_mask.
        The weight is the value at that pixel location in the image_mask.

    Raises
    ------
    ValueError
        If image_mask is not 2D.
    """
    if len(image_mask.shape) != 2:
        raise ValueError("image_mask must be 2D (height, width)")
    pixel_mask = []
    it = np.nditer(image_mask, flags=["multi_index"])
    while not it.finished:
        weight = it[0][()]
        if weight > 0:
            x = it.multi_index[0]
            y = it.multi_index[1]
            pixel_mask.append([x, y, weight])
        it.iternext()
    return pixel_mask


Segmentation2D.add_roi = add_roi
Segmentation2D.pixel_to_image = pixel_to_image
Segmentation2D.image_to_pixel = image_to_pixel


@docval(
    {"name": "description", "type": str, "doc": "a brief description of what the region is"},
    {"name": "region", "type": (slice, list, tuple), "doc": "the indices of the table", "default": slice(None)},
    {"name": "name", "type": str, "doc": "the name of the ROITableRegion", "default": "rois"},
)
def create_roi_table_region(self, **kwargs):
    """Create a region (sub-selection) of ROIs.

    Parameters
    ----------
    description : str
        Brief description of what the region represents.
    region : slice, list, tuple, optional
        The indices of the table to include in the region. Default is slice(None) (all ROIs).
    name : str, optional
        Name of the ROITableRegion. Default is 'rois'.

    Returns
    -------
    DynamicTableRegion
        Table region object for the selected ROIs.
    """
    return super(Segmentation2D, self).create_region(**kwargs)


Segmentation2D.create_roi_table_region = create_roi_table_region


# Segmentation3D API functions

Segmentation3D = get_class("Segmentation3D", extension_name)


@docval(
    {
        "name": "voxel_mask",
        "type": "array_data",
        "default": None,
        "doc": "voxel mask for 3D ROIs: [(x1, y1, z1, weight1), (x2, y2, z2, weight2), ...]",
        "shape": (None, 4),
    },
    {
        "name": "image_mask",
        "type": "array_data",
        "default": None,
        "doc": "image with the same size of image where positive values mark this ROI",
        "shape": [[None] * 3],
    },
    {"name": "id", "type": int, "doc": "the ID for the ROI", "default": None},
    allow_extra=True,
)
def add_roi(self, **kwargs):
    """Add a Region Of Interest (ROI) data to this Segmentation3D.

    Parameters
    ----------
    voxel_mask : array_data, optional
        Voxel mask for 3D ROIs in format [(x1, y1, z1, weight1), (x2, y2, z2, weight2), ...].
        Each row contains x,y,z coordinates and weight value for a voxel.
    image_mask : array_data, optional
        3D image where positive values mark this ROI.
    id : int, optional
        The ID for the ROI. If not provided, will be auto-generated.
    **kwargs : dict
        Additional keyword arguments passed to add_row.

    Returns
    -------
    NWBTable.Row
        Row object representing the added ROI.

    Raises
    ------
    ValueError
        If neither voxel_mask nor image_mask is provided.
    """
    voxel_mask, image_mask = popargs("voxel_mask", "image_mask", kwargs)
    if image_mask is None and voxel_mask is None:
        raise ValueError("Must provide 'image_mask' and/or 'voxel_mask'")
    rkwargs = dict(kwargs)
    if image_mask is not None:
        rkwargs["image_mask"] = image_mask
    if voxel_mask is not None:
        rkwargs["voxel_mask"] = voxel_mask
    return super(Segmentation3D, self).add_row(**rkwargs)


@staticmethod
def voxel_to_image(voxel_mask, image_shape=None):
    """Convert a 3D voxel_mask of a ROI into a 3D image_mask.

    Parameters
    ----------
    voxel_mask : array-like
        Array of shape (N, 4) where each row contains (x, y, z, weight) coordinates.
        The x, y, z coordinates specify the voxel position and weight specifies the value
        to fill in the output image mask.
    image_shape : tuple, optional
        Shape of the output image (depth, height, width). If not provided, will be determined
        from the maximum x,y,z coordinates in voxel_mask.

    Returns
    -------
    image_matrix : numpy.ndarray
        3D array where non-zero values indicate the ROI voxels with their corresponding weights.

    Raises
    ------
    ValueError
        If voxel_mask does not have shape (N, 4).
    """
    npmask = np.asarray(voxel_mask)
    if npmask.shape[1] != 4:
        raise ValueError("voxel_mask must have shape (N, 4) where each row is (x, y, z, weight)")

    x_coords = npmask[:, 0].astype(np.int32)
    y_coords = npmask[:, 1].astype(np.int32)
    z_coords = npmask[:, 2].astype(np.int32)
    weights = npmask[:, -1]

    # Determine dimensions from max coordinates
    if image_shape is None:
        image_shape = (np.max(x_coords) + 1, np.max(y_coords) + 1, np.max(z_coords) + 1)
    image_matrix = np.zeros(image_shape)
    image_matrix[x_coords, y_coords, z_coords] = weights

    return image_matrix


@staticmethod
def image_to_voxel(image_mask):
    """Convert a 3D image_mask of a ROI into a voxel_mask.

    Parameters
    ----------
    image_mask : numpy.ndarray
        3D array where non-zero values indicate ROI voxels.

    Returns
    -------
    list
        List of [x, y, z, weight] coordinates for each non-zero voxel in the image_mask.
        The weight is the value at that voxel location in the image_mask.

    Raises
    ------
    ValueError
        If image_mask is not 3D.
    """
    if len(image_mask.shape) != 3:
        raise ValueError("image_mask must be 3D (depth, height, width)")
    voxel_mask = []
    it = np.nditer(image_mask, flags=["multi_index"])
    while not it.finished:
        weight = it[0][()]
        if weight > 0:
            x = it.multi_index[0]
            y = it.multi_index[1]
            z = it.multi_index[2]
            voxel_mask.append([x, y, z, weight])
        it.iternext()
    return voxel_mask


Segmentation3D.add_roi = add_roi
Segmentation3D.voxel_to_image = voxel_to_image
Segmentation3D.image_to_voxel = image_to_voxel


@docval(
    {"name": "description", "type": str, "doc": "a brief description of what the region is"},
    {"name": "region", "type": (slice, list, tuple), "doc": "the indices of the table", "default": slice(None)},
    {"name": "name", "type": str, "doc": "the name of the ROITableRegion", "default": "rois"},
)
def create_roi_table_region(self, **kwargs):
    """Create a region (sub-selection) of ROIs.

    Parameters
    ----------
    description : str
        Brief description of what the region represents.
    region : slice, list, tuple, optional
        The indices of the table to include in the region. Default is slice(None) (all ROIs).
    name : str, optional
        Name of the ROITableRegion. Default is 'rois'.

    Returns
    -------
    DynamicTableRegion
        Table region object for the selected ROIs.
    """
    return super(Segmentation3D, self).create_region(**kwargs)


Segmentation3D.create_roi_table_region = create_roi_table_region


# SegmentationContainer API functions
ImagingSpace = get_class("ImagingSpace", extension_name)
Segmentation = get_class("Segmentation", extension_name)


@register_class("SegmentationContainer", extension_name)
class SegmentationContainer(MultiContainerInterface):
    """Container for managing multiple segmentation objects.

    This class provides an interface for storing and managing multiple segmentation objects,
    each associated with a specific imaging space.
    """

    __clsconf__ = {
        "attr": "segmentations",
        "type": Segmentation,
        "add": "add_segmentation",
        "get": "get_segmentation",
        "create": "create_segmentation",
    }

    @docval(
        {"name": "imaging_space", "type": ImagingSpace, "doc": "the ImagingSpace this ROI applies to"},
        {
            "name": "description",
            "type": str,
            "doc": "Description of image space, depth, etc.",
            "default": None,
        },
        {"name": "name", "type": str, "doc": "name of Segmentation.", "default": None},
    )
    def add_segmentation(self, **kwargs):
        """Add a segmentation to this container.

        Parameters
        ----------
        imaging_space : ImagingSpace
            The imaging space this segmentation applies to.
        description : str, optional
            Description of the image space, depth, etc. If not provided,
            uses the description from imaging_space.
        name : str, optional
            Name of the segmentation.

        Returns
        -------
        Segmentation
            The created segmentation object.
        """
        kwargs.setdefault("description", kwargs["imaging_space"].description)
        return self.create_segmentation(**kwargs)


ExcitationLightPath = get_class("ExcitationLightPath", extension_name)


@docval(
    {"name": "excitation_source", "type": ExcitationSource, "doc": "The excitation source", "default": None},
    allow_extra=True,
)
def get_excitation_wavelength(self, **kwargs):
    """Get the excitation wavelength from the excitation source."""
    excitation_source = popargs("excitation_source", kwargs)
    return excitation_source.excitation_wavelength_in_nm


ExcitationLightPath.get_excitation_wavelength = get_excitation_wavelength


EmissionLightPath = get_class("EmissionLightPath", extension_name)


@docval(
    {"name": "photodetector", "type": Photodetector, "doc": "The photodetector", "default": None},
    allow_extra=True,
)
def get_emission_wavelength(self, **kwargs):
    """Get the emission wavelength from the photodetector."""
    photodetector = popargs("photodetector", kwargs)
    return photodetector.detected_wavelength_in_nm


EmissionLightPath.get_emission_wavelength = get_emission_wavelength


@docval(
    {"name": "indicator", "type": Indicator, "doc": "The indicator", "default": None},
    allow_extra=True,
)
def get_indicator_label(self, **kwargs):
    """Get the label of the indicator."""
    indicator = popargs("indicator", kwargs)
    return indicator.label


EmissionLightPath.get_indicator_label = get_indicator_label
