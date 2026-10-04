"""Saving and loading a FileSystem as JSON."""

from __future__ import annotations

import json
import os
from typing import Any

from .errors import FileSystemError
from .filesystem import FileSystem
from .models import Directory, File, Node

FORMAT_VERSION = 1


def _node_to_dict(node: Node) -> dict[str, Any]:
    if isinstance(node, File):
        return {"type": "file", "name": node.name, "content": node.content}
    return {
        "type": "dir",
        "name": node.name,
        "children": [_node_to_dict(child) for child in node.children.values()],
    }


def _node_from_dict(data: dict[str, Any], parent: Directory) -> Node:
    kind, name = data["type"], data["name"]
    if not isinstance(name, str) or not name or "/" in name or name in (".", ".."):
        raise ValueError(f"invalid name {name!r}")
    if kind == "file":
        content = data["content"]
        if not isinstance(content, str):
            raise ValueError(f"invalid content for {name!r}")
        return File(name, parent, content)
    if kind == "dir":
        directory = Directory(name, parent)
        _load_children(directory, data["children"])
        return directory
    raise ValueError(f"unknown node type {kind!r}")


def _load_children(directory: Directory, children: list[dict[str, Any]]) -> None:
    for child_data in children:
        child = _node_from_dict(child_data, directory)
        if child.name in directory.children:
            raise ValueError(f"duplicate name {child.name!r}")
        directory.children[child.name] = child


def to_dict(fs: FileSystem) -> dict[str, Any]:
    root = _node_to_dict(fs.root)
    return {"version": FORMAT_VERSION, "cwd": fs.cwd, "root": root["children"]}


def from_dict(data: dict[str, Any]) -> FileSystem:
    fs = FileSystem()
    _load_children(fs.root, data["root"])
    try:
        fs.change_directory(data.get("cwd", "/"))
    except FileSystemError:
        fs.change_directory("/")
    return fs


def save(fs: FileSystem, path: str) -> None:
    """Write `fs` to `path`, replacing the old file only once the new one is complete."""
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(to_dict(fs), f, indent=2)
    os.replace(tmp_path, path)


def load(path: str) -> FileSystem:
    """Load a file system from `path`, or return an empty one if it does not exist."""
    if not os.path.exists(path):
        return FileSystem()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("version") != FORMAT_VERSION:
            raise ValueError(f"unsupported version {data.get('version')!r}")
        return from_dict(data)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise FileSystemError(f"Could not load {path}: {e}") from e
