.. _examples:

********
Examples
********

This section provides detailed examples of using the ndx-microscopy extension for various microscopy techniques and workflows.

Two-Photon Calcium Imaging
------------------------

Complete example of two-photon calcium imaging with full optical path configuration:

.. code-block:: python

    from datetime import datetime
    from uuid import uuid4
    import matplotlib.pyplot as plt
    import numpy as np
    from pynwb import NWBFile, NWBHDF5IO
    from ndx_microscopy import (
        Microscope, 
        ExcitationLightPath,
        EmissionLightPath,
        PlanarImagingSpace,
        PlanarMicroscopySeries,
        Segmentation2D,
        SummaryImage,
        MicroscopyResponseSeries,
        MicroscopyResponseSeriesContainer,
        LineScan,  
        PlaneAcquisition, 
        RandomAccessScan,
    )
    from ndx_ophys_devices import (
        PulsedExcitationSource,
        BandOpticalFilter,
        DichroicMirror,
        Photodetector,
        Indicator
    )

    # Create NWB file
    nwbfile = NWBFile(
        session_description='Two-photon calcium imaging session',
        identifier=str(uuid4()),
        session_start_time=datetime.now(),
        lab='Neural Imaging Lab',
        institution='University of Neuroscience',
        experiment_description='GCaMP6f imaging in visual cortex'
    )

    # Set up microscope
    microscope = Microscope(
        name='2p-scope',
        description='Custom two-photon microscope for calcium imaging',
        manufacturer='Custom Build',
        model='2P-Special',
        technique='mirror scanning'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    laser = PulsedExcitationSource(
        name="chameleon",
        illumination_type="Laser",
        manufacturer="Coherent",
        model="Chameleon Ultra II",
        excitation_mode="two-photon",
        excitation_wavelength_in_nm=920.0,  # Common for GCaMP6f imaging
        power_in_W=2.5,  # Average power at sample, typically 1-3W for deep imaging
        peak_power_in_W=100000.0,  # 100kW peak power
        peak_pulse_energy_in_J=1.25e-9,  # 1.25 nJ
        pulse_rate_in_Hz=80.0e6,  # 80MHz typical for Chameleon Ultra II
    )
    nwbfile.add_device(laser)

    excitation_filter = BandOpticalFilter(
        name="excitation_filter",
        filter_type="Bandpass",
        manufacturer="Semrock",
        model="FF01-920/80",
        center_wavelength_in_nm=920.0,
        bandwidth_in_nm=80.0,
    )
    nwbfile.add_device(excitation_filter)

    dichroic = DichroicMirror(
        name="primary_dichroic",
        manufacturer="Semrock",
        model="FF757-Di01",  # Common dichroic for GCaMP imaging
        cut_on_wavelength_in_nm=757.0,  # Transmits >757nm
        cut_off_wavelength_in_nm=750.0,  # Reflects <750nm
        transmission_band_in_nm=[757.0, 1100.0],  # Transmits NIR excitation light
        reflection_band_in_nm=(400.0, 750.0),  # Reflects emission light (including 510nm GCaMP6f emission)
        angle_of_incidence_in_degrees=45.0,  # Standard angle for dichroic mirrors in microscopes
    )
    nwbfile.add_device(dichroic)

    emission_filter = BandOpticalFilter(
        name="emission_filter",
        filter_type="Bandpass",
        manufacturer="Semrock",
        model="FF01-510/84",
        center_wavelength_in_nm=510.0,
        bandwidth_in_nm=84.0,
    )
    nwbfile.add_device(emission_filter)

    detector = Photodetector(
        name="pmt",
        detector_type="PMT",
        manufacturer="Hamamatsu",
        model="R6357",
        detected_wavelength_in_nm=510.0,
        gain=1000000.0,  # 10^6 typical PMT gain
        gain_unit="V/A",  # Voltage/Current
    )
    nwbfile.add_device(detector)

    # Create indicator
    indicator = Indicator(
        name="gcamp6f",
        label="GCaMP6f",
        description="Calcium indicator for two-photon imaging",
        manufacturer="Addgene",
        injection_brain_region="Visual cortex",
        injection_coordinates_in_mm=[-2.5, 3.2, 0.5],
    )

    # Configure light paths
    excitation = ExcitationLightPath(
        name='2p_excitation',
        description='Femtosecond pulsed laser pathway',
        excitation_source=laser,
        excitation_filter=excitation_filter,
        dichroic_mirror=dichroic
    )
    nwbfile.add_lab_meta_data(excitation)

    emission = EmissionLightPath(
        name='gcamp_emission',
        description='GCaMP6f emission pathway',
        indicator=indicator,
        photodetector=detector,
        emission_filter=emission_filter,
        dichroic_mirror=dichroic
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
    imaging_space = PlanarImagingSpace(
        name='cortex_plane1',
        description='Layer 2/3 of visual cortex',
        pixel_size_in_um=[1.0, 1.0],
        origin_coordinates=[-1.2, -0.6, -2.0],
        location='Visual cortex, layer 2/3',
        reference_frame='bregma',
        orientation='RAS',  # Right-Anterior-Superior
        illumination_pattern=line_scan  # Include the illumination pattern
    )

    # Create example imaging data
    frames = 1000
    height = 512
    width = 512
    data = np.random.rand(frames, height, width)

    # Create imaging series
    imaging_series = PlanarMicroscopySeries(
        name='imaging_data',
        description='Two-photon calcium imaging',
        microscope=microscope,
        excitation_light_path=excitation,
        emission_light_path=emission,
        planar_imaging_space=imaging_space,
        data=data,
        unit='a.u.',
        rate=30.0,
        starting_time=0.0
    )
    nwbfile.add_acquisition(imaging_series)

    # Create ophys processing module
    ophys_module = nwbfile.create_processing_module(
        name='ophys',
        description='Optical physiology processing module'
    )

    # Create summary images
    mean_image = SummaryImage(
        name='mean',
        description='Mean intensity projection',
        data=np.mean(data, axis=0)
    )

    max_image = SummaryImage(
        name='max',
        description='Maximum intensity projection',
        data=np.max(data, axis=0)
    )

    # Create segmentation
    segmentation = Segmentation2D(
        name='rois',
        description='Manual ROI segmentation',
        planar_imaging_space=imaging_space,
        summary_images=[mean_image, max_image]
    )

    # Add ROIs using image masks
    roi_mask = np.zeros((height, width), dtype=bool)
    roi_mask[256:266, 256:266] = True  # 10x10 ROI
    segmentation.add_roi(image_mask=roi_mask)

    # OR Add ROIs using pixel masks
    # pixel_mask = [
    #     [100, 100, 1.0],  # x, y, weight
    #     [101, 100, 1.0],
    #     [102, 100, 1.0]
    # ]
    # segmentation.add_roi(pixel_mask=pixel_mask)

    # Create ROI responses
    roi_region = segmentation.create_roi_table_region(
        description='All ROIs',
        region=list(range(len(segmentation.id)))
    )

    # Extract responses (example calculation)
    num_rois = len(segmentation.id)
    responses = np.zeros((frames, num_rois))

    for i, roi_mask in enumerate(segmentation.image_mask[:]):
        roi_data = data[:, roi_mask]
        responses[:, i] = np.mean(roi_data, axis=1)

    # Create response series
    response_series = MicroscopyResponseSeries(
        name='roi_responses',
        description='Fluorescence responses from ROIs',
        data=responses,
        rois=roi_region,
        unit='n.a.',
        rate=30.0,
        starting_time=0.0
    )

    # Create container for response series
    response_container = MicroscopyResponseSeriesContainer(
        name='responses',
        microscopy_response_series=[response_series]
    )

    # Add segmentation and responses to ophys module
    ophys_module.add(segmentation)
    ophys_module.add(response_container)

    # Save file
    with NWBHDF5IO('calcium_imaging.nwb', 'w') as io:
        io.write(nwbfile)

    # Read file and access data
    with NWBHDF5IO('calcium_imaging.nwb', 'r') as io:
        nwbfile = io.read()

        # Access imaging data
        imaging = nwbfile.acquisition['imaging_data']
        raw_data = imaging.data[:]

        # Access ROI data
        ophys = nwbfile.processing['ophys']
        rois = ophys['rois']
        roi_masks = rois.image_mask[:]

        # Access responses
        responses = ophys['responses']
        roi_data = responses['roi_responses'].data[:]

Volumetric Imaging
---------------

Example of volumetric imaging with 3D ROI segmentation:

.. code-block:: python

    from datetime import datetime
    from uuid import uuid4
    import numpy as np
    from pynwb import NWBFile, NWBHDF5IO
    from ndx_microscopy import (
        Microscope,
        ExcitationLightPath,
        EmissionLightPath,
        VolumetricImagingSpace,
        VolumetricMicroscopySeries,
        Segmentation3D,
        SummaryImage,
        MicroscopyResponseSeries,
        MicroscopyResponseSeriesContainer,
        RandomAccessScan
    )
    from ndx_ophys_devices import (
        ExcitationSource,
        BandOpticalFilter,
        DichroicMirror,
        Photodetector,
        Indicator
    )

    # Create NWB file
    nwbfile = NWBFile(
        session_description='Volumetric imaging session',
        identifier=str(uuid4()),
        session_start_time=datetime.now(),
        lab='Neural Dynamics Lab',
        institution='University of Neuroscience',
        experiment_description='Volumetric imaging in cortex'
    )

    # Set up microscope with technique
    microscope = Microscope(
        name='volume-scope',
        description='Custom volumetric imaging microscope',
        manufacturer='Custom Build',
        model='Volume-Special',
        technique='acousto-optical deflectors'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    # Set up optical components
    laser = ExcitationSource(
        name='laser',
        illumination_type='Laser',
        manufacturer='Coherent',
        model='Chameleon',
        excitation_mode = "two-photon",
        excitation_wavelength_in_nm=920.0,
        power_in_W=2.0,
        intensity_in_W_per_m2=1000.0,
        exposure_time_in_s=0.001
    )
    nwbfile.add_device(laser)

    excitation_filter = BandOpticalFilter(
        name='excitation_filter',
        filter_type='Bandpass',
        manufacturer='Semrock',
        model='FF01-920/80',
        center_wavelength_in_nm=920.0,
        bandwidth_in_nm=80.0
    )
    nwbfile.add_device(excitation_filter)

    dichroic = DichroicMirror(
        name='primary_dichroic',
        manufacturer='Semrock',
        model='FF695-Di02',
        cut_wavelength_in_nm=695.0
    )
    nwbfile.add_device(dichroic)

    emission_filter = BandOpticalFilter(
        name='emission_filter',
        filter_type='Bandpass',
        manufacturer='Semrock',
        model='FF01-510/84',
        center_wavelength_in_nm=510.0,
        bandwidth_in_nm=84.0
    )
    nwbfile.add_device(emission_filter)

    detector = Photodetector(
        name='pmt',
        detector_type='PMT',
        manufacturer='Hamamatsu',
        model='R6357',
        detected_wavelength_in_nm=510.0,
        gain=70.0,
        gain_unit='dB'
    )
    nwbfile.add_device(detector)

    # Create indicator
    indicator = Indicator(
        name='gcamp6f',
        label='GCaMP6f',
        description='Calcium indicator for volumetric imaging',
        manufacturer='Addgene',
        injection_brain_region='Visual cortex',
        injection_coordinates_in_mm=[-2.5, 3.2, 0.5]
    )

    # Configure light paths
    excitation = ExcitationLightPath(
        name='volume_excitation',
        description='Laser excitation pathway for volumetric imaging',
        excitation_source=laser,
        excitation_filter=excitation_filter,
        dichroic_mirror=dichroic
    )
    nwbfile.add_lab_meta_data(excitation)

    emission = EmissionLightPath(
        name='volume_emission',
        description='GCaMP6f emission pathway',
        indicator=indicator,
        photodetector=detector,
        emission_filter=emission_filter,
        dichroic_mirror=dichroic
    )
    nwbfile.add_lab_meta_data(emission)

    # Define illumination pattern for volumetric imaging
    random_access_scan = RandomAccessScan(
        name='random_access',
        description='Targeted imaging of specific neurons',
        max_scan_points=1000,
        dwell_time_in_s=1.0e-6,
        scanning_pattern='spiral'
    )

    # Define volumetric imaging space with illumination pattern
    volume_space = VolumetricImagingSpace(
        name='cortex_volume',
        description='Visual cortex volume',
        voxel_size_in_um=[1.0, 1.0, 2.0],  # Higher spacing in z
        origin_coordinates=[-1.2, -0.6, -2.0],
        location='Visual cortex',
        reference_frame='bregma',
        orientation='RAS',  # Right-Anterior-Superior
        illumination_pattern=random_access_scan  # Include the illumination pattern
    )

    # Create example volumetric data
    frames = 100
    height = 512
    width = 512
    depths = 10
    data = np.random.rand(frames, height, width, depths)

    # Create volumetric series
    volume_series = VolumetricMicroscopySeries(
        name='volume_data',
        description='Volumetric imaging series',
        microscope=microscope,
        excitation_light_path=excitation,
        emission_light_path=emission,
        imaging_space=volume_space,
        data=data,
        unit='a.u.',
        rate=5.0,  # Lower rate for volumetric imaging
        starting_time=0.0
    )
    nwbfile.add_acquisition(volume_series)

    # Create ophys processing module
    ophys_module = nwbfile.create_processing_module(
        name='ophys',
        description='Optical physiology processing module'
    )

    # Create 3D summary images
    mean_image = SummaryImage(
        name='mean',
        description='Mean intensity projection',
        data=np.mean(data, axis=0)
    )

    max_image = SummaryImage(
        name='max',
        description='Maximum intensity projection',
        data=np.max(data, axis=0)
    )

    # Create 3D segmentation
    segmentation = Segmentation3D(
        name='volume_rois',
        description='3D ROI segmentation',
        volumetric_imaging_space=volume_space,
        summary_images=[mean_image, max_image]
    )

    # Add 3D ROIs using image masks
    roi_mask = np.zeros((height, width, depths), dtype=bool)
    roi_mask[256:266, 256:266, 4:6] = True  # 10x10x2 ROI
    segmentation.add_roi(image_mask=roi_mask)

    # Add ROIs using voxel masks
    voxel_mask = [
        [100, 100, 5, 1.0],  # x, y, z, weight
        [101, 100, 5, 1.0],
        [102, 100, 5, 1.0]
    ]
    segmentation.add_roi(voxel_mask=voxel_mask)

    # Create ROI responses
    roi_region = segmentation.create_roi_table_region(
        description='All 3D ROIs',
        region=list(range(len(segmentation.id)))
    )

    # Extract responses (example calculation)
    num_rois = len(segmentation.id)
    responses = np.zeros((frames, num_rois))
    
    for i, roi_mask in enumerate(segmentation.image_mask[:]):
        roi_data = data[:, roi_mask]
        responses[:, i] = np.mean(roi_data, axis=1)

    # Create response series
    response_series = MicroscopyResponseSeries(
        name='volume_responses',
        description='Fluorescence responses from 3D ROIs',
        data=responses,
        rois=roi_region,
        unit='n.a.',
        rate=5.0,
        starting_time=0.0
    )

    # Create container for response series
    response_container = MicroscopyResponseSeriesContainer(
        name='volume_responses',
        microscopy_response_series=[response_series]
    )

    # Add segmentation and responses to ophys module
    ophys_module.add(segmentation)
    ophys_module.add(response_container)

    # Save file
    with NWBHDF5IO('volumetric_imaging.nwb', 'w') as io:
        io.write(nwbfile)

    # Read file and access data
    with NWBHDF5IO('volumetric_imaging.nwb', 'r') as io:
        nwbfile = io.read()
        
        # Access volumetric data
        imaging = nwbfile.acquisition['volume_data']
        volume_data = imaging.data[:]
        
        # Access ROI data
        ophys = nwbfile.processing['ophys']
        rois = ophys['volume_rois']
        roi_masks = rois.image_mask[:]
        
        # Access responses
        responses = ophys['volume_responses']
        roi_data = responses['volume_responses'].data[:]

Multi-Plane Imaging
----------------

Example of multi-plane imaging with an electrically tunable lens:

.. code-block:: python

    from datetime import datetime
    from uuid import uuid4
    import numpy as np
    from pynwb import NWBFile, NWBHDF5IO
    from ndx_microscopy import (
        Microscope,
        ExcitationLightPath,
        EmissionLightPath,
        PlanarImagingSpace,
        PlanarMicroscopySeries,
        MultiPlaneMicroscopyContainer,
        Segmentation2D,
        SummaryImage,
        MicroscopyResponseSeries,
        MicroscopyResponseSeriesContainer,
        SegmentationContainer,
        PlaneAcquisition
    )
    from ndx_ophys_devices import (
        ExcitationSource,
        BandOpticalFilter,
        DichroicMirror,
        Photodetector,
        Indicator
    )

    # Create NWB file
    nwbfile = NWBFile(
        session_description='Multi-plane imaging session',
        identifier=str(uuid4()),
        session_start_time=datetime.now(),
        lab='Neural Circuits Lab',
        institution='University of Neuroscience',
        experiment_description='Multi-plane imaging with ETL'
    )

    # Set up microscope with ETL and technique
    microscope = Microscope(
        name='etl-scope',
        description='Two-photon microscope with electrically tunable lens',
        manufacturer='Custom Build',
        model='ETL-Special',
        technique='electrically tunable lens'  # Specify the technique used
    )
    nwbfile.add_device(microscope)

    # Set up optical components
    laser = ExcitationSource(
        name='laser',
        illumination_type='Laser',
        manufacturer='Coherent',
        model='Chameleon',
        excitation_wavelength_in_nm=920.0,
        power_in_W=1.5,
        intensity_in_W_per_m2=1000.0,
        exposure_time_in_s=0.001
    )
    nwbfile.add_device(laser)

    excitation_filter = BandOpticalFilter(
        name='excitation_filter',
        filter_type='Bandpass',
        manufacturer='Semrock',
        model='FF01-920/80',
        center_wavelength_in_nm=920.0,
        bandwidth_in_nm=80.0
    )
    nwbfile.add_device(excitation_filter)

    dichroic = DichroicMirror(
        name='primary_dichroic',
        manufacturer='Semrock',
        model='FF695-Di02',
        cut_wavelength_in_nm=695.0
    )
    nwbfile.add_device(dichroic)

    emission_filter = BandOpticalFilter(
        name='emission_filter',
        filter_type='Bandpass',
        manufacturer='Semrock',
        model='FF01-510/84',
        center_wavelength_in_nm=510.0,
        bandwidth_in_nm=84.0
    )
    nwbfile.add_device(emission_filter)

    detector = Photodetector(
        name='pmt',
        detector_type='PMT',
        manufacturer='Hamamatsu',
        model='R6357',
        detected_wavelength_in_nm=510.0,
        gain=70.0,
        gain_unit='dB'
    )
    nwbfile.add_device(detector)

    # Create indicator
    indicator = Indicator(
        name='gcamp6f',
        label='GCaMP6f',
        description='Calcium indicator for multi-plane imaging',
        manufacturer='Addgene',
        injection_brain_region='Visual cortex',
        injection_coordinates_in_mm=[-2.5, 3.2, 0.5]
    )

    # Configure light paths
    excitation = ExcitationLightPath(
        name='etl_excitation',
        description='Laser excitation pathway with ETL',
        excitation_source=laser,
        excitation_filter=excitation_filter,
        dichroic_mirror=dichroic
    )
    nwbfile.add_lab_meta_data(excitation)

    emission = EmissionLightPath(
        name='etl_emission',
        description='GCaMP6f emission pathway',
        indicator=indicator,
        photodetector=detector,
        emission_filter=emission_filter,
        dichroic_mirror=dichroic
    )
    nwbfile.add_lab_meta_data(emission)

    # Create ophys processing module
    ophys_module = nwbfile.create_processing_module(
        name='ophys',
        description='Optical physiology processing module'
    )

    # Create multiple imaging planes
    planar_series_list = []
    segmentation_list = []
    response_series_list = []
    depths = [-100, -50, 0, 50, 100]  # Depths in µm

    # Create illumination pattern
    plane_acquisition = PlaneAcquisition(
        name=f'plane_acquisition',
        description=f'Plane acquisition',
        plane_thickness_in_um=2.0
    )

    for depth in depths:
        # Create imaging space for this depth with illumination pattern
        plane_space = PlanarImagingSpace(
            name=f'plane_depth_{depth}',
            description=f'Imaging plane at {depth} µm depth',
            pixel_size_in_um=[1.0, 1.0],
            origin_coordinates=[-1.2, -0.6, depth/1000],  # Convert to mm
            location='Visual cortex',
            reference_frame='bregma',
            orientation='RAS',
            illumination_pattern=plane_acquisition  # Include the illumination pattern
        )

        # Create example data for this plane
        frames = 1000
        height = 512
        width = 512
        data = np.random.rand(frames, height, width)

        # Create imaging series for this plane
        plane_series = PlanarMicroscopySeries(
            name=f'imaging_depth_{depth}',
            description=f'Imaging data at {depth} µm depth',
            microscope=microscope,
            excitation_light_path=excitation,
            emission_light_path=emission,
            imaging_space=plane_space,
            data=data,
            unit='a.u.',
            conversion=1.0,
            offset=0.0,
            rate=30.0,
            starting_time=0.0
        )
        planar_series_list.append(plane_series)

        # Create summary images for this plane
        mean_image = SummaryImage(
            name=f'mean_{depth}',
            description=f'Mean intensity projection at {depth} µm',
            data=np.mean(data, axis=0)
        )

        max_image = SummaryImage(
            name=f'max_{depth}',
            description=f'Maximum intensity projection at {depth} µm',
            data=np.max(data, axis=0)
        )

        # Create segmentation for this plane
        segmentation = Segmentation2D(
            name=f'rois_{depth}',
            description=f'ROI segmentation at {depth} µm',
            planar_imaging_space=plane_space,
            summary_images=[mean_image, max_image]
        )

        # Add ROIs
        roi_mask = np.zeros((height, width), dtype=bool)
        roi_mask[256:266, 256:266] = True
        segmentation.add_roi(image_mask=roi_mask)

        segmentation_list.append(segmentation)

        # Create ROI responses
        roi_region = segmentation.create_roi_table_region(
            description=f'ROIs at {depth} µm',
            region=list(range(len(segmentation.id)))
        )

        # Extract responses
        num_rois = len(segmentation.id)
        responses = np.zeros((frames, num_rois))
        
        for i, roi_mask in enumerate(segmentation.image_mask[:]):
            roi_data = data[:, roi_mask]
            responses[:, i] = np.mean(roi_data, axis=1)

        # Create response series
        response_series = MicroscopyResponseSeries(
            name=f'responses_{depth}',
            description=f'Fluorescence responses at {depth} µm',
            data=responses,
            rois=roi_region,
            unit='n.a.',
            rate=30.0,
            starting_time=0.0
        )
        response_series_list.append(response_series)

    # Create containers
    multi_plane_container = MultiPlaneMicroscopyContainer(
        name='multi_plane_data',
        planar_microscopy_series=planar_series_list
    )
    nwbfile.add_acquisition(multi_plane_container)

    segmentation_container = SegmentationContainer(
        name='plane_segmentations',
        segmentations=segmentation_list
    )
    ophys_module.add(segmentation_container)

    response_container = MicroscopyResponseSeriesContainer(
        name='plane_responses',
        microscopy_response_series=response_series_list
    )
    ophys_module.add(response_container)

    # Save file
    with NWBHDF5IO('multi_plane_imaging.nwb', 'w') as io:
        io.write(nwbfile)

    # Read file and access data
    with NWBHDF5IO('multi_plane_imaging.nwb', 'r') as io:
        nwbfile = io.read()
        
        # Access multi-plane data
        multi_plane = nwbfile.acquisition['multi_plane_data']
        
        # Access specific plane data
        plane_0 = multi_plane.planar_microscopy_series['imaging_depth_0']
        plane_data = plane_0.data[:]
        
        # Access ROI data
        ophys = nwbfile.processing['ophys']
        segmentations = ophys['plane_segmentations']
        rois_0 = segmentations['rois_0']
        roi_masks = rois_0.image_mask[:]
        
        # Access responses
        responses = ophys['plane_responses']
        responses_0 = responses['responses_0']
        roi_data = responses_0.data[:]
