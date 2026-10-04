class FileSystemError(Exception):
    """Raised when a file system operation cannot be carried out."""


class DirectoryNotEmptyError(FileSystemError):
    """Raised when deleting a non-empty directory without `recursive=True`."""
