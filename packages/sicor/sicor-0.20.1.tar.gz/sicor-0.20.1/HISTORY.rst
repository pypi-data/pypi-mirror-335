=======
History
=======

0.20.1 (2025-03-20)
-------------------

* !127: Fixed ValueError that avoided automatic retraining of novelty detector for Landsat/Sentinel-2 cloud screening.
  (fixes #107 and #73). Removed pinning of scikit-learn to <=1.2.2.


0.20.0 (2024-08-28)
-------------------

* Bumped version of docker base image.
* Adapted CI runner build script to upstream changes in GitLab 17.0.
* !126: Migrated setup procedure from using setup.py + setup.cfg to using pyproject.toml only.
  Moved binary scripts to cli subfolder. Removed mock requirement (replaced by unittest.mock).


0.19.4 (2024-05-30)
-------------------

* !125: Fixed zero-BOA-reflectance-values in the VNIR at pixels below sea level.


0.19.3 (2024-05-16)
-------------------

* !123: Vectorized first guess retrievals for water vapor, liquid water, ice, and snow. This speeds up the computations
  from several minutes to a few seconds.
* !122: Handled cases where LUT range is exceeded by the spectrum in the water vapor and snow first guess retrieval
  (avoids NaNs in the first guess output as well as subsequent artefacts in the AC output).
* !124: Vectorized parts of sicor_ac_enmap which mainly improves the runtime on Linux (factor 4-5).


0.19.2 (2024-04-05)
-------------------

* !120: DEM values below sea level are now automatically set to 0 instead of raising an AssertionError.
* !121: Fixed #100 (Water vapor first guess retrieval fails with recently acquired EnMAP data).
  Added independent band index selection for first guess calculation of the three phases of water.
  Replaced potential non-physical values in water vapor first guess (e.g., for cloudy, shaded, or water pixel).
  Replaced empirical line solution by combined water vapor field smoothing and per-pixel inversion of surface
  reflectance. Added smoothing sigma key to enmap options file.


0.19.1 (2023-12-11)
-------------------

Maintenance:

* Replaced deprecated direct calls of setup.py.
* !118: Fixed #104 (Numba DeprecationWarning).
* Fixed some typos.
* Fixed deprecated call of np.int.
* Pinned isofit to >2.10.
* Bumped version of docker base image.
* Fixed #107 (Sentinel-2 tests broken due to scikit-learn/pickle exception.) by pinning scikit-learn to <=1.2.2 for now.


0.19.0 (2023-05-23)
-------------------

Maintenance:

* !112: Adapted SLIC segmentation to scikit-image 0.20.0 (fixes #103).
* !113: Revised CI jobs and runner (now based on Ubuntu). Revised requirements and environment files.
* !114: Dropped Python 3.6/3.7 support and add 3.9, 3.10, and 3.11 instead.
* !115: Moved linting into separate CI job.
* !116: Fixed scipy DeprecationWarnings.
* !117: Renamed master branch to main.
* !119: Implemented workaround for unset PROJ_DATA/PROJ_LIB environment variable.


0.18.0 (2022-02-04)
-------------------

New features:

* Added 'Lazy Gaussian inversion' of snow and ice surface properties based on joint OE of atmosphere and surface state.
* Switched from nosetests to pytest.
* Activated multiprocessing for coverage.

Bugfixes:

* Added pool.close() and pool.join() everywhere where multiprocessing.Pool is called.


0.17.6 (2021-12-20)
-------------------

Bugfixes:

* Added keyword 'start_label' to SLIC segmentation to avoid index error in LUT interpolation.


0.17.5 (2021-09-30)
-------------------

Bugfixes:

* Added download option from atmosphere data store for migrated ECMWF 'cams_nrealtime' datasets.


0.17.4 (2021-09-29)
-------------------

New features:

* Automatic publication for new version tags on real Zenodo instead of its sandbox.


0.17.3 (2021-09-29)
-------------------

New features:

* Automatic upload to Zenodo sandbox for new version tags.


0.17.2 (2021-09-28)
-------------------

Bugfixes:

* Added tests directory as export-ignore to .gitattributes to reduce upload file size of Zenodo sandbox archive.


0.17.1 (2021-09-23)
-------------------

Bugfixes:

* Fixed bug in Zenodo sandbox send-snapshot CI job.


0.17.0 (2021-09-23)
-------------------

New features:

* Zenodo sandbox send-snapshot CI job.
* Added .zenodo.json metadata dictionary.


0.16.5 (2021-09-21)
-------------------

New features:

* Multiprocessing option for water vapor first guess retrieval.
* Multiprocessing mode of SICOR available again on macOS.
* Option to choose between two solar irradiance models: 'new_kurucz' and 'fontenla'.

Bugfixes:

* Added missing initializer to multiprocessing pool in empirical line calculation and set multiprocessing start method to fork.
* Disabled water vapor first guess retrieval over water surfaces in case SICOR is running for land+water pixels.


0.16.4 (2021-06-18)
-------------------

Bugfixes:

* Updated setup.py by removing check for packages that do not install well with pip. This avoids incompatibilities with the latest gdal versions.


0.16.3 (2021-06-17)
-------------------

Bugfixes:

* Disabled multiprocessing for both the optimization and the empirical line extrapolation in case SICOR is running on Windows or macOS.


0.16.2 (2021-05-26)
-------------------

New features:

* Dimensionality reduction of LUT grid to increase interpolation speed.
* Updated final log message of SICOR AC for EnMAP.
* First guess water vapor retrieval is only applied to land pixels if land_only is set to true.

Bugfixes:

* Fixed bug in empirical line function which produced unrealistic peaks in water reflectance spectra.
* Removed infinite values from water vapor first guess map to ensure convergence of Eigenvalues when calculating information content.
* Removed numba jit from hyperspectral LUT interpolation to avoid potential numba related bugs.
* Data arrays from the EnMAP L1B object are now safely copied instead of remaining mutable. This prevents issues with later usages.


0.16.1 (2021-03-24)
-------------------

New features:

* 'make lint' now directly prints errors instead of only logging them to logfiles.
* Automatic retraining of S2 novelty detector in case pretrained scikit-learn random forest model is out of date.

Bugfixes:

* Pinned gdal to version<=3.1.2 to avoid import error.
* Fixed bug in empirical line function, which caused one single remaining unprocessed segmentation label.
* Replaced deprecated gdal imports to fix "DeprecationWarning: gdal.py was placed in a namespace, it is now available as osgeo.gdal".
* Updated cerberus schema for SicorValidator to avoid missing path warning in case of LUT file.
* Updated download link and file size of S2 novelty detector and unpinned scikit-learn version.


0.16.0 (2021-02-23)
-------------------

New features:

* Transformation of VNIR data cube to SWIR sensor geometry to enable accurate segmentation and first guess retrievals.
* Well-arranged separation between EnMAP-specific AC and generic AC.
* Added incorporation of uncertainties due to model unknowns.
* Extended options files with additional parameters:
  * Prior mean and standard deviation of state vector parameters
  * Standard deviations of model unknowns
  * Inversion parameters
* Extended optional output of Optimal Estimation:
  * Jacobian of solution state
  * Convergence message
  * Number of iterations
  * Gain matrix
  * Averaging kernel matrix
  * Value of cost function
  * Degrees of freedom
  * Information content
  * Retrieval noise
  * Smoothing error
* Updated first guess retrievals.

Bugfixes:

* Updated keyword for excluding patterns from URL check.
* Fixed bug in LUT file assertion.
* Removed slow inversion method based on downhill simplex algorithm.
* Removed option to turn off ice retrieval.


0.15.6 (2021-02-05)
-------------------

New features:

* Two optional processing modes for EnMAP data: 'land only' and 'land + water' based on water mask.

Bugfixes:

* Fixed bug in LUT file assertion.
* Replaced pandas xlrd dependency by openpyxl.


0.15.5 (2021-01-21)
-------------------

New features:

* Improved handling of clear and cloudy fraction. Additional logger warnings and infos are now printed.

Bugfixes:

* Fixed Qhull error within water vapor retrieval, which occurred while processing extremely cloudy images.


0.15.4 (2021-01-13)
-------------------

New features:

* Improved consistency in the logging of ECMWF errors within ac_gms().
* Default values and units for multispectral AC are now printed to the logs.

Bugfixes:

* Deprecated raise of assertion error in case the LUT file only represents an LFS pointer.
* Fixed "RuntimeWarning: overflow encountered in reduce" within ac_gms().
* Implemented CWV default value for AC of Landsat data in case no ECMWF data are available.


0.15.3 (2020-11-12)
-------------------

New features:

* Separated CI Jobs for optionally testing AC of EnMAP and/or Sentinel-2 data.

Bugfixes:

* Fixed Qhull error caused by scipy griddata function in except clause of ac_interpolation.
* Fixed error in getting ECMWF data.
* Modified input points and values for scipy RegularGridInterpolator to avoid NaN in interpolated variable.


0.15.2 (2020-10-22)
-------------------

New features:

* New handling of Sentinel-2 and Landsat-8 options files.

Bugfixes:

* Improved multispectral AC tables download during runtime by implementing an automatic check for table availability.


0.15.1 (2020-10-16)
-------------------

New features:

* Re-enabled and updated CI job for testing AC of Sentinel-2 data.

Bugfixes:

* Fixed scipy QHull error in interpolation function within Sentinel-2 AC.
* Updated package requirements.


0.15.0 (2020-10-12)
-------------------

New features:

* SICOR is now available as conda package on conda-forge.


0.14.6 (2020-10-05)
-------------------

New features:

* All needed AC tables both for hyper- and multispectral mode are now downloaded during runtime
* 'deploy_pypi' CI job is finally working after fixing some bugs.

Bugfixes:

* Fixed documentation links.
* Fixed pip install error caused by basemap library.


0.14.5 (2020-09-23)
-------------------

New features:

* Additional tables for multispectral mode are now downloaded during pip install.

Bugfixes:

* Moved imports of scikit-image from module level to function level to avoid
  'ImportError: dlopen: cannot load any more object with static TLS'.
* Fixed DeprecationWarnings h), i), and j) from issue #53.


0.14.4 (2020-09-07)
-------------------

New features:

* AC LUT is now downloaded during setup.py.

Bugfixes:

* Fixed issue #62 (ecmwf-api-client ImportError after following the installation instructions for the hyperspectral
  part of SICOR).


0.14.3 (2020-09-02)
-------------------

New features:

* The package is now available on the Python Package Index.
* Added 'deploy_pypi' CI job.


0.14.2 (2020-05-14)
-------------------

New features:

* Segmentation of input radiance data cubes to enhance processing speed.
* Empirical line solution for extrapolating reflectance spectra based on segment averages.


0.14.1 (2019-02-18)
-------------------

New features:

* Optimal estimation for atmospheric and surface parameters.
* Calculation of retrieval uncertainties.


0.14.0 (2019-02-11)
-------------------

New features:

* New EnMAP atmospheric correction.
* 3 phases of water retrieval for hyperspectral data.


0.13.0 (2018-12-18)
-------------------

* Development by Niklas Bohn started.
