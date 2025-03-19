# Copyright (c) 2024, InfinityQ Technology, Inc.
from dataclasses import dataclass
from typing import Optional

from titanq.errors import MpsMalformedFileError


@dataclass
class MPSParseOptions:

    skip_empty_lines: Optional[bool] = False
    """Will skip empty lines found inside the .mps file"""

    def empty_line_check(self, index: int, content: str) -> bool:
        """
        return a boolean value if it should skip the line or not.
        If skip_empty_lines is not raised, it will raise an error instead

        :param index: line index we are checking to skip or not
        :param conent: content of the line

        :raises: MPSMalormedFile if the line is empty and the flag is not raised
        """
        if not self.skip_empty_lines and not content:
            raise MpsMalformedFileError(
                f"Line number '{index}' in the .mps file is empty, use 'skip_empty_lines' as an option to ignore"
            )
        return self.skip_empty_lines and not content # skip only if flag set and it's empty