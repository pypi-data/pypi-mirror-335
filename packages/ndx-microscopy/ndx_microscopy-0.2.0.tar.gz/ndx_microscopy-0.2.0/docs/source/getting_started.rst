.. _getting_started:

***************
Getting Started
***************

Prerequisites
============

Before installing ndx-microscopy, ensure you have:

- Python 3.7 or later
- PyNWB installed
- ndx-ophys-devices extension installed (required for optical components)

Installation
===========

Python Installation
-----------------

The ndx-microscopy extension can be installed via pip:

.. code-block:: bash

   pip install ndx-microscopy

This will automatically install all required dependencies.

Basic Concepts
============

The ndx-microscopy extension provides a standardized way to store and organize microscopy data in the NWB format. Here are the key components:

Device Components
---------------
- **Microscope**: The primary device used for imaging
  - Includes technique specification (e.g., scan mirrors, light sheet, widefield)
- Other optical components (from ndx-ophys-devices):
    - ExcitationSource (lasers, LEDs)
    - OpticalFilter (bandpass, edge filters)
    - Photodetector (PMTs, cameras)
    - DichroicMirror
    - Indicator (fluorescent proteins, dyes)

Light Paths
----------
- **ExcitationLightPath**: Defines how light reaches the sample
- **EmissionLightPath**: Defines how emitted light reaches the detector
- Both can include optical filters, dichroic mirrors, and other metadata

Illumination Patterns
-----------------
- **IlluminationPattern**: Base class for describing how the sample is illuminated
- **LineScan**: For line scanning methods (common in two-photon microscopy)
- **PlaneAcquisition**: For whole plane acquisition (common in light sheet and one-photon)
- **RandomAccessScan**: For targeted, high-speed imaging of specific regions

Imaging Spaces
------------
- **PlanarImagingSpace**: For 2D imaging (single plane)
- **VolumetricImagingSpace**: For 3D imaging (z-stacks)
- Includes physical coordinates, grid spacing, and reference frames
- Requires an illumination pattern to specify how the space was scanned

Data Series
----------
- **PlanarMicroscopySeries**: 2D time series data
- **VolumetricMicroscopySeries**: 3D time series data
- **MultiPlaneMicroscopyContainer**: Multiple imaging planes

Quick Start Example
================

Here's a minimal example showing how to create a basic microscopy dataset:

.. code-block:: python

    from datetime import datetime
    from uuid import uuid4
    from pynwb import NWBFile
    from ndx_microscopy import (
        Microscope, 
        ExcitationLightPath,
        EmissionLightPath,
        PlanarImagingSpace,
        PlanarMicroscopySeries
    )
    from ndx_ophys_devices import Indicator, ExcitationSource, BandOpticalFilter, Photodetector
    import numpy as np

    # Create NWB file
    nwbfile = NWBFile(
        session_description='Example microscopy session',
        identifier=str(uuid4()),
        session_start_time=datetime.now()
    )

    # Set up microscope with technique
    microscope = Microscope(
        name='2p-scope',
        model='Custom two-photon microscope',
        technique='mirror scanning'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    # Create indicator
    indicator = Indicator(
        name='gcamp6f',
        label='GCaMP6f',
        description='Calcium indicator'
    )

    # Create example optical components
    laser = ExcitationSource(
        name = "Laser.",
        manufacturer = "laser manufacturer.",
        model = "laser model",
        illumination_type = "Laser",
        excitation_mode = "two-photon",
        excitation_wavelength_in_nm = 500.0,
    )
    ex_filter = BandOpticalFilter(
        name='ex_filter',
        description='Excitation filter',
        center_wavelength_in_nm = 505.0,
        bandwidth_in_nm = 30.0,  # 505±15nm
        filter_type = "Bandpass",
    )
    # Configure light paths
    excitation = ExcitationLightPath(
        name='2p_excitation',
        description='Two-photon excitation path'
        excitation_source=laser,          # from ndx-ophys-devices
        excitation_filter=ex_filter,      # from ndx-ophys-devices
    )
    nwbfile.add_lab_meta_data(excitation)

    # Create example optical components
    detector = Photodetector(
        name = "Photodetector",
        manufacturer = "Photodetector manufacturer",
        model = "Photodetector model",    
        detector_type = "PMT",
        detected_wavelength_in_nm = 520.0,
    )
    em_filter = BandOpticalFilter(
        name='em_filter',
        description='Emission filter',
        center_wavelength_in_nm = 525.0,
        bandwidth_in_nm = 30.0,  # 525±15nm
        filter_type = "Bandpass",
    )
    emission = EmissionLightPath(
        name='gcamp_emission',
        description='GCaMP6f emission path',
        indicator=indicator,
        photodetector=detector,           # from ndx-ophys-devices
        emission_filter=em_filter,        # from ndx-ophys-devices
    )
    nwbfile.add_lab_meta_data(emission)

    # Define illumination pattern
    line_scan = LineScan(
        name='line_scanning',
        description='Line scanning two-photon microscopy',
        scan_direction='horizontal',
        line_rate_in_Hz=1000.0,
        dwell_time_in_s=1.0e-6
    )

    # Define imaging space with illumination pattern
    planar_imaging_space = PlanarImagingSpace(
        name='cortex_plane',
        description='Layer 2/3 of visual cortex',
        pixel_size_in_um=[1.0, 1.0],
        origin_coordinates=[-1.2, -0.6, -2.0],
        illumination_pattern=line_scan  # Include the illumination pattern
    )

    # Create example imaging data
    data = np.random.rand(100, 512, 512)  # 100 frames, 512x512 pixels

    # Create imaging series
    microscopy_series = PlanarMicroscopySeries(
        name='imaging_data',
        microscope=microscope,
        excitation_light_path=excitation,
        emission_light_path=emission,
        planar_imaging_space=planar_imaging_space,
        data=data,
        unit='a.u.',
        rate=30.0,
        starttin_time=0.0,
    )
    nwbfile.add_acquisition(microscopy_series)

    # Save file
    from pynwb import NWBHDF5IO
    with NWBHDF5IO('microscopy_session.nwb', 'w') as io:
        io.write(nwbfile)

Next Steps
=========

After getting familiar with the basics:

1. Check out the :ref:`examples` section for more detailed examples including:
   - Volumetric imaging
   - Multi-plane imaging
   - ROI segmentation and response series

2. Read the :ref:`user_guide` for best practices and detailed workflows

3. Review the :ref:`api` documentation for complete reference

4. See the :ref:`format` section to understand the underlying data organization
