"""Tree nodes and the open-file handle."""

from __future__ import annotations

from typing import Optional

from .errors import FileSystemError


class Node:
    """A named entry in the tree with a link to its parent directory."""

    def __init__(self, name: str, parent: Optional[Directory]):
        self.name = name
        self.parent = parent


class File(Node):
    """A file holding text content."""

    def __init__(self, name: str, parent: Optional[Directory], content: str = ""):
        super().__init__(name, parent)
        self.content = content


class Directory(Node):
    """A directory whose children (files and directories) share one namespace."""

    def __init__(self, name: str, parent: Optional[Directory]):
        super().__init__(name, parent)
        self.children: dict[str, Node] = {}


class OpenFile:
    """A handle for reading (`r`), overwriting (`w`) or appending to (`a`) a file.

    Opening in `w` mode truncates the file immediately.
    """

    MODES = ("r", "w", "a")

    def __init__(self, file: File, mode: str):
        if mode not in self.MODES:
            raise FileSystemError(f"Invalid mode '{mode}', expected one of r, w, a")
        self.file = file
        self.mode: Optional[str] = mode
        self.pos = 0
        if mode == "w":
            file.content = ""
        elif mode == "a":
            self.pos = len(file.content)

    @property
    def closed(self) -> bool:
        return self.mode is None

    def close(self) -> None:
        self.mode = None

    def _require(self, modes: tuple, action: str) -> None:
        if self.closed:
            raise FileSystemError("File is closed")
        if self.mode not in modes:
            raise FileSystemError(f"File not open for {action}")

    def read(self) -> str:
        self._require(("r",), "reading")
        return self.file.content

    def read_portion(self, start: int, size: int) -> str:
        """Return up to `size` characters starting at `start`."""
        self._require(("r",), "reading")
        if start < 0 or start > len(self.file.content):
            raise FileSystemError("Invalid start position")
        if size < 0:
            raise FileSystemError("Invalid size")
        return self.file.content[start:start + size]

    def write(self, content: str) -> None:
        """Append `content` to the end of the file."""
        self._require(("w", "a"), "writing")
        self.file.content += content
        self.pos = len(self.file.content)

    def write_at_pos(self, content: str, position: int) -> None:
        """Overwrite the file starting at `position`, extending it if needed."""
        self._require(("w", "a"), "writing")
        text = self.file.content
        if position < 0 or position > len(text):
            raise FileSystemError("Invalid position")
        self.file.content = text[:position] + content + text[position + len(content):]
        self.pos = position + len(content)
