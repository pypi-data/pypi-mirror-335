# Copyright (c) 2024, InfinityQ Technology, Inc.

"""
TitanQ
======

The TitanQ SDK for Python. This package will let you use InfinityQ's solver named TitanQ.

Documentation
-------------

Documentation is available as docstrings.
See also: https://sdk.titanq.infinityq.io

License
-----------------------------

Apache Software License (Apache 2.0)

"""

# These symbols must be exposed by this lib
from ._model import fast_sum, fastSum, Model, OptimizeResponse, Precision, Target, Vtype
# S3Storage must be exposed to the end user if they wish to use s3 buckets
from ._storage import S3Storage

# logger config
import logging as _logging
_logging.getLogger("TitanQ").addHandler(_logging.NullHandler())

__version__ = 'v0.31.0'