import pickle
import os

SAVE_FILE = "sample.dat"

def clear_screen():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

# Read an integer from the user, returning None if the input is not a number
def read_int(prompt):
    value = input(prompt).strip()
    try:
        return int(value)
    except ValueError:
        return None

# Create a class called File that creates a logical file in the program
class File:
    # Initialize the file with its name
    def __init__(self, file_name, parent):
        self.file_name = file_name
        self.content = ""
        self.parent = parent

# Create a class of directory that acts as a node in a tree structure
class Directory:
    # Initialize the directory with its name
    def __init__(self, dir_name, parent):
        self.dir_name = dir_name
        self.children = dict()
        self.parent = parent

# Create a class that manages read and write operations on files
class OpenFile:
    MODES = ("r", "w", "a")

    # Initialize the object with file and mode
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode
        self.pos = 0
        # Append mode continues from current position
        if self.mode == "a":
            self.pos = len(self.file.content)
        # Write mode starts from the beginning and overrites the content
        elif self.mode == "w":
            self.file.content = ""

    # Check that the file is open in one of the given modes
    def _check_mode(self, modes, action):
        if self.mode is None:
            print("File is closed")
            return False
        if self.mode not in modes:
            print(f"File not open for {action}")
            return False
        return True

    # Write to the file
    def write(self, content):
        if not self._check_mode(("w", "a"), "writing"):
            return
        self.file.content += content
        self.pos = len(self.file.content)

    # Write at a specific point in a file, overwriting what is there
    def write_at_pos(self, content, position):
        if not self._check_mode(("w", "a"), "writing"):
            return
        if position < 0 or position > len(self.file.content):
            print("Invalid position")
            return
        self.file.content = self.file.content[:position] + content + self.file.content[position + len(content):]
        # Update position
        self.pos = position + len(content)

    # Read from the file
    def read(self):
        if not self._check_mode(("r",), "reading"):
            return None
        return self.file.content

    # Read from a specific point in the file
    def read_portion(self, start, size):
        if not self._check_mode(("r",), "reading"):
            return None
        if start < 0 or start > len(self.file.content):
            print("Invalid start position")
            return None
        if size < 0:
            print("Invalid size")
            return None
        return self.file.content[start:start + size]

# Create a class for managing the whole file system
class FileSystem:
    # Initialize the file system with a root directory
    def __init__(self):
        self.root = Directory("/", None)
        self.current_dir = self.root

    # The current directory as a string, built from the tree
    @property
    def dir_string(self):
        names = []
        node = self.current_dir
        while node is not self.root:
            names.append(node.dir_name)
            node = node.parent
        return "/" + "".join(name + "/" for name in reversed(names))

    # Check that a name can be used for a file or directory
    @staticmethod
    def _valid_name(name):
        if name in ("", ".", "..") or "/" in name:
            print("Invalid name")
            return False
        return True

    # Walk a list of path segments starting from a directory
    def _walk(self, start, segments):
        node = start
        for segment in segments:
            if not isinstance(node, Directory):
                return None
            if segment == ".":
                continue
            elif segment == "..":
                if node.parent is not None:
                    node = node.parent
            elif segment in node.children:
                node = node.children[segment]
            else:
                return None
        return node

    # Split a path into its starting directory and segments
    def _split(self, path):
        start = self.root if path.startswith("/") else self.current_dir
        return start, [s for s in path.split("/") if s]

    # Find the file or directory at a path, or None
    def _resolve(self, path):
        start, segments = self._split(path)
        return self._walk(start, segments)

    # Find the directory containing the last segment of a path and that segment's name
    def _resolve_parent(self, path):
        start, segments = self._split(path)
        if not segments:
            return None, None
        parent = self._walk(start, segments[:-1])
        if not isinstance(parent, Directory):
            print("Directory not found")
            return None, None
        return parent, segments[-1]

    # Find the file at a path
    def _resolve_file(self, path):
        node = self._resolve(path)
        if isinstance(node, File):
            return node
        print("File not found")
        return None

    # Find the directory at a path
    def _resolve_dir(self, path):
        node = self._resolve(path)
        if isinstance(node, Directory):
            return node
        print("Directory not found")
        return None

    # Create a new node at a path, rejecting invalid or duplicate names
    def _create(self, path, node_class):
        parent, name = self._resolve_parent(path)
        if parent is None:
            if name is None:
                print("Invalid name")
            return
        if not self._valid_name(name):
            return
        if name in parent.children:
            print(f"'{name}' already exists")
            return
        parent.children[name] = node_class(name, parent)

    # Create a new file
    def create_file(self, path):
        self._create(path, File)

    # Create a new directory
    def create_directory(self, path):
        self._create(path, Directory)

    # Change the current directory to the specified directory
    def change_directory(self, path):
        new_dir = self._resolve_dir(path)
        if new_dir is not None:
            self.current_dir = new_dir

    # List the contents of the current directory
    def list_directory(self):
        for name, entity in self.current_dir.children.items():
            if isinstance(entity, Directory):
                print(f"Directory: {name}")
            elif isinstance(entity, File):
                print(f"File: {name}")

    # Go back to parent directory
    def go_back(self):
        if self.current_dir is self.root:
            print("Already at root directory")
        else:
            self.current_dir = self.current_dir.parent

    # Move file to previous directory
    def move_back(self, path):
        if self.current_dir is self.root:
            print("Already at root directory")
            return
        self.move_file(path, "..")

    # Delete a file
    def delete_file(self, path):
        file = self._resolve_file(path)
        if file is not None:
            file.parent.children.pop(file.file_name)

    # Delete a directory, calling confirm() first if it is not empty
    def delete_dir(self, path, confirm=None):
        directory = self._resolve_dir(path)
        if directory is None:
            return
        if directory is self.root:
            print("Cannot delete root directory")
            return
        # Deleting a directory containing the current one would leave us inside a detached subtree
        node = self.current_dir
        while node is not None:
            if node is directory:
                print("Cannot delete the current directory or one of its parents")
                return
            node = node.parent
        if directory.children and confirm is not None and not confirm():
            return
        directory.parent.children.pop(directory.dir_name)

    # Move a file into another directory
    def move_file(self, path, dest_path):
        file = self._resolve_file(path)
        if file is None:
            return
        dest = self._resolve_dir(dest_path)
        if dest is None:
            return
        if dest is file.parent:
            return
        if file.file_name in dest.children:
            print(f"'{file.file_name}' already exists in destination")
            return
        file.parent.children.pop(file.file_name)
        dest.children[file.file_name] = file
        file.parent = dest

    # Open a file
    def open_file(self, path, mode):
        if mode not in OpenFile.MODES:
            print("Invalid mode")
            return None
        file = self._resolve_file(path)
        if file is None:
            return None
        return OpenFile(file, mode)

    # Close file
    def close_file(self, file):
        if isinstance(file, OpenFile):
            file.mode = None
        else:
            print("Invalid file object")

    # Print the current directory as a string
    def print_dir(self):
        print("Current Dir: " + self.dir_string)

# Load the saved file system, or start a new one
def load():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Could not load {SAVE_FILE} ({e}), starting with an empty file system")
            input("Press Enter to continue...")
    return FileSystem()

# Save the file system
def save(fs):
    with open(SAVE_FILE, "wb") as f:
        pickle.dump(fs, f)

# Menu for working with an open file, until it is closed
def file_menu(fs, file):
    while True:
        clear_screen()
        if file.mode == "r":
            print("1. Read")
            print("2. Read portion")
            print("3. Close")
            choice = read_int("Enter choice: ")
            if choice == 1:
                content = file.read()
                if content is not None:
                    print(content)
            elif choice == 2:
                start = read_int("Enter start position: ")
                size = read_int("Enter size: ")
                if start is None or size is None:
                    print("Please enter numbers")
                else:
                    content = file.read_portion(start, size)
                    if content is not None:
                        print(content)
            elif choice == 3:
                fs.close_file(file)
                break
            else:
                print("Invalid choice")
        else:
            print("1. Write")
            print("2. Write at position")
            print("3. Close")
            choice = read_int("Enter choice: ")
            if choice == 1:
                content = input("Enter content: ")
                file.write(content)
            elif choice == 2:
                content = input("Enter content: ")
                position = read_int("Enter position: ")
                if position is None:
                    print("Please enter a number")
                else:
                    file.write_at_pos(content, position)
            elif choice == 3:
                fs.close_file(file)
                break
            else:
                print("Invalid choice")
        input("Press Enter to continue...")

# The main menu loop
def main_menu(fs):
    while True:
        # User menu
        clear_screen()
        fs.print_dir()
        print()
        fs.list_directory()
        print()
        print("1. Create File")
        print("2. Create Directory")
        print("3. Change Directory")
        print("4. Go Back")
        print("5. Delete File")
        print("6. Delete Directory")
        print("7. Move File")
        print("8. Move File to Parent Directory")
        print("9. Open File")
        print("10. Exit")
        choice = read_int("Enter choice: ")
        if choice == 1:
            fs.create_file(input("Enter file path: "))
        elif choice == 2:
            fs.create_directory(input("Enter directory path: "))
        elif choice == 3:
            fs.change_directory(input("Enter directory path: "))
        elif choice == 4:
            fs.go_back()
        elif choice == 5:
            fs.delete_file(input("Enter file path: "))
        elif choice == 6:
            path = input("Enter directory path: ")
            fs.delete_dir(path, lambda: input("Directory is not empty, delete it and its contents? (y/N): ").strip().lower() == "y")
        elif choice == 7:
            file_path = input("Enter file path: ")
            dest_path = input("Enter destination directory path: ")
            fs.move_file(file_path, dest_path)
        elif choice == 8:
            fs.move_back(input("Enter file path: "))
        elif choice == 9:
            file_path = input("Enter file path: ")
            mode = input("Enter mode(r,w,a): ").strip()
            file = fs.open_file(file_path, mode)
            if file is not None:
                file_menu(fs, file)
        elif choice == 10:
            break
        else:
            print("Invalid choice")
        input("Press Enter to continue...")

# The main code
if __name__ == "__main__":
    fs = load()
    try:
        main_menu(fs)
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        # Save data before exiting
        save(fs)
