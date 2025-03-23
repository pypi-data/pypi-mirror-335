# jsonstate
Manage global App state in a JSON (Python dictionary).

## Installation
- `pip install jsonstate`

## Usage
```
from jsonstate import State

state = State({
    "title": "State Example",
    "products": [
        {"name": "Foo", "description": "Foo spam"},
        {"name": "Bar", "description": "Bar spam"},
    ]
})
print_event = lambda **kwargs: print("Event", kwargs)
state.callbacks(key="title").append(print_event)
state.callbacks(key="products").append(print_event)

# This statement updates the state and also invokes on_change callback:
state["products"]["name"] = "Eggs"
# Event {'new_value': 'Eggs', 'old_value': 'State Example', 'action': 'update'}

# This statement also updates the state and invokes on_change callback:
state["products"].append({"name": "Eggs", "description": "Eggs spam"})
# Event {'new_value': {"name": "Eggs", "description": "Eggs spam"}, 'action': 'append'}
```

## Development
Commonly used commands for package development:
- `make check` - run unit tests and linters.
- `make fix` - format code and fix detected fixable issues.
- `make publish` - publishes current package version to pypi.org.
- `make compile` - bump and freeze dependency versions in requirements*.txt files
- `make sync` - upgrade installed dependencies in Virtual Environment (executed after `make compile`)

## Toolset
This package uses these cutting edge tools:
- ruff - for linting and code formatting
- mypy - for type checking
- pip-audit - for known vulnerability detection in dependencies
- deadcode - for unused code detection
- pytest - for collecting and running unit tests
- coverage - for code coverage by unit tests
- hatch - for publishing package to pypi.org
- uv - for Python virtual environment and dependency management
- pyproject.toml - configuration file for all tools
- Makefile - aliases for commonly used command line commands
