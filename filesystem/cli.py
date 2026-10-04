"""The interactive menu."""

from __future__ import annotations

import os
from typing import Callable, Optional, Tuple

from . import storage
from .errors import DirectoryNotEmptyError, FileSystemError
from .filesystem import FileSystem
from .models import OpenFile

DEFAULT_SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "filesystem.json")

MenuItem = Tuple[str, Callable[[], Optional[bool]]]


def clear_screen() -> None:
    print("\033[2J\033[H", end="", flush=True)


def pause() -> None:
    input("Press Enter to continue...")


def read_int(prompt: str) -> int:
    value = input(prompt).strip()
    try:
        return int(value)
    except ValueError:
        raise FileSystemError(f"'{value}' is not a number") from None


def run_menu(header: Callable[[], None], items: list[MenuItem]) -> None:
    """Show `items` until a handler returns True. Errors from handlers are printed."""
    while True:
        clear_screen()
        header()
        for number, (label, _) in enumerate(items, start=1):
            print(f"{number}. {label}")
        choice = input("Enter choice: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(items):
            print("Invalid choice")
            pause()
            continue
        _, handler = items[int(choice) - 1]
        try:
            if handler():
                return
        except FileSystemError as e:
            print(e)
        pause()


def file_menu(file: OpenFile) -> None:
    def read() -> None:
        print(file.read())

    def read_portion() -> None:
        start = read_int("Enter start position: ")
        size = read_int("Enter size: ")
        print(file.read_portion(start, size))

    def write() -> None:
        file.write(input("Enter content: "))

    def write_at_pos() -> None:
        content = input("Enter content: ")
        file.write_at_pos(content, read_int("Enter position: "))

    def close() -> bool:
        file.close()
        return True

    if file.mode == "r":
        items: list[MenuItem] = [("Read", read), ("Read portion", read_portion), ("Close", close)]
    else:
        items = [("Write", write), ("Write at position", write_at_pos), ("Close", close)]
    run_menu(lambda: print(f"File: {file.file.name} (mode {file.mode})\n"), items)


def main_menu(fs: FileSystem) -> None:
    def header() -> None:
        print(f"Current Dir: {fs.cwd}\n")
        for name, is_dir in fs.list_directory():
            print(f"{'Directory' if is_dir else 'File'}: {name}")
        print()

    def go_back() -> None:
        if fs.current_dir is fs.root:
            raise FileSystemError("Already at root directory")
        fs.change_directory("..")

    def delete_directory() -> None:
        path = input("Enter directory path: ")
        try:
            fs.delete_directory(path)
        except DirectoryNotEmptyError:
            answer = input("Directory is not empty, delete it and its contents? (y/N): ")
            if answer.strip().lower() == "y":
                fs.delete_directory(path, recursive=True)

    def move_to_parent() -> None:
        if fs.current_dir is fs.root:
            raise FileSystemError("Already at root directory")
        fs.move_file(input("Enter file path: "), "..")

    def open_file() -> None:
        path = input("Enter file path: ")
        file_menu(fs.open_file(path, input("Enter mode (r, w, a): ").strip()))

    items: list[MenuItem] = [
        ("Create File", lambda: fs.create_file(input("Enter file path: "))),
        ("Create Directory", lambda: fs.create_directory(input("Enter directory path: "))),
        ("Change Directory", lambda: fs.change_directory(input("Enter directory path: "))),
        ("Go Back", go_back),
        ("Delete File", lambda: fs.delete_file(input("Enter file path: "))),
        ("Delete Directory", delete_directory),
        ("Move File", lambda: fs.move_file(input("Enter file path: "), input("Enter destination directory path: "))),
        ("Move File to Parent Directory", move_to_parent),
        ("Open File", open_file),
        ("Exit", lambda: True),
    ]
    run_menu(header, items)


def main(save_path: Optional[str] = None) -> None:
    save_path = save_path or os.environ.get("FS_SAVE_FILE") or DEFAULT_SAVE_FILE
    try:
        fs = storage.load(save_path)
    except FileSystemError as e:
        # Keep the unreadable file instead of overwriting it on exit.
        backup_path = save_path + ".corrupt"
        os.replace(save_path, backup_path)
        print(f"{e}\nIt was moved to {backup_path}. Starting with an empty file system.")
        pause()
        fs = FileSystem()
    try:
        main_menu(fs)
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        storage.save(fs, save_path)
