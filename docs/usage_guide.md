# JSON Editor Usage Guide

This guide provides detailed instructions on how to use the JSON Editor, a system that allows you to manage structured JSON files with schema validation.

## Table of Contents

1. [Introduction](#introduction)
2. [Basic Concepts](#basic-concepts)
3. [Getting Started](#getting-started)
4. [User Interface](#user-interface)
5. [File Operations](#file-operations)
6. [Data Editing](#data-editing)
7. [Search and Navigation](#search-and-navigation)
8. [Settings](#settings)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

## Introduction

The JSON Editor is a graphical application that allows you to edit, validate, and manage JSON files based on a predefined schema. The system works with two types of files:

1.  **Model File**: Contains the schema definition in the `__meta__` section, which specifies fields, data types, and requirements.
2.  **Data File**: Contains the actual data, which must follow the structure defined in the model.

## Basic Concepts

### Data Model (`__meta__`)

The model defines the expected data structure through a `__meta__` object with the following format:

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

### Supported Data Types

- `str`: Strings
- `int`: Integers
- `float`: Floating-point numbers
- `bool`: Boolean values (true/false)
- `list`: Generic lists
- `list[type]`: Typed lists (e.g., `list[str]` for a list of strings)
- `dict` or `object`: Nested dictionaries. If the model specifies the dictionary fields, the editing interface will display structured fields. Otherwise, a generic key-value pair interface will be used.

### Data File

The data is stored as a list of JSON objects that follow the structure defined in the model:

```json
[
  {
    "name": "John Silva",
    "email": "john@example.com",
    "age": 30,
    "active": true
  },
  {
    "name": "Maria Oliveira",
    "email": "maria@example.com",
    "age": 25,
    "active": false
  }
]
```

## Getting Started

### Starting the Application

1.  Run the `main.py` file:
    ```
    python main.py
    ```
2.  The application will load and display the main window.

### Loading a Model

1.  Click the "Load Model" button on the toolbar or use the File > Load Model menu (or press `Ctrl+O`).
2.  Select the JSON file containing the `__meta__` definition.
3.  The system will parse the model and configure the interface accordingly.

### Loading Data

1.  Click the "Load Data" button on the toolbar or use the File > Load Data menu (or press `Ctrl+D`).
2.  Select the JSON file containing the data.
3.  The data will be loaded and validated against the current model.

## User Interface

### Main Components

-   **Toolbar**: Contains buttons for the most common operations.
-   **Search Panel**: Allows you to search for information in the data.
-   **Table View**: Displays the data in a tabular format.
-   **Status Bar**: Shows information about the loaded files.

### Keyboard Shortcuts

- `Ctrl+O`: Load model file
- `Ctrl+D`: Load data file
- `Ctrl+S`: Save data
- `Ctrl+N`: Add new entry
- `Delete`: Delete selected entry
- `Ctrl+Z`: Undo
- `Ctrl+Y`: Redo
- `Ctrl+F`: Focus on search field
- `F3`: Next search result
- `Shift+F3`: Previous search result

## File Operations

### Loading an Existing Model

1.  Use the "Load Model" button or the File > Load Model menu.
2.  Navigate to the desired JSON model file.
3.  Select the file and click "Open".

### Loading Existing Data

1.  Use the "Load Data" button or the File > Load Data menu.
2.  Navigate to the desired JSON data file.
3.  Select the file and click "Open".

### Saving Data

1.  Use the "Save Data" button or the File > Save menu (or press `Ctrl+S`).
2.  If the file has not been saved before, you will be prompted for a location to save it.
3.  The data will be validated and saved in JSON format.

### Saving Data as a New File

1.  Use the File > Save As menu.
2.  Navigate to the desired location and provide a name for the file.
3.  Click "Save".

### Exporting to CSV

1.  Use the Tools > Export to CSV menu.
2.  Select the location and name for the CSV file.
3.  The data will be converted and saved in CSV format.

### Importing from CSV

1.  Use the Tools > Import from CSV menu.
2.  Select the CSV file to import.
3.  The data will be converted to JSON and validated against the current model.

## Data Editing

### Adding a New Entry

1.  Click the "Add" button or use the Edit > Add Entry menu (or press `Ctrl+N`).
2.  A new entry will be created with default values for required fields.
3.  An editing dialog will open for each field, allowing you to fill in the values.

### Editing an Existing Entry

1.  Select the entry you want to edit in the table.
2.  Click the "Edit" button, use the Edit > Edit Selected menu, or double-click the entry.
3.  An editing dialog will open for each field, allowing you to change the values.

### Deleting an Entry

1.  Select the entry you want to delete in the table.
2.  Click the "Delete" button, use the Edit > Delete Selected menu, or press the `Delete` key.
3.  Confirm the deletion when prompted.

### Undo/Redo

-   To undo the last operation, use the "Undo" button, the Edit > Undo menu, or press `Ctrl+Z`.
-   To redo an undone operation, use the "Redo" button, the Edit > Redo menu, or press `Ctrl+Y`.

## Search and Navigation

### Searching the Data

1.  Type the search term in the search field at the top of the window.
2.  Press `Enter` or click the "Search" button.
3.  The first result will be selected automatically.

### Navigating Between Results

-   To go to the next result, click the "Next" button or press `F3`.
-   To go to the previous result, click the "Previous" button or press `Shift+F3`.

## Settings

### Accessing Preferences

1.  Use the Settings > Preferences menu.
2.  A settings dialog will open with several tabs for different categories.

### Toggling the Theme

1.  Click the "Dark/Light Theme" button on the toolbar or use the View > Toggle Theme menu.
2.  The interface will be updated with the new theme.

### Customizing Behavior

The settings dialog allows you to customize various aspects of the system:

-   **Interface**: Window size, font, drag-and-drop behavior, etc.
-   **Files**: Backup creation, auto-save, encoding, etc.
-   **Validation**: When to validate, strict type checking, etc.
-   **Export**: Export formats, CSV delimiters, etc.
-   **Directories**: Custom locations for different file types.

## Advanced Features

### Data Validation

The system automatically validates data against the model at various times:

-   When loading a data file
-   When editing an entry
-   Before saving (can be disabled in settings)

Invalid entries are highlighted in the table view.

### Drag and Drop

You can drag JSON files directly into the application window:

-   If the file contains a `__meta__` object, it will be treated as a model.
-   Otherwise, it will be treated as a data file.

### Auto-Save

The system can automatically save data at regular intervals if configured:

1.  Go to Settings > Preferences > Files.
2.  Set the auto-save interval in seconds (0 to disable).

## Troubleshooting

### Validation Errors

If the data does not match the model, you will see detailed error messages:

-   Missing required fields
-   Incorrect data types
-   Fields not defined in the model

### Large Files

For very large files, the system uses optimized processing:

-   Loading in chunks
-   Partial validation
-   Optimized saving

The threshold for considering a file "large" can be adjusted in the settings.

### Compatibility

-   The system is designed to work on Windows, Linux, and macOS.
-   Some features (like drag and drop) may depend on the operating system.
-   Full drag-and-drop functionality on Windows requires the `pywin32` module.

### Common Issues

1.  **Error loading model**: Check that the file contains a valid JSON object with a `__meta__` section.
2.  **Error loading data**: Check that the file contains valid JSON.
3.  **Validation error**: Ensure that the data follows the format defined in the model.
4.  **Unresponsive interface**: For very large files, some operations may take longer.

For more information, consult the full documentation or contact support.