.. image:: https://github.com/easybuilders/easybuild/raw/develop/logo/png/easybuild_logo_2022_horizontal_dark_bg_transparent.png
   :align: center
   :height: 400px

`EasyBuild <https://easybuild.io>`_ is a software build
and installation framework that allows you to manage (scientific) software
on High Performance Computing (HPC) systems in an efficient way.

The **easybuild-easyconfigs-archive** package provides a collection of old
*easyconfig files* for EasyBuild that have been archived from the main
**easybuild-easyconfigs** repository.

Easyconfig files are used to specify which software to build, which
version of the software (and its dependencies), which build parameters
to use (e.g., which compiler toolchain to use), etc.

The easyconfig files in this collection are provided as-is without any
warranties. In the past they were well-tested on a variety of systems, but this
might not longer be the case on modern systems.

The EasyBuild documentation is available at http://docs.easybuild.io/.

The easybuild-easyconfigs-archive package is hosted on GitHub. Given the
archival nature of this repository, no issue tracker for bug reports or feature
requests is provided. See https://github.com/easybuilders/easybuild-easyconfigs-archive.

Related Python packages:

* **easybuild-framework**

  * the EasyBuild framework, which includes the ``easybuild.framework`` and ``easybuild.tools`` Python
    packages that provide general support for building and installing software
  * GitHub repository: https://github.com/easybuilders/easybuild-framework
  * PyPi: https://pypi.python.org/pypi/easybuild-framework

* **easybuild-easyblocks**

  * a collection of easyblocks that implement support for building and installing (groups of) software packages
  * GitHub repository: https://github.com/easybuilders/easybuild-easyblocks
  * package on PyPi: https://pypi.python.org/pypi/easybuild-easyblocks

* **easybuild-easyconfigs**

  * a collection of example easyconfig files that specify which software to build,
    and using which build options; these easyconfigs will be well tested
    with the latest compatible versions of the easybuild-framework and easybuild-easyblocks packages
  * GitHub repository: https://github.com/easybuilders/easybuild-easyconfigs
  * PyPi: https://pypi.python.org/pypi/easybuild-easyconfigs
