.. _api:

***
API
***

This section provides detailed documentation for all classes and methods in the ndx-microscopy extension.

Device Components
===========

Microscope
---------
.. autoclass:: ndx_microscopy.Microscope
   :members:
   :undoc-members:
   :show-inheritance:

Light Path Components
===================

ExcitationLightPath
------------------
.. autoclass:: ndx_microscopy.ExcitationLightPath
   :members:
   :undoc-members:
   :show-inheritance:

Methods
^^^^^^^
.. automethod:: ndx_microscopy.ExcitationLightPath.get_excitation_wavelength

EmissionLightPath
----------------
.. autoclass:: ndx_microscopy.EmissionLightPath
   :members:
   :undoc-members:
   :show-inheritance:

Methods
^^^^^^^
.. automethod:: ndx_microscopy.EmissionLightPath.get_emission_wavelength
.. automethod:: ndx_microscopy.EmissionLightPath.get_indicator_label

Imaging Space Components
=====================

ImagingSpace
-----------
.. autoclass:: ndx_microscopy.ImagingSpace
   :members:
   :undoc-members:
   :show-inheritance:

PlanarImagingSpace
-----------------
.. autoclass:: ndx_microscopy.PlanarImagingSpace
   :members:
   :undoc-members:
   :show-inheritance:

VolumetricImagingSpace
---------------------
.. autoclass:: ndx_microscopy.VolumetricImagingSpace
   :members:
   :undoc-members:
   :show-inheritance:

Microscopy Series Components
=========================

MicroscopySeries
---------------
.. autoclass:: ndx_microscopy.MicroscopySeries
   :members:
   :undoc-members:
   :show-inheritance:

PlanarMicroscopySeries
---------------------
.. autoclass:: ndx_microscopy.PlanarMicroscopySeries
   :members:
   :undoc-members:
   :show-inheritance:

VolumetricMicroscopySeries
-------------------------
.. autoclass:: ndx_microscopy.VolumetricMicroscopySeries
   :members:
   :undoc-members:
   :show-inheritance:

MultiPlaneMicroscopyContainer
---------------------------
.. autoclass:: ndx_microscopy.MultiPlaneMicroscopyContainer
   :members:
   :undoc-members:
   :show-inheritance:

Segmentation Components
====================

Segmentation
-----------
.. autoclass:: ndx_microscopy.Segmentation
   :members:
   :undoc-members:
   :show-inheritance:

Segmentation2D
-------------
.. autoclass:: ndx_microscopy.Segmentation2D
   :members:
   :undoc-members:
   :show-inheritance:

Methods
^^^^^^^
.. automethod:: ndx_microscopy.Segmentation2D.add_roi
.. automethod:: ndx_microscopy.Segmentation2D.pixel_to_image
.. automethod:: ndx_microscopy.Segmentation2D.image_to_pixel
.. automethod:: ndx_microscopy.Segmentation2D.create_roi_table_region

Segmentation3D
-------------
.. autoclass:: ndx_microscopy.Segmentation3D
   :members:
   :undoc-members:
   :show-inheritance:

Methods
^^^^^^^
.. automethod:: ndx_microscopy.Segmentation3D.add_roi
.. automethod:: ndx_microscopy.Segmentation3D.voxel_to_image
.. automethod:: ndx_microscopy.Segmentation3D.image_to_voxel
.. automethod:: ndx_microscopy.Segmentation3D.create_roi_table_region

SegmentationContainer
-------------------
.. autoclass:: ndx_microscopy.SegmentationContainer
   :members:
   :undoc-members:
   :show-inheritance:

Methods
^^^^^^^
.. automethod:: ndx_microscopy.SegmentationContainer.add_segmentation

SummaryImage
-----------
.. autoclass:: ndx_microscopy.SummaryImage
   :members:
   :undoc-members:
   :show-inheritance:

Response Series Components
=======================

MicroscopyResponseSeries
----------------------
.. autoclass:: ndx_microscopy.MicroscopyResponseSeries
   :members:
   :undoc-members:
   :show-inheritance:

MicroscopyResponseSeriesContainer
------------------------------
.. autoclass:: ndx_microscopy.MicroscopyResponseSeriesContainer
   :members:
   :undoc-members:
   :show-inheritance:
