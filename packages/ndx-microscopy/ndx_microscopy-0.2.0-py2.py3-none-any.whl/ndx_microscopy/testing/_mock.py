import warnings
from typing import List, Optional, Tuple

import numpy as np
import pynwb.base
from ndx_ophys_devices import ExcitationSource, Indicator, OpticalFilter, Photodetector, DichroicMirror
from ndx_ophys_devices.testing import (
    mock_ExcitationSource,
    mock_Indicator,
    mock_OpticalFilter,
    mock_Photodetector,
    mock_DichroicMirror,
)
from pynwb.testing.mock.utils import name_generator

import ndx_microscopy


def mock_Microscope(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a Microscope type to be used for rapid testing.",
    manufacturer: str = "A fake manufacturer of the mock microscope.",
    model: str = "A fake model of the mock microscope.",
    technique: str = "A fake technique used by the mock microscope.",
) -> ndx_microscopy.Microscope:
    microscope = ndx_microscopy.Microscope(
        name=name or name_generator("Microscope"),
        description=description,
        manufacturer=manufacturer,
        model=model,
        technique=technique,
    )
    return microscope


def mock_ExcitationLightPath(
    *,
    name: Optional[str] = None,
    description: str = None,
    excitation_source: ExcitationSource = None,
    excitation_filter: OpticalFilter = None,
    dichroic_mirror: DichroicMirror = None,
) -> ndx_microscopy.ExcitationLightPath:
    excitation_light_path = ndx_microscopy.ExcitationLightPath(
        name=name or name_generator("ExcitationLightPath"),
        description=description or "A mock instance of a ExcitationLightPath type to be used for rapid testing.",
        excitation_source=excitation_source or mock_ExcitationSource(),
        excitation_filter=excitation_filter or mock_OpticalFilter(),
        dichroic_mirror=dichroic_mirror or mock_DichroicMirror(),
    )
    return excitation_light_path


def mock_EmissionLightPath(
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    indicator: Indicator = None,
    photodetector: Photodetector = None,
    emission_filter: OpticalFilter = None,
    dichroic_mirror: DichroicMirror = None,
) -> ndx_microscopy.EmissionLightPath:
    emission_light_path = ndx_microscopy.EmissionLightPath(
        name=name or name_generator("EmissionLightPath"),
        description=description or "A mock instance of a EmissionLightPath type to be used for rapid testing.",
        indicator=indicator or mock_Indicator(),
        photodetector=photodetector or mock_Photodetector(),
        emission_filter=emission_filter or mock_OpticalFilter(),
        dichroic_mirror=dichroic_mirror or mock_DichroicMirror(),
    )
    return emission_light_path


def mock_IlluminationPattern(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of an IlluminationPattern type to be used for rapid testing.",
) -> ndx_microscopy.IlluminationPattern:
    """Base class for describing microscopy imaging modalities."""
    illumination_pattern = ndx_microscopy.IlluminationPattern(
        name=name or name_generator("IlluminationPattern"),
        description=description,
    )
    return illumination_pattern


def mock_LineScan(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a LineScan type to be used for rapid testing.",
    scan_direction: Optional[str] = "horizontal",
    line_rate_in_Hz: Optional[float] = 1000.0,
    dwell_time_in_s: Optional[float] = 1.0e-6,
) -> ndx_microscopy.LineScan:
    """Line scanning method used in microscopy, particularly common in two-photon imaging."""
    line_scan = ndx_microscopy.LineScan(
        name=name or name_generator("LineScan"),
        description=description,
        scan_direction=scan_direction,
        line_rate_in_Hz=line_rate_in_Hz,
        dwell_time_in_s=dwell_time_in_s,
    )
    return line_scan


def mock_PlaneAcquisition(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a PlaneAcquisition type to be used for rapid testing.",
    plane_thickness_in_um: Optional[float] = 5.0,
    illumination_angle_in_degrees: Optional[float] = 45.0,
    plane_rate_in_Hz: Optional[float] = 100.0,
) -> ndx_microscopy.PlaneAcquisition:
    """Light sheet method."""
    plane_acquisition = ndx_microscopy.PlaneAcquisition(
        name=name or name_generator("PlaneAcquisition"),
        description=description,
        plane_thickness_in_um=plane_thickness_in_um,
        illumination_angle_in_degrees=illumination_angle_in_degrees,
        plane_rate_in_Hz=plane_rate_in_Hz,
    )
    return plane_acquisition


def mock_RandomAccessScan(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a RandomAccessScan type to be used for rapid testing.",
    max_scan_points: Optional[int] = 1000,
    dwell_time_in_s: Optional[float] = 1.0e-6,
    scanning_pattern: Optional[str] = "spiral",
) -> ndx_microscopy.RandomAccessScan:
    """Random access scanning method for targeted, high-speed imaging of specific regions."""
    random_access_scan = ndx_microscopy.RandomAccessScan(
        name=name or name_generator("RandomAccessScan"),
        description=description,
        max_scan_points=max_scan_points,
        dwell_time_in_s=dwell_time_in_s,
        scanning_pattern=scanning_pattern,
    )
    return random_access_scan


def mock_PlanarImagingSpace(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a PlanarImagingSpace type to be used for rapid testing.",
    origin_coordinates: Tuple[float, float, float] = (-1.2, -0.6, -2),
    pixel_size_in_um: Tuple[float, float, float] = (20, 20),
    location: str = "The location targeted by the mock imaging space.",
    reference_frame: str = "The reference frame of the mock planar imaging space.",
    orientation: str = "The orientation of the mock planar imaging space.",
    illumination_pattern: ndx_microscopy.IlluminationPattern = None,
) -> ndx_microscopy.PlanarImagingSpace:
    planar_imaging_space = ndx_microscopy.PlanarImagingSpace(
        name=name or name_generator("PlanarImagingSpace"),
        description=description,
        origin_coordinates=origin_coordinates,
        pixel_size_in_um=pixel_size_in_um,
        location=location,
        reference_frame=reference_frame,
        orientation=orientation,
        illumination_pattern=illumination_pattern or mock_IlluminationPattern(),
    )
    return planar_imaging_space


def mock_VolumetricImagingSpace(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a VolumetricImagingSpace type to be used for rapid testing.",
    origin_coordinates: Tuple[float, float, float] = (-1.2, -0.6, -2),
    voxel_size_in_um: Tuple[float, float, float] = (20, 20, 50),
    location: str = "The location targeted by the mock imaging space.",
    reference_frame: str = "The reference frame of the mock volumetric imaging space.",
    orientation: str = "The orientation of the mock planar imaging space.",
    illumination_pattern: ndx_microscopy.IlluminationPattern = None,
) -> ndx_microscopy.VolumetricImagingSpace:
    volumetric_imaging_space = ndx_microscopy.VolumetricImagingSpace(
        name=name or name_generator("VolumetricImagingSpace"),
        description=description,
        origin_coordinates=origin_coordinates,
        voxel_size_in_um=voxel_size_in_um,
        location=location,
        reference_frame=reference_frame,
        orientation=orientation,
        illumination_pattern=illumination_pattern or mock_IlluminationPattern(),
    )
    return volumetric_imaging_space


def mock_SummaryImage(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a SummaryImage type to be used for rapid testing.",
    image_shape: Tuple[int, int] = (10, 10),
    data: Optional[np.ndarray] = None,
) -> ndx_microscopy.SummaryImage:
    name = name or name_generator("SummaryImage")
    data = data if data is not None else np.ones(image_shape)
    summary_image = ndx_microscopy.SummaryImage(name=name, description=description, data=data)
    return summary_image


def mock_Segmentation(
    *,
    name: Optional[str] = None,
    description: str = "A mock instance of a Segmentation type to be used for rapid testing.",
    summary_images: Optional[List[ndx_microscopy.SummaryImage]] = None,
) -> ndx_microscopy.Segmentation:
    """Base abstract class with summary images."""
    name = name or name_generator("Segmentation")

    # Create default summary images if none provided
    if summary_images is None:
        mean_image = mock_SummaryImage(name="mean", description="Mean intensity projection")
        max_image = mock_SummaryImage(name="max", description="Maximum intensity projection")
        summary_images = [mean_image, max_image]

    segmentation = ndx_microscopy.Segmentation(name=name, description=description, summary_images=summary_images)

    return segmentation


def mock_Segmentation2D(
    *,
    planar_imaging_space: ndx_microscopy.PlanarImagingSpace,
    name: Optional[str] = None,
    description: str = "A mock instance of a Segmentation2D type to be used for rapid testing.",
    number_of_rois: int = 5,
    image_shape: Tuple[int, int] = (10, 10),
    summary_images: Optional[List[ndx_microscopy.SummaryImage]] = None,
) -> ndx_microscopy.Segmentation2D:
    """2D segmentation with image_mask/pixel_mask."""
    name = name or name_generator("Segmentation2D")

    # Create default summary images if none provided
    if summary_images is None:
        mean_image = mock_SummaryImage(name="mean", description="Mean intensity projection", image_shape=image_shape)
        max_image = mock_SummaryImage(name="max", description="Maximum intensity projection", image_shape=image_shape)
        summary_images = [mean_image, max_image]

    segmentation_2D = ndx_microscopy.Segmentation2D(
        name=name,
        description=description,
        planar_imaging_space=planar_imaging_space,
        id=list(range(number_of_rois)),
        summary_images=summary_images,
    )

    # Add image masks
    image_masks = list()
    for _ in range(number_of_rois):
        image_masks.append(np.zeros(image_shape, dtype=bool))

    segmentation_2D.add_column(name="image_mask", description="ROI image masks", data=image_masks)

    return segmentation_2D


def mock_Segmentation3D(
    *,
    volumetric_imaging_space: ndx_microscopy.VolumetricImagingSpace,
    name: Optional[str] = None,
    description: str = "A mock instance of a Segmentation3D type to be used for rapid testing.",
    number_of_rois: int = 5,
    image_shape: Tuple[int, int, int] = (10, 10, 10),
    summary_images: Optional[List[ndx_microscopy.SummaryImage]] = None,
) -> ndx_microscopy.Segmentation3D:
    """3D segmentation with image_mask/voxel_mask."""
    name = name or name_generator("Segmentation3D")

    # Create default summary images if none provided
    if summary_images is None:
        mean_image = mock_SummaryImage(name="mean", description="Mean intensity projection", image_shape=image_shape)
        max_image = mock_SummaryImage(name="max", description="Maximum intensity projection", image_shape=image_shape)
        summary_images = [mean_image, max_image]

    volumetric_segmentation = ndx_microscopy.Segmentation3D(
        name=name,
        description=description,
        volumetric_imaging_space=volumetric_imaging_space,
        id=list(range(number_of_rois)),
        summary_images=summary_images,
    )

    # Add image masks
    image_masks = list()
    for _ in range(number_of_rois):
        image_masks.append(np.zeros(image_shape, dtype=bool))

    volumetric_segmentation.add_column(name="image_mask", description="ROI image masks", data=image_masks)

    return volumetric_segmentation


def mock_SegmentationContainer(
    *,
    name: Optional[str] = None,
    segmentations: Optional[List[ndx_microscopy.Segmentation]] = None,
) -> ndx_microscopy.SegmentationContainer:
    """Container for multiple segmentations."""
    name = name or name_generator("SegmentationContainer")

    # Create default segmentations if none provided
    if segmentations is None:
        planar_imaging_space = mock_PlanarImagingSpace()
        volumetric_imaging_space = mock_VolumetricImagingSpace()
        segmentations = [
            mock_Segmentation2D(planar_imaging_space=planar_imaging_space),
            mock_Segmentation3D(volumetric_imaging_space=volumetric_imaging_space),
        ]

    container = ndx_microscopy.SegmentationContainer(name=name, segmentations=segmentations)

    return container


def mock_PlanarMicroscopySeries(
    *,
    microscope: ndx_microscopy.Microscope,
    excitation_light_path: ndx_microscopy.ExcitationLightPath,
    planar_imaging_space: ndx_microscopy.PlanarImagingSpace,
    emission_light_path: ndx_microscopy.EmissionLightPath,
    name: Optional[str] = None,
    description: str = "A mock instance of a PlanarMicroscopySeries type to be used for rapid testing.",
    data: Optional[np.ndarray] = None,
    unit: str = "a.u.",
    conversion: float = 1.0,
    offset: float = 0.0,
    starting_time: Optional[float] = None,
    rate: Optional[float] = None,
    timestamps: Optional[np.ndarray] = None,
) -> ndx_microscopy.PlanarMicroscopySeries:
    series_name = name or name_generator("PlanarMicroscopySeries")
    series_data = data if data is not None else np.ones(shape=(15, 5, 5))

    if timestamps is None:
        series_starting_time = starting_time or 0.0
        series_rate = rate or 10.0
        series_timestamps = None
    else:
        if starting_time is not None or rate is not None:
            warnings.warn(
                message=(
                    "Timestamps were provided in addition to either rate or starting_time! "
                    "Please specify only timestamps, or both starting_time and rate. Timestamps will take precedence."
                ),
                stacklevel=2,
            )

        series_starting_time = None
        series_rate = None
        series_timestamps = timestamps

    planar_microscopy_series = ndx_microscopy.PlanarMicroscopySeries(
        name=series_name,
        description=description,
        microscope=microscope,
        excitation_light_path=excitation_light_path,
        planar_imaging_space=planar_imaging_space,
        emission_light_path=emission_light_path,
        data=series_data,
        unit=unit,
        conversion=conversion,
        offset=offset,
        starting_time=series_starting_time,
        rate=series_rate,
        timestamps=series_timestamps,
    )
    return planar_microscopy_series


def mock_MultiPlaneMicroscopyContainer(
    *,
    planar_microscopy_series: List[ndx_microscopy.PlanarMicroscopySeries],
    name: Optional[str] = None,
) -> ndx_microscopy.MultiPlaneMicroscopyContainer:
    container_name = name or name_generator("MultiPlaneMicroscopyContainer")

    multi_plane_microscopy_container = ndx_microscopy.MultiPlaneMicroscopyContainer(
        name=container_name, planar_microscopy_series=planar_microscopy_series
    )

    return multi_plane_microscopy_container


def mock_VolumetricMicroscopySeries(
    *,
    microscope: ndx_microscopy.Microscope,
    excitation_light_path: ndx_microscopy.ExcitationLightPath,
    volumetric_imaging_space: ndx_microscopy.VolumetricImagingSpace,
    emission_light_path: ndx_microscopy.EmissionLightPath,
    name: Optional[str] = None,
    description: str = "A mock instance of a VolumetricMicroscopySeries type to be used for rapid testing.",
    data: Optional[np.ndarray] = None,
    unit: str = "a.u.",
    conversion: float = 1.0,
    offset: float = 0.0,
    starting_time: Optional[float] = None,
    rate: Optional[float] = None,
    timestamps: Optional[np.ndarray] = None,
) -> ndx_microscopy.VolumetricMicroscopySeries:
    series_name = name or name_generator("VolumetricMicroscopySeries")
    series_data = data if data is not None else np.ones(shape=(5, 5, 5, 3))

    if timestamps is None:
        series_starting_time = starting_time or 0.0
        series_rate = rate or 10.0
        series_timestamps = None
    else:
        if starting_time is not None or rate is not None:
            warnings.warn(
                message=(
                    "Timestamps were provided in addition to either rate or starting_time! "
                    "Please specify only timestamps, or both starting_time and rate. Timestamps will take precedence."
                ),
                stacklevel=2,
            )

        series_starting_time = None
        series_rate = None
        series_timestamps = timestamps

    volumetric_microscopy_series = ndx_microscopy.VolumetricMicroscopySeries(
        name=series_name,
        description=description,
        microscope=microscope,
        excitation_light_path=excitation_light_path,
        volumetric_imaging_space=volumetric_imaging_space,
        emission_light_path=emission_light_path,
        data=series_data,
        unit=unit,
        conversion=conversion,
        offset=offset,
        starting_time=series_starting_time,
        rate=series_rate,
        timestamps=series_timestamps,
    )
    return volumetric_microscopy_series


def mock_MicroscopyResponseSeries(
    *,
    rois: pynwb.core.DynamicTableRegion,
    name: Optional[str] = None,
    description: str = "A mock instance of a MicroscopyResponseSeries type to be used for rapid testing.",
    data: Optional[np.ndarray] = None,
    unit: str = "a.u.",
    conversion: float = 1.0,
    offset: float = 0.0,
    starting_time: Optional[float] = None,
    rate: Optional[float] = None,
    timestamps: Optional[np.ndarray] = None,
) -> ndx_microscopy.MicroscopyResponseSeries:
    series_name = name or name_generator("MicroscopyResponseSeries")

    number_of_frames = 100
    number_of_rois = len(rois.data)
    series_data = data if data is not None else np.ones(shape=(number_of_frames, number_of_rois))

    if timestamps is None:
        series_starting_time = starting_time or 0.0
        series_rate = rate or 10.0
        series_timestamps = None
    else:
        if starting_time is not None or rate is not None:
            warnings.warn(
                message=(
                    "Timestamps were provided in addition to either rate or starting_time! "
                    "Please specify only timestamps, or both starting_time and rate. Timestamps will take precedence."
                ),
                stacklevel=2,
            )

        series_starting_time = None
        series_rate = None
        series_timestamps = timestamps

    microscopy_response_series = ndx_microscopy.MicroscopyResponseSeries(
        name=series_name,
        description=description,
        rois=rois,
        data=series_data,
        unit=unit,
        conversion=conversion,
        offset=offset,
        starting_time=series_starting_time,
        rate=series_rate,
        timestamps=series_timestamps,
    )

    return microscopy_response_series


def mock_MicroscopyResponseSeriesContainer(
    *,
    microscopy_response_series: List[ndx_microscopy.MicroscopyResponseSeries],
    name: Optional[str] = None,
) -> ndx_microscopy.MicroscopyResponseSeriesContainer:
    container_name = name or name_generator("MicroscopyResponseSeriesContainer")

    microscopy_response_series_container = ndx_microscopy.MicroscopyResponseSeriesContainer(
        name=container_name, microscopy_response_series=microscopy_response_series
    )

    return microscopy_response_series_container
