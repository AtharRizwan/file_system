"""The file system tree and the operations on it."""

from __future__ import annotations

from typing import Optional

from .errors import DirectoryNotEmptyError, FileSystemError
from .models import Directory, File, Node, OpenFile


class FileSystem:
    """An in-memory file system.

    Every operation takes a path, either absolute (`/a/b`) or relative to the
    current directory, and may use `.` and `..`.
    """

    def __init__(self) -> None:
        self.root = Directory("/", None)
        self.current_dir = self.root

    @property
    def cwd(self) -> str:
        """The current directory as a path string, e.g. `/a/b/`."""
        return self.path_of(self.current_dir)

    def path_of(self, node: Node) -> str:
        is_dir = isinstance(node, Directory)
        names = []
        while node is not self.root:
            names.append(node.name)
            node = node.parent
        path = "/" + "/".join(reversed(names))
        if is_dir and names:
            path += "/"
        return path

    # Path resolution

    @staticmethod
    def _validate_name(name: str) -> None:
        if name in ("", ".", "..") or "/" in name:
            raise FileSystemError(f"Invalid name '{name}'")

    def _split(self, path: str) -> tuple[Directory, list[str]]:
        start = self.root if path.startswith("/") else self.current_dir
        return start, [s for s in path.split("/") if s]

    @staticmethod
    def _walk(start: Directory, segments: list[str]) -> Optional[Node]:
        node: Node = start
        for segment in segments:
            if not isinstance(node, Directory):
                return None
            if segment == ".":
                continue
            if segment == "..":
                if node.parent is not None:
                    node = node.parent
            elif segment in node.children:
                node = node.children[segment]
            else:
                return None
        return node

    def _resolve(self, path: str) -> Optional[Node]:
        return self._walk(*self._split(path))

    def _resolve_parent(self, path: str) -> tuple[Directory, str]:
        """Resolve all but the last segment of `path` to a directory."""
        start, segments = self._split(path)
        if not segments:
            raise FileSystemError("Invalid name ''")
        parent = self._walk(start, segments[:-1])
        if not isinstance(parent, Directory):
            raise FileSystemError(f"Directory not found: {path}")
        return parent, segments[-1]

    def _resolve_file(self, path: str) -> File:
        node = self._resolve(path)
        if not isinstance(node, File):
            raise FileSystemError(f"File not found: {path}")
        return node

    def _resolve_dir(self, path: str) -> Directory:
        node = self._resolve(path)
        if not isinstance(node, Directory):
            raise FileSystemError(f"Directory not found: {path}")
        return node

    # Operations

    def _create(self, path: str, node_class: type) -> None:
        parent, name = self._resolve_parent(path)
        self._validate_name(name)
        if name in parent.children:
            raise FileSystemError(f"'{name}' already exists")
        parent.children[name] = node_class(name, parent)

    def create_file(self, path: str) -> None:
        self._create(path, File)

    def create_directory(self, path: str) -> None:
        self._create(path, Directory)

    def change_directory(self, path: str) -> None:
        self.current_dir = self._resolve_dir(path)

    def list_directory(self, path: str = ".") -> list[tuple[str, bool]]:
        """Return `(name, is_dir)` pairs, directories first, each group sorted by name."""
        directory = self._resolve_dir(path)
        entries = [(name, isinstance(node, Directory)) for name, node in directory.children.items()]
        return sorted(entries, key=lambda entry: (not entry[1], entry[0]))

    def delete_file(self, path: str) -> None:
        file = self._resolve_file(path)
        del file.parent.children[file.name]

    def delete_directory(self, path: str, recursive: bool = False) -> None:
        """Delete a directory. A non-empty one is deleted only if `recursive` is true."""
        directory = self._resolve_dir(path)
        if directory is self.root:
            raise FileSystemError("Cannot delete the root directory")
        node: Optional[Directory] = self.current_dir
        while node is not None:
            if node is directory:
                raise FileSystemError("Cannot delete the current directory or one of its parents")
            node = node.parent
        if directory.children and not recursive:
            raise DirectoryNotEmptyError(f"Directory not empty: {path}")
        del directory.parent.children[directory.name]

    def move_file(self, path: str, dest_path: str) -> None:
        file = self._resolve_file(path)
        dest = self._resolve_dir(dest_path)
        if dest is file.parent:
            return
        if file.name in dest.children:
            raise FileSystemError(f"'{file.name}' already exists in {self.path_of(dest)}")
        del file.parent.children[file.name]
        dest.children[file.name] = file
        file.parent = dest

    def open_file(self, path: str, mode: str) -> OpenFile:
        if mode not in OpenFile.MODES:
            raise FileSystemError(f"Invalid mode '{mode}', expected one of r, w, a")
        return OpenFile(self._resolve_file(path), mode)
