import pickle
import os

def clear_screen():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

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
# Create a class that manages read and write operations on files
class OpenFile:
    # Initialize the file with name and mode
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode
        self.pos = None
        if self.mode == "a":
            self.pos = len(self.file.content)
        elif self.mode == "w":
            self.file.content = ""
            self.pos = 0

    # Write to the file
    def write(self, content):
        if self.mode == "w":
            self.file.content += content
            self.pos += len(content)
        elif self.mode == "a":
            self.file.content += content
            self.pos += len(content)
        else:
            print("File not open for writing")

    # Write at a specific point in a file
    def write_at_pos(self, content, position):
        if self.mode == "w" or self.mode == "a":
            if position < 0:
                print("Invalid position")
            elif position > len(self.file.content):
                self.file.content += content
            elif len(self.file.content) < position + len(content):
                self.file.content = self.file.content[:position] + content
            else:
                self.file.content = self.file.content[:position] + content + self.file.content[position + len(content):]
        else:
            print("File not open for writing")

    # Read from the file
    def read(self):
        if self.mode == "r":
            return self.file.content
        else:
            print("File not open for reading")
    
    # Read from a specific point in the file
    def read_portion(self, start, size):
        if self.mode == "r":
            if start < 0 or start >= len(self.file.content):
                print("Invalid start position")
            elif start + size > len(self.file.content):
                return self.file.content[start:]
            else:
                return self.file.content[start:start + size]
        else:
            print("File not open for reading")

# Create a class for managing the whole file system
class FileSystem:
    # Initialize the file system with a root directory
    def __init__(self):
        self.root = Directory("/", None)
        self.current_dir = self.root
        self.dir_string = "/"
    
    # Create a new file in the current directory
    def create_file(self, file_name):
        new_file = File(file_name, self.current_dir)
        self.current_dir.children[file_name] = new_file

    # Create a new directory in the current directory
    def create_directory(self, dir_name):
        new_dir = Directory(dir_name, self.current_dir)
        self.current_dir.children[dir_name] = new_dir

    # Change the current directory to the specified directory
    def change_directory(self, dir_name):
        # children list is a dictionary
        if dir_name in self.current_dir.children and isinstance(self.current_dir.children[dir_name], Directory):
            self.current_dir = self.current_dir.children[dir_name]
            self.dir_string += dir_name + "/"
        else: 
            print("Directory not found")

    # List the contents of the current directory
    def list_directory(self):
        for name, entity in self.current_dir.children.items():
            if isinstance(entity, Directory):
                print(f"Directory: {name}")
            elif isinstance(entity, File):
                print(f"File: {name}")

    # Go back to parent directory
    def go_back(self):
        if self.current_dir == self.root:
            print("Already at root directory")
        else:
            self.current_dir = self.current_dir.parent
            self.dir_string = self.dir_string[:self.dir_string.rfind("/", 0, len(self.dir_string) - 1) + 1]
    
    # Move file to previous directory
    def move_back(self, file_name):
        if file_name in self.current_dir.children and isinstance(self.current_dir.children[file_name], File):
            parent_dir = self.current_dir.parent
            parent_dir.children[file_name] = self.current_dir.children[file_name]
            self.current_dir.children.pop(file_name)
        else:
            print("File not found")
 

    # Delete a file
    def delete_file(self, file_name):
        if file_name in self.current_dir.children and isinstance(self.current_dir.children[file_name], File):
            self.current_dir.children.pop(file_name)
        else:
            print("File not found")
            
    # Delete a directory
    def delete_dir(self, dir_name):
        if dir_name in self.current_dir.children and isinstance(self.current_dir.children[dir_name], Directory):
            self.current_dir.children.pop(dir_name)
        else:
            print("Directory not found")
            
    # Move a file
    def move_file(self, file_name, new_dir):
        if file_name in self.current_dir.children and isinstance(self.current_dir.children[file_name], File):
            if new_dir in self.current_dir.children and isinstance(self.current_dir.children[new_dir], Directory):
                self.current_dir.children[new_dir].children[file_name] = self.current_dir.children[file_name]
                self.current_dir.children.pop(file_name)
            else:
                print("Directory not found")
        else:
            print("File not found")

    # Open a file
    def open_file(self, file_name, mode):
        if file_name in self.current_dir.children and isinstance(self.current_dir.children[file_name], File):
            return OpenFile(self.current_dir.children[file_name], mode)
        else:
            print("File not found")

    # Close file
    def close_file(self, file):
        if isinstance(file, OpenFile):
            file = None
        else:
            print("Invalid file object")
    
    def print_dir(self):
        print("Current Dir: " + self.dir_string)
    
# The main code
if __name__ == "__main__":
    fs = FileSystem()
    while (True): 
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
        print("8. Move File to Parent Direcctory")
        print("9. Open File")
        print("10. Exit")
        choice = input("Enter choice: ")
        # If choice is a number
        if choice.isdigit():
            choice = int(choice)
        else:
            choice = 0
        if choice == 1:
            file_name = input("Enter file name: ")
            fs.create_file(file_name)
        elif choice == 2:
            dir_name = input("Enter directory name: ")
            fs.create_directory(dir_name)
        elif choice == 3:
            dir_name = input("Enter directory name: ")
            fs.change_directory(dir_name)
        elif choice == 4:
            fs.go_back()
        elif choice == 5:
            file_name = input("Enter file name: ")
            fs.delete_file(file_name)
        elif choice == 6:
            dir_name = input("Enter directory name: ")
            fs.delete_dir(dir_name)
        elif choice == 7:
            file_name = input("Enter file name: ")
            new_dir = input("Enter new directory: ")
            fs.move_file(file_name, new_dir)
        elif choice == 8:
            file_name = input("Enter file name: ")
            fs.move_back(file_name)
        elif choice == 9:
            file_name = input("Enter file name: ")
            mode = input("Enter mode(r,w,a): ")
            file = fs.open_file(file_name, mode)
            if file and mode in ["r", "w", "a"]:
                while True:
                    clear_screen()
                    if file.mode == "r":
                        print("1. Read")
                        print("2. Read portion")
                        print("3. Close")
                        choice = input("Enter choice: ")
                        # If choice is a number
                        if choice.isdigit():
                            choice = int(choice)
                        else:
                            choice = 0
                        if choice == 1:
                            print(file.read())
                        elif choice == 2:
                            start = int(input("Enter start position: "))
                            size = int(input("Enter size: "))
                            print(file.read_portion(start, size))
                        elif choice == 3:
                            fs.close_file(file)
                            break
                    elif file.mode == "w" or file.mode == "a":
                        print("1. Write")
                        print("2. Write at position")
                        print("3. Close")
                        choice = int(input("Enter choice: "))
                        if choice == 1:
                            content = input("Enter content: ")
                            file.write(content)
                        elif choice == 2:
                            content = input("Enter content: ")
                            position = int(input("Enter position: "))
                            file.write_at_pos(content, position)
                        elif choice == 3:
                            fs.close_file(file)
                            break
                    input("Press Enter to continue...")
            else:
                print("Invalid file or mode")
        elif choice == 10:
            break
        else:
            print("Invalid choice")
        input("Press Enter to continue...")

