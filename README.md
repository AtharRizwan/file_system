# file_system

An in-memory file system simulator with an interactive terminal menu. You can create, navigate, move and delete files and directories, and open files to read or write them. Everything is saved to a JSON file when you exit.

## Running

Requires Python 3.8 or later. There are no dependencies.

    python3 main.py

## Menu

| Option | What it does |
|---|---|
| 1. Create File | Create an empty file at a path |
| 2. Create Directory | Create a directory at a path |
| 3. Change Directory | Move to another directory |
| 4. Go Back | Move to the parent directory |
| 5. Delete File | Delete a file |
| 6. Delete Directory | Delete a directory, asking first if it is not empty |
| 7. Move File | Move a file into another directory |
| 8. Move File to Parent Directory | Move a file into the parent of the current directory |
| 9. Open File | Open a file to read or write it (see below) |
| 10. Exit | Save and quit |

### Paths

Anywhere a name is asked for, you can give a path:

- Absolute: `/projects/notes/todo`
- Relative to the current directory: `notes/todo`, `../other`
- `.` is the current directory and `..` is its parent.

Files and directories in the same directory share one namespace, so a file and a directory cannot have the same name. Names cannot be empty, contain `/`, or be `.` or `..`.

### Opening files

| Mode | Meaning |
|---|---|
| `r` | Read the whole file, or a portion from a start position |
| `w` | Clear the file, then write to it |
| `a` | Write to the end of the existing content |

In `w` and `a` modes, "Write at position" overwrites text starting at a position, extending the file if needed.

## Saving

The file system is saved to `filesystem.json` next to `main.py` when you exit, whether through option 10, Ctrl+C or the end of piped input. To use a different file, set `FS_SAVE_FILE`:

    FS_SAVE_FILE=/tmp/scratch.json python3 main.py

If the save file cannot be read, it is renamed to `filesystem.json.corrupt`, and the program starts with an empty file system.

## Project layout

```
main.py                 entry point
filesystem/
  models.py             File, Directory and the OpenFile handle
  filesystem.py         FileSystem: path resolution and operations
  storage.py            JSON save and load
  cli.py                interactive menus
  errors.py             FileSystemError
```

`filesystem` can also be used as a library:

```python
from filesystem import FileSystem

fs = FileSystem()
fs.create_directory("docs")
fs.create_file("docs/readme")
handle = fs.open_file("docs/readme", "w")
handle.write("hello")
handle.close()
```
