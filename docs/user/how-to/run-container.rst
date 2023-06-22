Run in a container
==================

Pre-built containers with jungfrau_commissioning and its dependencies already
installed are available on `Github Container Registry
<https://ghcr.io/dperl-dls/jungfrau_commissioning>`_.

Starting the container
----------------------

To pull the container from github container registry and run::

    $ docker run ghcr.io/dperl-dls/jungfrau_commissioning:main --version

To get a released version, use a numbered release instead of ``main``.
