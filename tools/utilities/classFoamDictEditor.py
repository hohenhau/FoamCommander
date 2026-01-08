#!/usr/bin/python

import re
import sys
from pathlib import Path
from typing import Optional


class FoamDictEditor:
    """Editor for OpenFOAM dictionary files with support for reading, writing, and deleting entries."""

    def __init__(self, foam_dict: str | Path):
        """
        Initialize the editor with a path to an OpenFOAM dictionary file.

        Args:
            foam_dict: Path to the OpenFOAM dictionary file

        Raises:
            FileNotFoundError: If the specified file does not exist
        """
        self.foam_dict = Path(foam_dict)
        self.entries: dict = {}

        if not self.foam_dict.exists():
            raise FileNotFoundError(f"File {self.foam_dict} does not exist")


    def _read_file(self) -> str:
        """Read and return the contents of the foam dictionary file."""
        return self.foam_dict.read_text()


    def _write_file(self, content: str) -> None:
        """Write content to the foam dictionary file."""
        self.foam_dict.write_text(content)


    @staticmethod
    def _get_entry_regex(key: str) -> re.Pattern:
        """
        Create a regex pattern for identifying OpenFOAM entries.

        Matches: Indentation, Key, Value (up to ; or //), and trailing Comment/Semicolon.

        Args:
            key: The dictionary key to match

        Returns:
            Compiled regex pattern
        """
        # Group 1: Leading whitespace and key
        # Value: Matches everything that isn't a semicolon or comment start
        # Group 2: Trailing whitespace, inline comments, and semicolon
        return re.compile(
            rf"^(\s*{re.escape(key)}\s+)[^;/]+(.*?;)",
            re.MULTILINE
        )


    def get_value(self, key: str) -> Optional[str]:
        """
        Retrieve the value of a key directly from the file.

        Args:
            key: The dictionary key to retrieve

        Returns:
            The value associated with the key, or None if not found
        """
        text = self._read_file()
        # \s+ handles multiple whitespaces between key and value
        # [^;/]+ captures everything up to semicolon or comment
        pattern = re.compile(rf"^\s*{re.escape(key)}\s+([^;/]+)", re.MULTILINE)
        match = pattern.search(text)

        return match.group(1).strip() if match else None


    def set_value(self, key: str, new_value: str) -> None:
        """
        Replace the value of an existing key, preserving comments and formatting.

        Args:
            key: The dictionary key to update
            new_value: The new value to set

        Raises:
            SystemExit: If the key is not found in the file
        """
        self.entries[key] = new_value
        text = self._read_file()
        pattern = self._get_entry_regex(key)

        if not pattern.search(text):
            sys.exit(f"Error: Key '{key}' not found in {self.foam_dict}. Exiting.")

        # Escape the new_value to prevent it from being interpreted as a backreference
        escaped_value = new_value.replace("\\", r"\\")
        # \1 is ' key ', \2 is ' // comment ;'
        updated = pattern.sub(rf"\1{escaped_value} \2", text)
        self._write_file(updated)


    def add_value(self, key: str, value: str, comment: Optional[str] = None) -> None:
        """
        Append a new key-value pair to the end of the dictionary file.

        Args:
            key: The dictionary key to add
            value: The value to associate with the key
            comment: Optional comment to include above the entry
        """
        comment_str = ""
        if comment:
            # Ensure comment starts with //
            comment_str = comment if comment.startswith("//") else f"// {comment}"
            # Ensure comment ends with newline
            comment_str = comment_str if comment_str.endswith("\n") else f"{comment_str}\n"

        value_str = f"{key} {value};\n"
        text = self._read_file().rstrip()

        self._write_file(f"{text}\n\n{comment_str}{value_str}")


    def delete_value(self, key: str) -> None:
        """
        Delete a dictionary entry by key and clean up preceding whitespace.

        Args:
            key: The dictionary key to delete

        Raises:
            KeyError: If the key is not found in the dictionary
        """
        lines = self._read_file().splitlines()
        new_lines = []
        entry_deleted = False

        for line in lines:
            # Remove comments for matching purposes
            stripped = re.sub(r"//.*", "", line).strip()

            # Check if this line contains the key
            if re.match(rf"^{re.escape(key)}\s+.*?;", stripped):
                entry_deleted = True
                # Remove preceding empty lines
                while new_lines and not new_lines[-1].strip():
                    new_lines.pop()
                continue

            new_lines.append(line)

        if not entry_deleted:
            raise KeyError(f"Key '{key}' not found in dictionary")

        self._write_file("\n".join(new_lines) + "\n")


    def has_key(self, key: str) -> bool:
        """
        Check if a key exists in the dictionary.

        Args:
            key: The dictionary key to check

        Returns:
            True if the key exists, False otherwise
        """
        return self.get_value(key) is not None


    @staticmethod
    def parse_value(value: str) -> None | bool | int | float | str:
        """
        Parse a string value into its appropriate Python type.

        Args:
            value: The string value to parse

        Returns:
            Parsed value as None, bool, int, float, or str
        """
        value_lower = value.lower()

        # Check for None/NA
        if value_lower in ("none", "na"):
            return None

        # Check for boolean values
        if value_lower in ("true", "yes", "on"):
            return True
        if value_lower in ("false", "no", "off"):
            return False

        # Try to parse as numeric
        try:
            # Check if it's an integer (no decimal point or scientific notation)
            if '.' not in value and 'e' not in value_lower:
                return int(value)
            return float(value)
        except ValueError:
            pass

        # Return as string if all else fails
        return value


    def load_dict_entries(self) -> dict:
        """
        Load and parse all entries from the OpenFOAM dictionary file.

        Parses key-value pairs from the file, handling comments and
        converting values to appropriate Python types.

        Returns:
            Dictionary of parsed entries with keys mapped to their typed values
        """
        text = self._read_file()

        # Remove /* block */ comments (multi-line safe)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

        self.entries.clear()

        for line in text.splitlines():
            # Remove inline comments (any text following a '//')
            line = re.sub(r"//.*", "", line).strip()

            # Skip blank lines
            if not line:
                continue

            # Entry format: "<whitespaces> key <whitespaces> value <whitespaces>;"
            # \s+ handles multiple whitespaces between key and value
            # .*? captures the value (non-greedy to stop at semicolon)
            match = re.match(r"([A-Za-z0-9_]+)\s+(.*?);", line)
            if match:
                key, value = match.groups()
                value = value.strip()
                value = self.parse_value(value)
                self.entries[key] = value

        return self.entries


    def load_nu_from_transport_properties(self) -> float:
        """
        Load the kinematic viscosity (nu) value from transportProperties.

        Handles OpenFOAM format: nu nu [0 2 -1 0 0 0 0] 1.0e-06

        Returns:
            The kinematic viscosity value as a float

        Raises:
            KeyError: If 'nu' key is not found in the file
            ValueError: If the nu value cannot be parsed as a float
        """
        self.load_dict_entries()
        raw_value = self.entries.get("nu")

        if raw_value is None:
            raise KeyError("Key 'nu' not found in transportProperties")

        try:
            # Extract the last token (the magnitude) regardless of notation
            val_token = str(raw_value).split()[-1]
            return float(val_token)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Could not parse numerical nu value from: {raw_value}") from e


    def overwrite_nu_in_transport_properties(self, new_nu: float) -> None:
        """
        Overwrite the nu value in transportProperties with scientific notation.

        Expected format: nu nu [0 2 -1 0 0 0 0] 1.000e-06;

        Args:
            new_nu: The new kinematic viscosity value

        Raises:
            KeyError: If 'nu' entry cannot be located in the expected format
        """
        text = self._read_file()

        # Format the float to scientific notation with 3 decimal places
        new_nu_str = f"{new_nu:.3e}"

        # Pattern matches: nu nu [0 2 -1 0 0 0 0] <value>;
        # Group 1: 'nu nu [0 2 -1 0 0 0 0] '
        # Group 2: trailing whitespace/semicolon
        pattern = re.compile(
            r"^(nu\s+nu\s+\[\s*0\s+2\s+-1\s+0\s+0\s+0\s+0\s*\]\s+)[0-9.eE+-]+(\s*;)",
            re.MULTILINE
        )

        if not pattern.search(text):
            raise KeyError("Could not locate 'nu' entry in expected format: nu nu [0 2 -1 0 0 0 0] <value>;")

        updated = pattern.sub(rf"\1{new_nu_str}\2", text)
        self._write_file(updated)
