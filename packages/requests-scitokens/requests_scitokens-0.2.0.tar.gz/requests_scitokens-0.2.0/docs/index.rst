##################
requests-scitokens
##################

.. toctree::
   :hidden:

   Home <self>

`requests-scitokens` provides an authentication plugin for
`Requests <http://requests.readthedocs.io/>`__ that handles attaching
`SciTokens <https://scitokens.org>`__ to HTTP requests.

.. image:: https://badge.fury.io/py/requests-scitokens.svg
    :target: http://badge.fury.io/py/requests-scitokens
    :alt: requests-scitokens PyPI version badge
.. image:: https://img.shields.io/conda/vn/conda-forge/requests-scitokens.svg
    :target: https://anaconda.org/conda-forge/requests-scitokens/
    :alt: requests-scitokens conda-forge badge


.. raw:: html

    <br/>

.. image:: https://img.shields.io/pypi/l/requests-scitokens.svg
    :target: https://choosealicense.com/licenses/apache-2.0/
    :alt: requests-scitokens license badge
.. image:: https://img.shields.io/pypi/pyversions/requests-scitokens.svg
    :alt: Supported Python versions badge

.. raw:: html

    <br/>

.. image:: https://git.ligo.org/computing/software/requests-scitokens/badges/main/pipeline.svg
    :alt: Build status
    :target: https://git.ligo.org/computing/software/requests-scitokens/-/pipelines
.. image:: https://git.ligo.org/computing/software/requests-scitokens/badges/main/coverage.svg
    :alt: Code coverage
.. image:: https://readthedocs.org/projects/requests-scitokens/badge/?version=latest
    :alt: Documentation Status
    :target: https://requests-scitokens.readthedocs.io/en/latest/?badge=latest

============
Installation
============

.. tab-set::

    .. tab-item:: Conda

        .. code-block:: bash

            conda install -c conda-forge requests-scitokens

    .. tab-item:: Debian Linux

        .. code-block:: bash

            apt-get install python3-requests-scitokens

        See the IGWN Computing Guide software repositories entry for
        `Debian <https://computing.docs.ligo.org/guide/software/debian/>`__
        for instructions on how to configure the required
        IGWN Debian repositories.

    .. tab-item:: Enterprise Linux

        .. code-block:: bash

            dnf install python3-requests-scitokens

        See the IGWN Computing Guide software repositories entries for
        `Rocky Linux 8 <https://computing.docs.ligo.org/guide/software/rl8/>`__ or
        `Rocky Linux 9 <https://computing.docs.ligo.org/guide/software/rl9/>`__
        for instructions on how to configure the required IGWN RPM repositories.

    .. tab-item:: Pip

        .. code-block:: bash

            python -m pip install requests-scitokens

====================================
``requests-scitokens`` documentation
====================================

.. automodapi:: requests_scitokens
    :no-heading:
    :headings: -~
