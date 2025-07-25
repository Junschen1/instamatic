[![build](https://github.com/instamatic-dev/instamatic/actions/workflows/test.yml/badge.svg)](https://github.com/instamatic-dev/instamatic/actions/workflows/test.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/instamatic)](https://pypi.org/project/instamatic/)
[![PyPI](https://img.shields.io/pypi/v/instamatic.svg?style=flat)](https://pypi.org/project/instamatic/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1090388.svg)](https://doi.org/10.5281/zenodo.1090388)

![Instamatic banner](https://raw.githubusercontent.com/instamatic-dev/instamatic/main/docs/banner.png)

# Instamatic

Instamatic is a Python program that is being developed with the aim to automate the collection of electron diffraction data. At the core is a Python library for transmission electron microscope experimental control with bindings for the JEOL/FEI microscopes and interfaces to the ASI/TVIPS/Gatan cameras. Routines have been implemented for collecting serial electron diffraction (serialED), continuous rotation electron diffraction (cRED, aka 3D-ED / microED), and stepwise rotation electron diffraction (RED) data. For streaming cameras, instamatic includes a live-view GUI.

Instamatic is distributed via [pypi](https://pypi.org/project/instamatic) and https://github.com/instamatic-dev/instamatic/releases. However, the most up-to-date version of the code (including bugs!) is available from this repository.

Electron microscopes supported:

- JEOL microscopes with the TEMCOM library
- FEI microscopes via the scripting interface

Cameras supported:

- ASI Timepix
- ASI CheeTah through `serval-toolkit` library
- TVIPS cameras through EMMENU4 API
- Quantum Detectors MerlinEM
- (Gatan cameras through DM plugin [1])

Instamatic has been developed on a JEOL-2100 with a Timepix camera, and a JEOL-1400 and JEOL-3200 with TVIPS cameras (XF416/F416).

[1]: Support for Gatan cameras is somewhat underdeveloped. As an alternative, a DigitalMicrograph script for collecting cRED data on a OneView camera (or any other Gatan camera) can be found [here](https://github.com/instamatic-dev/InsteaDMatic).


## Installation

If you use conda, create a new environment:

```
conda create -n instamatic python=3.11
conda activate instamatic
```

Install using pip, works with python versions 3.7 or newer:

```bash
pip install instamatic
```

## OS requirement

The package requires Windows 7 or higher. It has been mainly developed and tested under windows 7 and higher.

## Package dependencies

Check [pypoject.toml](pypoject.toml) for the full dependency list and versions.

## Documentation

See [the documentation](https://instamatic.readthedocs.io) for how to set up and use Instamatic.
## Win_server update
To use the indexing server: XDS (Ubuntu in Windows), first ensure that Windows Subsystem for Linux 2 (WSL2) is installed. If not, refer to the official installation guide:
https://learn.microsoft.com/en-us/windows/wsl/install

Then ensure that XDS is installed in wsl2. If not, refer to the official installation guide:
https://wiki.uni-konstanz.de/xds/index.php/Installation
Please follow the linux guide and install the XDS package in wsl2.

Finally ensure that Shelxt is installed in wsl2. If not, refer to the official installation guide:
https://shelx.uni-goettingen.de/

Once all dependencies are downloaded, please download the exe file from [10.5281/zenodo.16018017](https://doi.org/10.5281/zenodo.16018017). Then place the file in the same directory as instamatic.exe. For example, if instamatic.exe is located in your_anaconda_directory\envs\instamatic\Scripts, put the newly downloaded exe file in the same your_anaconda_directory\envs\instamatic\Scripts directory.​
Next, you need to modify the configuration item in the settings.yaml file. This file is usually located in C:\Users****\AppData\Roaming\instamatic\config. However, if you can't find the file address, you can open instamatic and look for the config directory information that pops up. The path shown there will lead you to the location of the settings.yaml file. Once you've located the file, change the name of the configuration item following "Win_XDS_PATH:" in the settings.yaml file to the directory where xds was installed.

Finally, you can use the indexing server "XDS (Ubuntu in Windows)" in the advanced section of Instamatic. Note that the SMV file path sent to the autosolution server must not be located in your Ubuntu subsystem.
## Reference

If you found `Instamatic` useful, please consider citing it or one of the references below.

Each software release is archived on [Zenodo](https://zenodo.org), which provides a DOI for the project and each release. The project DOI [10.5281/zenodo.1090388](https://doi.org/10.5281/zenodo.1090388) will always resolve to the latest archive, which contains all the information needed to cite the release.

Alternatively, some of the methods implemented in `Instamatic` are described in:

- B. Wang, X. Zou, and S. Smeets, [Automated serial rotation electron diffraction combined with cluster analysis: an efficient multi-crystal workflow for structure determination](https://doi.org/10.1107/S2052252519007681), IUCrJ (2019). 6, 854-867

- B. Wang, [Development of rotation electron diffraction as a fully automated and accurate method for structure determination](http://www.diva-portal.org/smash/record.jsf?pid=diva2:1306254). PhD thesis (2019), Dept. of Materials and Environmental Chemistry (MMK), Stockholm University

- M.O. Cichocka, J. Ångström, B. Wang, X. Zou, and S. Smeets, [High-throughput continuous rotation electron diffraction data acquisition via software automation](http://dx.doi.org/10.1107/S1600576718015145), J. Appl. Cryst. (2018). 51, 1652–1661

- S. Smeets, X. Zou, and W. Wan, [Serial electron crystallography for structure determination and phase analysis of nanocrystalline materials](http://dx.doi.org/10.1107/S1600576718009500), J. Appl. Cryst. (2018). 51, 1262–1273

## Source Code Structure

* **`demos/`** - Jupyter demo notebooks
* **`docs/`** - Documentation
* **`src/`** - Source code for instamatic
* **`src/instamatic/`**
  * **`TEMController/`** - Microscope interaction code
  * **`calibrate/`** - Tools for calibration
  * **`camera/`** - Camera interaction code
  * **`config/`** - Configuration management
  * **`experiments/`** - Specific data collection routines
  * **`formats/`** - Image formats and other IO
  * **`gui/`** - GUI code
  * **`neural_network/`** - Crystal quality prediction
  * **`processing/`** - Data processing tools
  * **`server/`** - Manages interprocess/network communication
  * **`utils/`** - Helpful utilities
  * **`acquire_at_items.py`** - Stage movement/data acquisition engine
  * **`admin.py`** - Check for administrator
  * **`banner.py`** - Appropriately annoying thank you message
  * **`browser.py`** - Montage browsing class
  * **`exceptions.py`** - Internal exceptions
  * **`goniotool.py`** - Goniotool (JEOL) interaction code
  * **`gridmontage.py`** - Grid montage data collection code
  * **`image_utils.py`** - Image transformation routines
  * **`imreg.py`** - Image registration (cross correlation)
  * **`io.py`** - Some io-related scripts
  * **`main.py`** - Main entry point
  * **`montage.py`** - Image stitching
  * **`navigation.py`** - Optimize navigation paths
  * **`tools.py`** - Collection of functions used throughout the code
* **`scripts/`** - Helpful scripts
* **`pyproject.toml`** - Dependency/build system declaration
