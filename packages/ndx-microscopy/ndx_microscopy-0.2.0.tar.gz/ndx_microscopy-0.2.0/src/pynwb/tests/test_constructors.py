"""Test in-memory Python API constructors for the ndx-microscopy extension."""

import pytest

from ndx_microscopy.testing import (
    mock_EmissionLightPath,
    mock_ExcitationLightPath,
    mock_Microscope,
    mock_Segmentation,
    mock_Segmentation2D,
    mock_Segmentation3D,
    mock_SegmentationContainer,
    mock_PlanarImagingSpace,
    mock_PlanarMicroscopySeries,
    mock_MultiPlaneMicroscopyContainer,
    mock_VolumetricImagingSpace,
    mock_VolumetricMicroscopySeries,
    mock_MicroscopyResponseSeries,
    mock_MicroscopyResponseSeriesContainer,
    mock_IlluminationPattern,
    mock_LineScan,
    mock_PlaneAcquisition,
    mock_RandomAccessScan,
)
from ndx_microscopy import (
    Segmentation,
    Segmentation2D,
    Segmentation3D,
    PlanarImagingSpace,
    VolumetricImagingSpace,
    IlluminationPattern,
    LineScan,
    PlaneAcquisition,
    RandomAccessScan,
)


def test_constructor_microscope():
    microscope = mock_Microscope()
    assert microscope.description == "A mock instance of a Microscope type to be used for rapid testing."


def test_constructor_excitation_light_path():
    excitation_light_path = mock_ExcitationLightPath()
    assert (
        excitation_light_path.description
        == "A mock instance of a ExcitationLightPath type to be used for rapid testing."
    )


def test_constructor_emission_light_path():
    emission_light_path = mock_EmissionLightPath()
    assert (
        emission_light_path.description == "A mock instance of a EmissionLightPath type to be used for rapid testing."
    )


def test_constructor_illumination_pattern():
    """Test constructor for base IlluminationPattern class."""
    illumination_pattern = mock_IlluminationPattern()
    assert (
        illumination_pattern.description
        == "A mock instance of an IlluminationPattern type to be used for rapid testing."
    )
    assert isinstance(illumination_pattern, IlluminationPattern)


def test_constructor_line_scan():
    """Test constructor for LineScan class."""
    line_scan = mock_LineScan()
    assert line_scan.description == "A mock instance of a LineScan type to be used for rapid testing."
    assert line_scan.scan_direction == "horizontal"
    assert line_scan.line_rate_in_Hz == 1000.0
    assert line_scan.dwell_time_in_s == 1e-6
    assert isinstance(line_scan, LineScan)
    assert isinstance(line_scan, IlluminationPattern)


def test_constructor_plane_acquisition():
    """Test constructor for PlaneAcquisition class."""
    plane_acquisition = mock_PlaneAcquisition()
    assert plane_acquisition.description == "A mock instance of a PlaneAcquisition type to be used for rapid testing."
    assert plane_acquisition.plane_thickness_in_um == 5.0
    assert plane_acquisition.illumination_angle_in_degrees == 45.0
    assert plane_acquisition.plane_rate_in_Hz == 100.0
    assert isinstance(plane_acquisition, PlaneAcquisition)
    assert isinstance(plane_acquisition, IlluminationPattern)  # Test inheritance


def test_constructor_random_access_scan():
    """Test constructor for RandomAccessScan class."""
    random_access_scan = mock_RandomAccessScan()
    assert random_access_scan.description == "A mock instance of a RandomAccessScan type to be used for rapid testing."
    assert random_access_scan.max_scan_points == 1000
    assert random_access_scan.dwell_time_in_s == 1.0e-6
    assert random_access_scan.scanning_pattern == "spiral"
    assert isinstance(random_access_scan, RandomAccessScan)
    assert isinstance(random_access_scan, IlluminationPattern)  # Test inheritance


def test_constructor_planar_imaging_space():
    planar_imaging_space = mock_PlanarImagingSpace()
    assert (
        planar_imaging_space.description == "A mock instance of a PlanarImagingSpace type to be used for rapid testing."
    )
    assert isinstance(planar_imaging_space, PlanarImagingSpace)


def test_constructor_volumetric_imaging_space():
    volumetric_imaging_space = mock_VolumetricImagingSpace()
    assert (
        volumetric_imaging_space.description
        == "A mock instance of a VolumetricImagingSpace type to be used for rapid testing."
    )
    assert isinstance(volumetric_imaging_space, VolumetricImagingSpace)


def test_constructor_segmentation():
    """Test constructor for base Segmentation class."""
    segmentation = mock_Segmentation()
    assert segmentation.description == "A mock instance of a Segmentation type to be used for rapid testing."
    assert len(segmentation.summary_images) == 2
    assert "mean" in segmentation.summary_images
    assert "max" in segmentation.summary_images
    assert isinstance(segmentation, Segmentation)


def test_constructor_segmentation_2D():
    """Test constructor for Segmentation2D class."""
    planar_imaging_space = mock_PlanarImagingSpace()
    segmentation = mock_Segmentation2D(planar_imaging_space=planar_imaging_space)
    assert segmentation.description == "A mock instance of a Segmentation2D type to be used for rapid testing."
    assert len(segmentation.id) == 5  # Default number_of_rois
    assert "image_mask" in segmentation.colnames
    assert isinstance(segmentation.planar_imaging_space, PlanarImagingSpace)
    assert isinstance(segmentation, Segmentation2D)
    assert isinstance(segmentation, Segmentation)  # Test inheritance


def test_constructor_volumetric_segmentation():
    """Test constructor for Segmentation3D class."""
    volumetric_imaging_space = mock_VolumetricImagingSpace()
    segmentation = mock_Segmentation3D(volumetric_imaging_space=volumetric_imaging_space)
    assert segmentation.description == "A mock instance of a Segmentation3D type to be used for rapid testing."
    assert len(segmentation.id) == 5  # Default number_of_rois
    assert "image_mask" in segmentation.colnames
    assert isinstance(segmentation.volumetric_imaging_space, VolumetricImagingSpace)
    assert isinstance(segmentation, Segmentation3D)
    assert isinstance(segmentation, Segmentation)  # Test inheritance


def test_constructor_segmentation_container():
    """Test constructor for SegmentationContainer class."""
    container = mock_SegmentationContainer()
    assert len(container.segmentations) == 2  # Default includes both planar and volumetric
    segmentation_names = [seg_name for seg_name in container.segmentations]
    assert isinstance(container.segmentations[segmentation_names[0]], Segmentation2D)
    assert isinstance(container.segmentations[segmentation_names[1]], Segmentation3D)


def test_constructor_planar_microscopy_series():
    microscope = mock_Microscope()
    excitation_light_path = mock_ExcitationLightPath()
    planar_imaging_space = mock_PlanarImagingSpace()
    emission_light_path = mock_EmissionLightPath()

    planar_microscopy_series = mock_PlanarMicroscopySeries(
        microscope=microscope,
        excitation_light_path=excitation_light_path,
        planar_imaging_space=planar_imaging_space,
        emission_light_path=emission_light_path,
    )
    assert (
        planar_microscopy_series.description
        == "A mock instance of a PlanarMicroscopySeries type to be used for rapid testing."
    )


def test_constructor_multi_plane_microscopy_container():

    microscope = mock_Microscope()
    excitation_light_path = mock_ExcitationLightPath()
    planar_imaging_space = mock_PlanarImagingSpace()
    emission_light_path = mock_EmissionLightPath()
    planar_microscopy_series = mock_PlanarMicroscopySeries(
        microscope=microscope,
        excitation_light_path=excitation_light_path,
        planar_imaging_space=planar_imaging_space,
        emission_light_path=emission_light_path,
    )

    multi_plane_microscopy_container = mock_MultiPlaneMicroscopyContainer(
        planar_microscopy_series=[planar_microscopy_series]
    )
    assert multi_plane_microscopy_container.name == "MultiPlaneMicroscopyContainer"


def test_constructor_volumetric_microscopy_series():
    microscope = mock_Microscope()
    excitation_light_path = mock_ExcitationLightPath()
    volumetric_imaging_space = mock_VolumetricImagingSpace()
    emission_light_path = mock_EmissionLightPath()

    volumetric_microscopy_series = mock_VolumetricMicroscopySeries(
        microscope=microscope,
        excitation_light_path=excitation_light_path,
        volumetric_imaging_space=volumetric_imaging_space,
        emission_light_path=emission_light_path,
    )
    assert (
        volumetric_microscopy_series.description
        == "A mock instance of a VolumetricMicroscopySeries type to be used for rapid testing."
    )


def test_constructor_microscopy_response_series():
    number_of_rois = 10
    planar_imaging_space = mock_PlanarImagingSpace()
    segmentation = mock_Segmentation2D(planar_imaging_space=planar_imaging_space, number_of_rois=number_of_rois)

    rois = segmentation.create_roi_table_region(
        description="test region",
        region=[x for x in range(number_of_rois)],
    )

    microscopy_response_series = mock_MicroscopyResponseSeries(rois=rois)
    assert (
        microscopy_response_series.description
        == "A mock instance of a MicroscopyResponseSeries type to be used for rapid testing."
    )


def test_constructor_microscopy_response_series_container():
    number_of_rois = 10
    planar_imaging_space = mock_PlanarImagingSpace()
    segmentation = mock_Segmentation2D(planar_imaging_space=planar_imaging_space, number_of_rois=number_of_rois)

    rois = segmentation.create_roi_table_region(
        description="test region",
        region=[x for x in range(number_of_rois)],
    )

    microscopy_response_series = mock_MicroscopyResponseSeries(rois=rois)

    microscopy_response_series_container = mock_MicroscopyResponseSeriesContainer(
        microscopy_response_series=[microscopy_response_series]
    )
    assert microscopy_response_series_container.name == "MicroscopyResponseSeriesContainer"


if __name__ == "__main__":
    pytest.main([__file__])
