"""
file_utils.py

A utility module for managing file operations.
Provides methods to check for file existence, write, read, remove, rename,
move, and copy files.
Each method is documented with its purpose, parameters, and return values.
"""

import os
import shutil

from darca_exception.exception import DarcaException
from darca_log_facility.logger import DarcaLogger

from darca_file_utils.directory_utils import (
    DirectoryUtils,  # Importing directory utilities
)

# Initialize the logger
logger = DarcaLogger(name="file_utils").get_logger()


class FileUtilsException(DarcaException):
    """
    Custom exception for file utility errors.
    Inherits from DarcaException to provide structured logging,
    metadata handling, and optional chaining of original exceptions.
    """

    def __init__(self, message, error_code=None, metadata=None, cause=None):
        super().__init__(
            message=message,
            error_code=error_code or "FILE_UTILS_ERROR",
            metadata=metadata,
            cause=cause,
        )


class FileUtils:
    @staticmethod
    def file_exist(path: str) -> bool:
        """
        Check if a file exists.

        Args:
            path (str): The file path to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        exists = os.path.isfile(path)
        logger.debug(f"Checked file existence for '{path}': {exists}")
        return exists

    @staticmethod
    def write_file(
        file_path: str, content: str, mode: str = "w", encoding: str = "utf-8"
    ) -> bool:
        """
        Write the given content to a file.

        Args:
            file_path (str): The path to the file.
            content (str): The content to be written.
            mode (str, optional): The file opening mode (default is "w").
            encoding (str, optional): The file encoding (default is "utf-8").

        Returns:
            bool: True if the file was written successfully.

        Raises:
            FileUtilsException: If the file could not be written.
        """
        directory = os.path.dirname(file_path)
        if directory and not DirectoryUtils.directory_exist(directory):
            logger.warning(
                f"Directory does not exist for file: {directory}, creating it."
            )
            created = DirectoryUtils.create_directory(directory)
            if not created:
                raise FileUtilsException(
                    message="Failed to create directory for file writing.",
                    error_code="DIRECTORY_CREATION_FAILED",
                    metadata={"directory": directory},
                )

        try:
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
            logger.debug(f"Wrote content to file: {file_path}")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to write to file: {file_path}",
                error_code="FILE_WRITE_ERROR",
                metadata={"file_path": file_path, "mode": mode},
                cause=e,
            )

    @staticmethod
    def read_file(
        file_path: str, mode: str = "r", encoding: str = "utf-8"
    ) -> str:
        """
        Read and return the content of the specified file.

        Args:
            file_path (str): The path to the file.
            mode (str, optional): The file opening mode (default is "r").
            encoding (str, optional): The file encoding (default is "utf-8").

        Returns:
            str: The content of the file.

        Raises:
            FileUtilsException: If the file doesn't exist or cannot be read.
        """
        if not FileUtils.file_exist(file_path):
            raise FileUtilsException(
                message=f"File not found: {file_path}",
                error_code="FILE_NOT_FOUND",
                metadata={"file_path": file_path},
            )

        try:
            with open(file_path, mode, encoding=encoding) as f:
                content = f.read()
            logger.debug(f"Read content from file: {file_path}")
            return content
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to read file: {file_path}",
                error_code="FILE_READ_ERROR",
                metadata={"file_path": file_path, "mode": mode},
                cause=e,
            )

    @staticmethod
    def remove_file(file_path: str) -> bool:
        """
        Remove the specified file.

        Args:
            file_path (str): The path to the file to be removed.

        Returns:
            bool: True if the file was removed successfully.

        Raises:
            FileUtilsException: If the file does not exist or
                                cannot be removed.
        """
        if not FileUtils.file_exist(file_path):
            raise FileUtilsException(
                message=f"File does not exist: {file_path}",
                error_code="FILE_NOT_FOUND",
                metadata={"file_path": file_path},
            )

        try:
            os.remove(file_path)
            logger.debug(f"Removed file: {file_path}")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to remove file: {file_path}",
                error_code="FILE_REMOVE_ERROR",
                metadata={"file_path": file_path},
                cause=e,
            )

    @staticmethod
    def rename_file(src: str, dst: str) -> bool:
        """
        Rename a file from the source path to the destination path.

        Args:
            src (str): The current file path.
            dst (str): The new file path.

        Returns:
            bool: True if the file was renamed successfully.

        Raises:
            FileUtilsException: If the source doesn't exist, destination
                                exists, or rename fails.
        """
        if not FileUtils.file_exist(src):
            raise FileUtilsException(
                message=f"Source file does not exist: {src}",
                error_code="FILE_NOT_FOUND",
                metadata={"src": src},
            )
        if FileUtils.file_exist(dst):
            raise FileUtilsException(
                message=f"Destination file already exists: {dst}",
                error_code="FILE_ALREADY_EXISTS",
                metadata={"dst": dst},
            )

        try:
            os.rename(src, dst)
            logger.debug(f"Renamed file from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to rename file from '{src}' to '{dst}'",
                error_code="FILE_RENAME_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )

    @staticmethod
    def move_file(src: str, dst: str) -> bool:
        """
        Move a file from the source path to the destination path.

        Args:
            src (str): The current file path.
            dst (str): The destination file path.

        Returns:
            bool: True if the file was moved successfully.

        Raises:
            FileUtilsException: If the source doesn't exist or move fails.
        """
        if not FileUtils.file_exist(src):
            raise FileUtilsException(
                message=f"Source file does not exist: {src}",
                error_code="FILE_NOT_FOUND",
                metadata={"src": src},
            )

        try:
            shutil.move(src, dst)
            logger.debug(f"Moved file from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to move file from '{src}' to '{dst}'",
                error_code="FILE_MOVE_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )

    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """
        Copy a file from the source path to the destination path.

        Args:
            src (str): The source file path.
            dst (str): The destination file path.

        Returns:
            bool: True if the file was copied successfully.

        Raises:
            FileUtilsException: If the source doesn't exist, destination
                                exists, or copy fails.
        """
        if not FileUtils.file_exist(src):
            raise FileUtilsException(
                message=f"Source file does not exist: {src}",
                error_code="FILE_NOT_FOUND",
                metadata={"src": src},
            )
        if FileUtils.file_exist(dst):
            raise FileUtilsException(
                message=f"Destination file already exists: {dst}",
                error_code="FILE_ALREADY_EXISTS",
                metadata={"dst": dst},
            )

        try:
            shutil.copy2(src, dst)
            logger.debug(f"Copied file from '{src}' to '{dst}'")
            return True
        except Exception as e:
            raise FileUtilsException(
                message=f"Failed to copy file from '{src}' to '{dst}'",
                error_code="FILE_COPY_ERROR",
                metadata={"src": src, "dst": dst},
                cause=e,
            )
