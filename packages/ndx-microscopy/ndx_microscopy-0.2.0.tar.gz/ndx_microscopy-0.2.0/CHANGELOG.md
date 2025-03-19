# v0.2.0 (March 19, 2025)

## Deprecations and Changes
- Change `grid_spacing_in_um` in `pixel_size_in_um` and `voxel_size_in_um` (and relative doc string) to better represent the physical dimension of the fundamental unit of the image (pixel or voxel).

## Bug Fixes

## Features

## Improvements
- New illumination pattern classes to represent different microscopy scanning methods:
  - `IlluminationPattern`: Base class for describing the illumination pattern used to acquire images
  - `LineScan`: Line scanning method commonly used in two-photon microscopy
  - `PlaneAcquisition`: Whole plane acquisition method, common for light sheet and one-photon techniques
  - `RandomAccessScan`: Random access method for targeted, high-speed imaging of specific regions

- Added `technique` attribute to the `Microscope` class to describe the imaging technique used

- Updated `ImagingSpace` classes to include an `illumination_pattern` parameter, creating a direct link between the imaging space and the acquisition method

- Added mock implementations for all new classes in `_mock.py` for testing purposes

- Updated example notebooks to demonstrate the use of different scanning methods

## Notes

- These changes are backward compatible and add new functionality without removing existing features
- The `illumination_pattern` parameter is now required when creating `ImagingSpace` objects
