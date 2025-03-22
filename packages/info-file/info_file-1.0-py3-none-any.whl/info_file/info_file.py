import re

class InfoFileParser:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self.variables: dict[str, int | float | str] = {}

    def read(self) -> None:
        """Reads and parses the Info File."""
        pattern = re.compile(r'var\s+(\w+):\s*(\w+)\s*\[\s*(.+?)\s*\]')
        
        with open(self.file_path, "r") as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace
                if not line or line.startswith("#"):  # Ignore empty lines and comments
                    continue

                match = pattern.match(line)
                if match:
                    name, var_type, value = match.groups()
                    self.variables[name] = self._convert_value(var_type, value)

    def _convert_value(self, var_type: str, value: str) -> int | float | str:
        """Converts string value to the correct type."""
        if var_type == "int":
            return int(value)
        elif var_type == "float":
            return float(value)
        elif var_type == "string":
            return value.strip('"')  # Remove surrounding quotes
        return value  # Default to string if unknown type

    def get(self, variable_name: str) -> int | float | str | None:
        """Retrieves the value of a variable."""
        value = self.variables.get(variable_name, None)
        if value is not None:
            print(f"Contents of variable '{variable_name}': {value}")
        else:
            print(f"Variable '{variable_name}' not found.")
        return value

# Global function for direct access
def read(file_name: str, var: str) -> int | float | str | None:
    parser = InfoFileParser(file_name)
    parser.read()
    return parser.get(var)