.. _user_guide:

**********
User Guide
**********

This guide provides detailed information about using the ndx-microscopy extension effectively.

Core Concepts
-----------

Device Components
^^^^^^^^^^^^^^^

The primary device component is the Microscope class:

.. code-block:: python

    microscope = Microscope(
        name='2p-scope',
        description='Custom two-photon microscope'
        manufacturer='Company X'
        model='Model Y'
    )
    nwbfile.add_device(microscope)

Other optical components (filters, sources, detectors) are provided by the ndx-ophys-devices extension.

Light Path Configuration
^^^^^^^^^^^^^^^^^^^^^

Light paths define how light travels through the microscope:

1. **ExcitationLightPath**: Defines illumination pathway

   .. code-block:: python

       excitation = ExcitationLightPath(
           name='2p_excitation',
           description='Two-photon excitation path',
           excitation_source=laser,          # from ndx-ophys-devices
           excitation_filter=ex_filter,      # from ndx-ophys-devices
           dichroic_mirror=dichroic         # from ndx-ophys-devices
       )

2. **EmissionLightPath**: Defines collection pathway

   .. code-block:: python

       emission = EmissionLightPath(
           name='gcamp_emission',
           description='GCaMP6f emission path',
           indicator=indicator,              # from ndx-ophys-devices
           photodetector=detector,           # from ndx-ophys-devices
           emission_filter=em_filter,        # from ndx-ophys-devices
           dichroic_mirror=dichroic         # from ndx-ophys-devices
       )

Illumination Pattern Configuration
^^^^^^^^^^^^^^^^^^^^^

Illumination patterns define how the microscope scans or illuminates the sample:

1. **IlluminationPattern**: Base class for general use cases

   .. code-block:: python

       illumination_pattern = IlluminationPattern(
           name='custom_pattern',
           description='Custom illumination pattern'
       )

2. **LineScan**: For line scanning methods (common in two-photon microscopy)

   .. code-block:: python

       line_scan = LineScan(
           name='line_scanning',
           description='Line scanning two-photon microscopy',
           scan_direction='horizontal',  # or 'vertical'
           line_rate_in_Hz=1000.0,       # lines per second
           dwell_time_in_s=1.0e-6        # time spent at each point
       )

3. **PlaneAcquisition**: For whole plane acquisition (common in light sheet and one-photon)

   .. code-block:: python

       plane_acquisition = PlaneAcquisition(
           name='plane_acquisition',
           description='Widefield fluorescence imaging',
           plane_thickness_in_um=5.0,
           illumination_angle_in_degrees=45.0,  # for light sheet
           plane_rate_in_Hz=100.0               # planes per second
       )

4. **RandomAccessScan**: For targeted, high-speed imaging of specific regions

   .. code-block:: python

       random_access_scan = RandomAccessScan(
           name='random_access',
           description='Targeted imaging of specific neurons',
           max_scan_points=1000,
           dwell_time_in_s=1.0e-6,
           scanning_pattern='spiral'  # or other pattern description
       )

Imaging Space Definition
^^^^^^^^^^^^^^^^^^^^^

Imaging spaces define the physical region being imaged:

1. **PlanarImagingSpace**: For 2D imaging

   .. code-block:: python

       # First define an illumination pattern
       line_scan = LineScan(
           name='line_scanning',
           description='Line scanning two-photon microscopy',
           scan_direction='horizontal',
           line_rate_in_Hz=1000.0,
           dwell_time_in_s=1.0e-6
       )
       
       # Then create the imaging space with the illumination pattern
       space_2d = PlanarImagingSpace(
           name='cortex_plane',
           description='Layer 2/3 of visual cortex',
           pixel_size_in_um=[1.0, 1.0],        # x, y spacing
           origin_coordinates=[-1.2, -0.6, -2.0], # relative to bregma
           location='Visual cortex',
           reference_frame='bregma',
           orientation='RAS',                    # Right-Anterior-Superior
           illumination_pattern=line_scan        # Include the illumination pattern
       )

2. **VolumetricImagingSpace**: For 3D imaging

   .. code-block:: python

       # First define an illumination pattern
       plane_acquisition = PlaneAcquisition(
           name='plane_acquisition',
           description='Light sheet imaging',
           plane_thickness_in_um=5.0,
           illumination_angle_in_degrees=45.0,
           plane_rate_in_Hz=100.0
       )
       
       # Then create the imaging space with the illumination pattern
       space_3d = VolumetricImagingSpace(
           name='cortex_volume',
           description='Visual cortex volume',
           voxel_size_in_um=[1.0, 1.0, 2.0],   # x, y, z spacing
           origin_coordinates=[-1.2, -0.6, -2.0],
           location='Visual cortex',
           reference_frame='bregma',
           orientation='RAS',
           illumination_pattern=plane_acquisition
       )

Common Workflows
-------------

2D Imaging
^^^^^^^^^

Basic workflow for 2D imaging:

.. code-block:: python

    # 1. Set up microscope with technique
    microscope = Microscope(
        name='2p-scope',
        description='Custom two-photon microscope',
        manufacturer='Custom Build',
        model='2P-Special',
        technique='mirror scanning',  # Specify the technique
    )
    nwbfile.add_device(microscope)

    # 2. Define illumination pattern
    line_scan = LineScan(
        name='line_scanning',
        description='Line scanning two-photon microscopy',
        scan_direction='horizontal',
        line_rate_in_Hz=1000.0,
        dwell_time_in_s=1.0e-6
    )

    # 3. Set up imaging space with illumination pattern
    planar_imaging_space = PlanarImagingSpace(
        name='cortex_plane',
        description='Layer 2/3 of visual cortex',
        pixel_size_in_um=[1.0, 1.0],        # x, y spacing
        origin_coordinates=[-1.2, -0.6, -2.0], # relative to bregma
        location='Visual cortex',
        reference_frame='bregma',
        orientation='RAS',                    # Right-Anterior-Superior
        illumination_pattern=line_scan        # Include the illumination pattern
    )

    # 4. Create imaging series
    microscopy_series = PlanarMicroscopySeries(
        name='microscopy_series',
        description='Two-photon calcium imaging',
        microscope=microscope,
        excitation_light_path=excitation,
        emission_light_path=emission,
        planar_imaging_space=planar_imaging_space,
        data=data,                # [frames, height, width]
        unit='a.u.',
        rate=30.0,
        starting_time=0.0,
    )
    nwbfile.add_acquisition(microscopy_series)

One-Photon Imaging with Plane Acquisition
^^^^^^^^^

Workflow for one-photon widefield imaging:

.. code-block:: python

    # 1. Set up microscope with technique
    microscope = Microscope(
        name='1p-scope',
        description='Custom one-photon microscope',
        manufacturer='Custom Build',
        model='1P-Special',
        technique='widefield',  # Specify the technique
    )
    nwbfile.add_device(microscope)

    # 2. Define illumination pattern
    plane_acquisition = PlaneAcquisition(
        name='plane_acquisition',
        description='Widefield fluorescence imaging',
        plane_thickness_in_um=5.0,
        plane_rate_in_Hz=30.0
    )

    # 3. Set up imaging space with illumination pattern
    planar_imaging_space = PlanarImagingSpace(
        name='hippo_plane',
        description='CA1 region of hippocampus',
        pixel_size_in_um=[1.0, 1.0],
        origin_coordinates=[-1.8, 2.0, 1.2],
        location='Hippocampus, CA1 region',
        reference_frame='bregma',
        orientation='RAS',
        illumination_pattern=plane_acquisition
    )

    # 4. Create imaging series
    microscopy_series = PlanarMicroscopySeries(
        name='imaging_data',
        description='One-photon calcium imaging',
        microscope=microscope,
        excitation_light_path=excitation,
        emission_light_path=emission,
        planar_imaging_space=planar_imaging_space,
        data=data,
        unit='a.u.',
        rate=30.0,
        starting_time=0.0
    )
    nwbfile.add_acquisition(microscopy_series)

3D Imaging with Random Access Scanning
^^^^^^^^^

Workflow for volumetric imaging with targeted scanning:

.. code-block:: python

    # 1. Set up microscope with technique
    microscope = Microscope(
        name='volume-scope',
        description='Custom volumetric imaging microscope',
        manufacturer='Custom Build',
        model='Volume-Special',
        technique='acousto-optical deflectors',  # Specify the technique
    )
    nwbfile.add_device(microscope)

    # 2. Define illumination pattern
    random_access_scan = RandomAccessScan(
        name='random_access',
        description='Targeted imaging of specific neurons',
        max_scan_points=1000,
        dwell_time_in_s=1.0e-6,
        scanning_pattern='spiral'
    )

    # 3. Set up volumetric space with illumination pattern
    volumetric_imaging_space = VolumetricImagingSpace(
        name='cortex_volume',
        description='Visual cortex volume',
        voxel_size_in_um=[1.0, 1.0, 2.0],   # x, y, z spacing
        origin_coordinates=[-1.2, -0.6, -2.0],
        location='Visual cortex',
        reference_frame='bregma',
        orientation='RAS',
        illumination_pattern=random_access_scan
    )

    # 4. Create volumetric series
    volume_series = VolumetricMicroscopySeries(
        name='volume_data',
        microscope=microscope,
        excitation_light_path=excitation,
        emission_light_path=emission,
        volumetric_imaging_space=volumetric_imaging_space,
        data=data,                # [frames, height, width, depths]
        unit='a.u.',
        rate=5.0,
        starting_time=0.0,
    )
    nwbfile.add_acquisition(volume_series)

ROI Segmentation
^^^^^^^^^^^^^

Workflow for ROI segmentation:

.. code-block:: python

    # 1. Create summary images
    mean_image = SummaryImage(
        name='mean',
        description='Mean intensity projection',
        data=np.mean(data, axis=0)
    )

    # 2. Create segmentation
    segmentation = Segmentation2D(
        name='rois',
        description='Manual ROI segmentation',
        planar_imaging_space=imaging_space,
        summary_images=[mean_image]
    )

    # 3. Add ROIs using image masks
    roi_mask = np.zeros((height, width), dtype=bool)
    roi_mask[256:266, 256:266] = True
    segmentation.add_roi(image_mask=roi_mask)

    # 4. Add ROIs using pixel masks
    pixel_mask = [
        [100, 100, 1.0],  # x, y, weight
        [101, 100, 1.0],
        [102, 100, 1.0]
    ]
    segmentation.add_roi(pixel_mask=pixel_mask)

Response Data Storage
^^^^^^^^^^^^^^^^^

Workflow for storing ROI responses:

.. code-block:: python

    # 1. Create ROI region
    roi_region = segmentation.create_roi_table_region(
        description='All ROIs',
        region=list(range(len(segmentation.id)))
    )

    # 2. Create response series
    response_series = MicroscopyResponseSeries(
        name='roi_responses',
        description='Fluorescence responses',
        data=responses,
        rois=roi_region,
        unit='n.a.',
        rate=30.0,
        starting_time=0.0,
    )

Best Practices
-----------

Data Organization
^^^^^^^^^^^^^

1. **Naming Conventions**
   - Use descriptive, consistent names
   - Include relevant metadata in descriptions
   - Document coordinate systems and reference frames

2. **Data Structure**
   - Group related data appropriately
   - Maintain clear relationships between raw and processed data
   - Include all necessary metadata
