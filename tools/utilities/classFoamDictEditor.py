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
    def parse_values(value:str):
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


    def load_dict_entries(self):
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
