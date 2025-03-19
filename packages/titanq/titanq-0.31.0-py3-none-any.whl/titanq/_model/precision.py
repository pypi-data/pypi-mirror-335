# Copyright (c) 2024, InfinityQ Technology, Inc.
import enum

class Precision(str, enum.Enum):
    """
    All precision level supported by TitanQ.

    Use ``Precision.AUTO`` when you don't know which one to use.
    """

    AUTO = 'auto'
    STANDARD = 'standard'
    HIGH = 'high'

    def __str__(self) -> str:
        return str(self.value)
