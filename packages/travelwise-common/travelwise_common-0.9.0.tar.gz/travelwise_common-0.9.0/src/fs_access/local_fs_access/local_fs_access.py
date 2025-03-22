import glob
import os
from contextlib import contextmanager
from typing import IO

from fs_access.base_fs_access import BaseFSAccess


class LocalFSAccess(BaseFSAccess):
    def get_file_paths(self, directory: str, file_type: str) -> list[str]:
        return glob.glob(
            os.path.join(directory, "**", f"*.{file_type.lower()}"),
            recursive=True,
        )

    @contextmanager
    def open(self, path: str, mode: str = "r") -> IO:
        with open(path, mode) as f:
            yield f
