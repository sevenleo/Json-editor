A system using Python and the Tkinter library, capable of managing JSON files through a graphical interface. The system should:

Load .json files and understand their structure, including nested objects and arrays.

Dynamically generate a visual CRUD interface (Create, Read, Update, Delete) that allows:

Viewing the JSON structure as a tree.

Editing primitive values (string, number, boolean).

Adding new fields to objects or new elements to arrays.

Removing keys, elements, or entire structures.

Save changes back to the original file or export to a new .json file.

Detect and preserve the data type when editing values.

Optionally validate the content based on a .schema.json file if provided.

Provide a simple and intuitive GUI that adapts to the complexity of the JSON structure.

Additional desired features:

Drag and drop support for JSON files.

Search functionality for keys or values within the JSON.

Change history with undo/redo support.

Support for large files, with optimized parsing.

Light and dark mode toggle.

The goal is to create a lightweight, cross-platform application that's easy to use for both technical and non-technical users, focusing on safe and organized JSON data editing.