# PyErrorSchema

PyErrorSchema is a structured error handling framework for Python that helps developers create consistent, schema-based error messages across applications.

## Installation

The source code is currently hosted on GitHub at [PyErrorSchema](https://github.com/sodinfeliz/PyErrorSchema).

Binary installers for the latest released version are available at the [Python Package Index (PyPI)](https://pypi.org/project/pyerrorschema/).

```sh
pip install pyerrorschema
```

## Key Features

- **Structured Error Schemas**: Define consistent error formats across your application
- **Pre-defined Error Types**: Includes common error types like database errors, file errors, validation errors
- **Framework Integrations**: Specialized support for FastAPI with location tracking
- **Exception Mapping**: Automatically map Python exceptions to appropriate error schemas
- **Hierarchical Error Organization**: Group related errors with specialized subclasses
- **Customizable Error Messages**: Format user-friendly error messages with context information
- **Frontend/Backend Message Separation**: Support for different messages for end-users vs developers (in FastAPI version)

## Basic Usage

```python
from pyerrorschema import ErrorSchema

# Create a basic error
error = ErrorSchema.database_error(
    msg="Failed to connect to the database"
)

# Convert to dictionary for API responses
error_dict = error.to_dict()
print(error_dict)
# Output: {'type': 'database_error', 'msg': 'Database error: failed to connect to the database'}
```

## FastAPI Integration

```python
from pyerrorschema import FastAPIErrorSchema

# Create a FastAPI-specific error
error = FastAPIErrorSchema.validation_error(
    msg="Invalid input data",
    ui_msg="Please check your input and try again",  # User-friendly message
    loc=["body", "user", "email"],  # Location of the error
    input={"email": "invalid-email"}  # Input that caused the error
)

# Convert to dictionary for API responses
print(error.to_dict())
# Output: {'type': 'validation_error', 'msg': 'Invalid input data', 'loc': ['body', 'user', 'email'], 'input': {'email': 'invalid-email'}}
```

## Working with File Errors

```python
from pyerrorschema import ErrorSchema

# Use specialized File error class
file_error = ErrorSchema.File.not_found(path="/path/to/config.json")
print(file_error.msg)
# Output: "File 'config.json' not found."

# Automatically detects directories
dir_error = ErrorSchema.File.not_found(path="/path/to/data/")
print(dir_error.msg)
# Output: "Directory 'data/' not found."
```

## Exception Mapping

```python
from pyerrorschema import ErrorSchema

try:
    # Some code that might raise an exception
    with open("nonexistent_file.txt", "r") as f:
        content = f.read()
except Exception as e:
    # Map the exception to an error schema
    error = ErrorSchema.from_exception(e)
    print(error.to_dict())
    # Output: {'type': 'file_error', 'msg': 'File error: [Errno 2] No such file or directory: 'nonexistent_file.txt''}
```

## Error Groups

Sometimes you need to collect multiple errors into a single group for easier management or to send them all in a single API response. You can use `ErrGroup` or its FastAPI-specific variant `FastAPIErrGroup` to aggregate error schemas. These groups work very similarly to Python lists, offering convenient methods to append, extend, or clear errors.

For example, you can create a group of FastAPI error schemas as follows:

```python
from pyerrorschema import FastAPIErrorSchema, FastAPIErrGroup

err_group = FastAPIErrGroup()
err_group.append(FastAPIErrorSchema.File.not_found(path="test.text"))
err_group.append(FastAPIErrorSchema.DB.no_results("querying the database"))

print(err_group)
```

Which will output:

```python
FastAPIErrGroup(
    FastAPIErrorSchema(
        type='file_error',
        msg="File error: file 'test.text' not found.",
        ui_msg="File 'test.text' not found.",
        loc=[],
        input={}
    ),
    FastAPIErrorSchema(
        type='database_error',
        msg='Database error: no results found while querying the database.',
        ui_msg='No results found while querying the database.',
        loc=[],
        input={}
    )
)
```

The usage of groups is similar to that of a `list`:

- `.append`: Append a single error schema instance to the group.
- `.extend`: Append a list of error schema instances into the group.
- `.clear`: Remove all error schemas from the group.
- **Index Access and Assignment**: Access or update individual errors by index.

## Available Error Types

PyErrorSchema provides a range of built-in error types:

- `database_error`: For database operation failures
- `file_error`: For file I/O issues
- `runtime_error`: For general runtime problems
- `timeout_error`: For timeouts
- `parse_error`: For parsing failures
- `value_error`: For invalid values
- `validation_error`: For input validation issues (FastAPI)
- `docker_error`: For Docker-related issues (FastAPI)

Each error type has specialized factory methods that create appropriate error messages with context.

## Why Use PyErrorSchema?

- **Consistency**: Ensure a consistent error format across your application
- **Maintainability**: Centralize error handling logic
- **Flexibility**: Adapt to different frameworks and use cases
- **User Experience**: Create better error messages for your users
- **Developer Experience**: Make debugging easier with structured error information

## License

This project is licensed under the BSD License.
