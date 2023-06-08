jungfrau_commissioning
===========================

|code_ci| |docs_ci| |coverage| |pypi_version| |license|

Simple tools using the Bluesky framework for comissioning the Jungfrau detector

============== ==============================================================
PyPI           ``pip install jungfrau_commissioning``
Source code    https://github.com/dperl-dls/jungfrau_commissioning
Documentation  https://dperl-dls.github.io/jungfrau_commissioning
Releases       https://github.com/dperl-dls/jungfrau_commissioning/releases
============== ==============================================================

To setup the environment, please run:

    $ ./setup_environment.sh

Running main starts an ipython terminal with imported ophyd devices and plans ready to run:

    $ python -m jungfrau_commissioning 

To explore and edit the code for this project and the associated dodal repository at once:

    $ module load vscode
    $ code .vscode/jungfrau_commissioning.code-workspace


.. |code_ci| image:: https://github.com/dperl-dls/jungfrau_commissioning/actions/workflows/code.yml/badge.svg?branch=main
    :target: https://github.com/dperl-dls/jungfrau_commissioning/actions/workflows/code.yml
    :alt: Code CI

.. |docs_ci| image:: https://github.com/dperl-dls/jungfrau_commissioning/actions/workflows/docs.yml/badge.svg?branch=main
    :target: https://github.com/dperl-dls/jungfrau_commissioning/actions/workflows/docs.yml
    :alt: Docs CI

.. |coverage| image:: https://codecov.io/gh/dperl-dls/jungfrau_commissioning/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/dperl-dls/jungfrau_commissioning
    :alt: Test Coverage

.. |pypi_version| image:: https://img.shields.io/pypi/v/jungfrau_commissioning.svg
    :target: https://pypi.org/project/jungfrau_commissioning
    :alt: Latest PyPI version

.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://opensource.org/licenses/Apache-2.0
    :alt: Apache License

..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

See https://dperl-dls.github.io/jungfrau_commissioning for more detailed documentation.
