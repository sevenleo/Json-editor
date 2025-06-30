# JSON Editor

A JSON file management system with a graphical interface, developed in Python with Tkinter. It allows editing, validating, and maintaining structured JSON files according to a defined schema.

## Description

This system is designed to function as a visual JSON database editor, allowing you to:

- Validate JSON data against a schema defined in a model file
- View and edit data in a user-friendly way with appropriate widgets for each data type
- Add and remove records following the defined schema
- Easily search for information, navigate, and manipulate records
- Export and save the edited data

## Requirements

- Python 3.6 or higher
- Tkinter (included in most standard Python installations)
- For full drag-and-drop support on Windows, the `pywin32` module is recommended:
  ```
  pip install pywin32
  ```

## Installation

1. Clone this repository or download the files
2. Ensure that Python 3.6+ is installed
3. (Optional) Install `pywin32` for full drag-and-drop support on Windows

## How to Use

Run the main file:

```
python main.py
```

### Basic workflow:

1. Load a JSON model file (containing the `__meta__` definition)
2. Load a JSON data file or create a new dataset
3. Edit, add, or remove records as needed
4. Save the changes to the original file or a new file

## Model File Structure

The model file must contain a JSON object with a `__meta__` property that defines the expected data structure:

```json
{
  "__meta__": {
    "field_name": {
      "type": "data_type",
      "required": true_or_false
    },
    ...
  }
}
```

### Supported data types:

- `str` - Strings
- `int` - Integers
- `float` - Floating-point numbers
- `bool` - Boolean values (true/false)
- `list` - Generic lists
- `list[type]` - Typed lists (e.g., `list[str]`). This also applies to `list[dict]`, allowing the creation of lists of objects with a defined structure.
- `dict` or `object` - Nested dictionaries. If the model specifies the dictionary fields, the editing interface will display structured fields. Otherwise, a generic key-value pair interface will be used.

### Example:

```json
{
  "__meta__": {
    "name": { "type": "str", "required": true },
    "email": { "type": "str", "required": false },
    "age": { "type": "int", "required": false },
    "active": { "type": "bool", "required": true },
    "tags": { "type": "list[str]", "required": false },
    "address": {
      "type": "dict",
      "required": false,
      "fields": {
        "street": { "type": "str", "required": true },
        "city": { "type": "str", "required": true },
        "zipcode": { "type": "str", "required": false }
      }
    }
  }
}
```

## Features

### Main features:

- **Real-time validation**: Identifies missing required fields and incorrect data types
- **Spreadsheet-like interface**: Grid view with individual cell editing
- **Type-appropriate editing**: Text inputs, checkboxes, numeric fields, etc.
- **Search**: Searches for content in any field
- **Action history**: Support for undo/redo operations
- **Light/dark theme**: Toggles between themes for better visual comfort
- **Drag and drop**: Support for loading files via drag & drop
- **Export**: Saves data in JSON format

### Keyboard Shortcuts:

- `Ctrl+O` - Load model file
- `Ctrl+D` - Load data file
- `Ctrl+S` - Save data
- `Ctrl+N` - Add new entry
- `Delete` - Delete selected entry
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+F` - Focus on search field
- `F3` - Next search result
- `Shift+F3` - Previous search result

## Examples

The system comes with example files in the `examples/` folder:

- `example_model.json` - An example model with various field types
- `example_data.json` - Example data compatible with the model.
- `complex_model.json` - A more complex model, demonstrating dictionaries and lists with nested structures.
- `complex_data.json` - Corresponding data for the complex model.

## Current Limitations

- Limited support for deeply nested structures
- No support for schema validation via JSON Schema or similar
- No native support for cross-object references

## License

This project is distributed under the MIT license.