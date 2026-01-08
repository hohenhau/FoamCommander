#!/usr/bin/python

import re
from pathlib import Path


class ClassFoamDictEditor:

    def __init__(self, foam_dict: str):
        self.foam_dict = Path(foam_dict)
        self.entries: dict = {}
        # Ensure file exists
        if not self.foam_dict.exists():
            raise FileNotFoundError(f"File {self.foam_dict} does not exist")


    @staticmethod
    def parse_values(value:str) -> bool | int | float | str | None:
        """Parses the value into None, a boolean, a float, an int, or a str"""
        if value.lower() in ("none", "na"):
            return None
        if value.lower() in ("true", "yes", "on"):
            return True
        if value.lower() in ("false", "no", "off"):
            return False
        try:
            if '.' not in value and 'e' not in value.lower():
                return int(value)
            return float(value)
        except ValueError:
            pass
        return value


    def load_dict_entries(self) -> dict:
        # Get the text from the OpenFOAM dictionary
        text = self.foam_dict.read_text()
        # Remove /* block */ comments (multi-line safe)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        self.entries.clear()
        for line in text.splitlines():
            # Remove comments (any text following a '//')
            line = re.sub(r"//.*", "", line).strip()
            # Skip blank lines
            if not line:
                continue
            # Entry format: "<whitespaces> key <whitespaces> value <whitespaces>;". Value may be multiple tokens.
            match = re.match(r"([A-Za-z0-9_]+)\s+(.*?)\s*;", line)
            if match:
                key, value = match.groups()
                value = value.strip()
                value = self.parse_values(value)
                self.entries[key] = value
        return self.entries


    def set_value(self, key: str, new_value) -> None:
        """Replace the value of an existing key in the file."""
        self.entries[key] = new_value
        new_value_str = f"{new_value};"
        text = self.foam_dict.read_text()
        # Match: key <anything until semicolon>
        pattern = re.compile(rf"({key}\s+).*?;", re.MULTILINE)
        # Substitute only the value portion
        updated = pattern.sub(rf"\1{new_value_str}", text)
        self.foam_dict.write_text(updated)


    def add_entry(self, key: str, value, comment:str | None = None) -> None:
        """Append a new key-value pair to the end of the dictionary file. Always writes in the form: key   value;"""
        if comment is None:
            comment = ""
        else:
            comment = comment if comment.startswith("//") else f"//{comment}"
            comment = comment if comment.endswith("\n") else f"{comment}\n"
        value_str = f"{key}    {value};\n"
        text = self.foam_dict.read_text().rstrip()
        self.foam_dict.write_text(text + "\n" + comment + value_str)


    def delete_entry(self, key: str) -> None:
        """Delete a dictionary entry by key and remove consecutive blank/comment lines above it."""
        lines = self.foam_dict.read_text().splitlines()
        new_lines = list()
        entry_deleted = False
        for i, line in enumerate(lines):
            # Strip inline // comments for detection
            stripped = re.sub(r"//.*", "", line).strip()
            # Detect target entry:  key  value ;
            if re.match(rf"{key}\s+.*?;", stripped):
                entry_deleted = True
                # Remove blank/comment lines above (in new_lines)
                while new_lines and re.sub(r"//.*", "", new_lines[-1]).strip() == "":
                    new_lines.pop()
                continue  # Do not copy the target line
            new_lines.append(line)
        if not entry_deleted:
            raise KeyError(f"Key '{key}' not found in dictionary")
        # Write output file back
        self.foam_dict.write_text("\n".join(new_lines) + "\n")


    def load_nu_from_transport_properties(self) -> float:
        """Loads the numerical kinematic viscosity (nu) value from transportProperties."""
        self.load_dict_entries()
        # OpenFOAM format typically: nu [0 2 -1 0 0 0 0] 1.0e-06
        raw_value = self.entries.get("nu")
        if raw_value is None:
            raise KeyError("Key 'nu' not found in transportProperties")
        try:
            # Extract the last token (the magnitude) regardless of notation
            val_token = str(raw_value).split()[-1]
            return float(val_token)
        except (ValueError, IndexError):
            raise ValueError(f"Could not parse numerical nu value from: {raw_value}")


    def overwrite_nu_in_transport_properties(self, new_nu: float) -> None:
        """Overwrites the nu value specifically in scientific notation (e.g., 1.000e-06)."""
        text = self.foam_dict.read_text()
        # Format the float to scientific notation with 3 decimal places
        new_nu_str = f"{new_nu:.3e}"
        # Pattern matches the key 'nu', the optional dimension set, and the existing number
        # Groups: 1: 'nu' + leading 'nu' + dimensions, 2: trailing whitespace/semicolon
        pattern = re.compile(r"^(nu\s+nu\s+\[.*?\]\s+)[0-9.eE+-]+(\s*;)", re.MULTILINE)
        if not pattern.search(text):
            # Fallback for entries without the repeated 'nu' keyword or dimensions
            pattern = re.compile(r"^(nu\s+)[0-9.eE+-]+(\s*;)", re.MULTILINE)
        if not pattern.search(text):
            raise KeyError("Could not locate 'nu' entry in the dictionary file.")
        updated = pattern.sub(rf"\1{new_nu_str}\2", text)
        self.foam_dict.write_text(updated)
