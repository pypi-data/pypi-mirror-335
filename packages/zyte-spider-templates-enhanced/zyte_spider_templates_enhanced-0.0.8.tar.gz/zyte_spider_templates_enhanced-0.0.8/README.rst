=====================
zyte-spider-templates
=====================

.. image:: https://img.shields.io/pypi/v/zyte-spider-templates.svg
   :target: https://pypi.python.org/pypi/zyte-spider-templates
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/zyte-spider-templates.svg
   :target: https://pypi.python.org/pypi/zyte-spider-templates
   :alt: Supported Python Versions

.. image:: https://github.com/zytedata/zyte-spider-templates/actions/workflows/test.yml/badge.svg
   :target: https://github.com/zytedata/zyte-spider-templates/actions/workflows/test.yml
   :alt: Automated tests

.. image:: https://codecov.io/github/zytedata/zyte-spider-templates/coverage.svg?branch=main
   :target: https://codecov.io/gh/zytedata/zyte-spider-templates
   :alt: Coverage report


.. description starts

Spider templates for automatic crawlers.

This library contains Scrapy_ spider templates. They can be used out of the box
with the Zyte features such as `Zyte API`_ or modified to be used standalone.
There is a `sample Scrapy project`_ for this library that you can use as a
starting point for your own projects.

.. _Scrapy: https://docs.scrapy.org/
.. _Zyte API: https://docs.zyte.com/zyte-api/get-started.html
.. _sample Scrapy project: https://github.com/zytedata/zyte-spider-templates-project

.. description ends

* Documentation: https://zyte-spider-templates.readthedocs.io/en/latest/
* License: BSD 3-clause

URL Metadata Feature
-------------------

Spiders now support attaching metadata to URLs that will be preserved and output with the scraped data. 
This is useful for tracking the source of data or adding context to the scraped results.

To use this feature:

1. When using a URL file (``urls_file`` parameter), include a second column with JSON metadata or plain text:

   .. code-block:: text

      https://example.com/product1  {"category": "electronics", "source": "campaign1"}
      https://example.com/product2  {"category": "books", "source": "campaign2"}

2. The metadata will be automatically attached to the items yielded by the spider in the ``url_metadata`` field.

This metadata is automatically preserved through the crawling process and included in the output.
