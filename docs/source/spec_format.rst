.. format of spec file

Specification Files
=====================================================
defines
-----------
Defines files are expected to exist in ``:/autobuild/``. ``defines`` files are usually
processed by ``autobuild`` script, however ``acbs`` also use this file to determine
the building order of a given set of packages.

``defines`` file MUST contain the following variables:

* ``PKGNAME`` The name of the package
* ``PKGSEC``  The section/group/"genre" of the package
* ``PKGDES``  The brief description of the package

This file may also include the following variables:

* ``PKGDEP``   The mandatory runtime requirements/dependencies
* ``BUILDDEP`` The mandatory compile-time requirements/dependencies
* ``PKGRECOM`` The optional runtime requirements/dependencies (for enhancing UX or add new features)
* ``EPOCH``    The epoch version number of the package

This file might also include ``autobuild`` specific controlling values.
Consult Autobuild3_ for more information.

spec
-----------
Defines files are expected to exist in ``:/`` (root of the top project folder).
``defines`` files are solely processed by ``acbs`` to fetch source files and control
``acbs`` how to transfer controls to ``autobuild``.

``spec`` file MUST contain the following variables:

* ``VER``  The version of the package, it might be not in semantic versioning scheme.

``spec`` file SHOULD ONLY contain ONE of the following variables:

* ``DUMMYSRC`` (Bool)   If set to 1, indicates this package does not require source files or source files processing cannot be handled well by current version of ``acbs``.
* ``SRCTBL``   (String) If set, indicates this package requires "zipped" or archived source files.
* ``<VCS_NAME>SRC``     If set, indicates required source files for this package are in a version controlled repository. (For a list of supported VCS systems, see :doc:`appendix`)

``spec`` file may also contain the following variables:

* ``<VCS_NAME>BRCH``    If set, indicates required branch of the repository for the package.
* ``<VCS_NAME>COMMIT``  If set, indicates required commit/revision of the repository for the package.
* ``CHKSUM`` Expected format: ``<ALGO_NAME>::<HASH_VALUE>`` If set, ``acbs`` will check the checksum of the source file against this value not available if the source is from VCS.
* ``SUBDIR`` If set, ``acbs`` will change to specified directory after finishing preparing the source files. (For a list of supported hashing algorithms, see :doc:`appendix`)

Upcoming, drafted, not yet implemented in current version:

* ``SRCS`` Expected format: ``(<VCS_NAME_1>::<URI_1> <VCS_NAME_2>::<URI_2> ...)`` See the footnote below for more information [1]_
* ``CHKSUMS`` Expected format: ``(<ALGO_NAME_1>::<HASH_VALUE_1> <ALGO_NAME_2>::<HASH_VALUE_2> ...)`` If set, ``acbs`` will check the checksum of the source files against this value not available if the source is from VCS. [2]_

.. _Autobuild3: https://github.com/AOSC-Dev/aosc-os-abbs/wiki/Autobuild3
.. [1] Example: ``SRCS=('git::git://github.com/AOSC-Dev/acbs' 'git::https://github.com/AOSC-Dev/acbs')`` This will make ``acbs`` to download two sets of source files
.. [2] Example: ``CHKSUMS=('sha1::a9c55882c935300bec93e209f1ec8a21f75638b7' 'sha256::4ccdbbd95d4aef058502c8ee07b1abb490f5ef4a4d6ff711440facd0b8eded33')`` This will make ``acbs`` to check two sets of source files
