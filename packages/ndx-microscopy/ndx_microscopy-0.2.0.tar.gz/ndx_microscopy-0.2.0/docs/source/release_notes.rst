.. _release_notes:

*************
Release Notes
*************

Version 0.2.0 (Upcoming)
============

Added support for different microscopy scanning methods and improved metadata.

Added
--------

* New illumination pattern classes to represent different microscopy scanning methods:
  
  * ``IlluminationPattern``: Base class for describing the illumination pattern used to acquire images
  * ``LineScan``: Line scanning method commonly used in two-photon microscopy
  * ``PlaneAcquisition``: Whole plane acquisition method, common for light sheet and one-photon techniques
  * ``RandomAccessScan``: Random access method for targeted, high-speed imaging of specific regions

* Added ``technique`` attribute to the ``Microscope`` class to describe the imaging technique used
* Updated ``ImagingSpace`` classes to include an ``illumination_pattern`` parameter, creating a direct link between the imaging space and the acquisition method
* Added mock implementations for all new classes in ``_mock.py`` for testing purposes
* Updated example notebooks to demonstrate the use of different scanning methods

Changed
-------

* Modified the YAML specification to include new neurodata type definitions and relationships
* Updated Python implementation files to expose the new classes in the API
* Enhanced test files to verify the new classes work correctly

Notes
-----

* These changes are backward compatible and add new functionality without removing existing features
* The ``illumination_pattern`` parameter is now required when creating ``ImagingSpace`` objects

Version 0.1.0
============

Initial release of ndx-microscopy extension.

Features
--------

* Microscope metadata: ``Microscope``
* Integration with ndx-ophys-devices for optical component specifications: ``ExcitationSource``/``PulsedExcitationSource``, ``BandOpticalFilter``/``EdgeOpticalFilter``, ``DichroicMirror``, ``Photodetector``, ``Indicator``
* Advanced light path configurations: ``ExcitationLightPath``, ``EmissionLightPath`` 
* Imaging space definitions: ``PlanarImagingSpace``, ``VolumetricImagingSpace``
* Support for 2D and 3D imaging: ``PlanarMicroscopySeries``, ``VolumetricMicroscopySeries``, ``MultiPlaneMicroscopyContainer``
* ROI/segmentation storage: ``SummaryImages``, ``Segmentation2D``, ``Segmentation3D``, ``SegmentationContainer``, ``MicroscopyResponseSeries``, ``MicroscopyResponseSeriesContainer``
* Abstract Neurodata types: ``ImagingSpace``, ``MicroscopySeries``, ``Segmentation``

Changes
-------

* Initial implementation of all neurodata data types
* Basic documentation and examples
* Integration tests and validation
