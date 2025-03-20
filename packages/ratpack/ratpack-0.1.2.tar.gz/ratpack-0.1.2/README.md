![Python build & test](https://github.com/software-students-spring2025/3-python-package-team-1/actions/workflows/build.yaml/badge.svg)

# RatPack 🐀

RatPack is a humorous Python package that simulates rat infestations in your code! It provides tools to create, count, visualize, and exterminate virtual rat infestations represented as files on your filesystem.

**[View on PyPI](https://pypi.org/project/ratpack/0.1.2/)** 

## Description

RatPack brings a bit of lighthearted fun to software development by creating harmless "rat" files in your project directories. These virtual rats can be managed using a set of intuitive functions. The package is perfect for:

- Teaching concepts of file system operations in a fun way
- Demonstrating Python decorator patterns
- Adding a bit of whimsy to your development process
- Setting up prank scenarios for your programmer colleagues

## Installation

Install RatPack using pip:

```bash
pip install ratpack
```

Or with pipenv:

```bash
pipenv install ratpack
```

## Usage

### Quick Start

Create an infestation and manage it:

```python
from ratpack import infest, count_rats, visualize_infestation, exterminate

# Decorate any function to create rats when it's called
@infest()
def my_function():
    return "This function creates rats when called!"

# Call the function to create rats
my_function()

# Count the rats
stats = count_rats()
print(f"You have {stats['total_rats']} rats!")

# Visualize the infestation
report = visualize_infestation()
print(report)

# Exterminate the rats
exterminate()
```

### Function Documentation

#### The `@infest` Decorator

The `@infest` decorator creates rat files when the decorated function is called.

```python
from ratpack import infest

@infest(infestation_level=3, rat_types=["sewer_rat", "brown_rat"], burrow_probability=0.2)
def my_function():
    return "This creates rats when called!"
```

Parameters:

- `infestation_level` (int, default=3): Controls how many rats are created (1-5)
- `rat_types` (List[str], default=None): List of rat types to create. If None, all types are used
- `burrow_probability` (float, default=0.2): Chance (0.0-1.0) of creating a rat burrow instead of individual rats

#### The `count_rats` Function

Count rat files in a specified directory.

```python
from ratpack import count_rats

# Count all rats in the current directory
stats = count_rats()

# Count specific rat types only
stats = count_rats(directory="./project", include_burrows=True, rat_types=["sewer_rat"])

print(f"Total rats: {stats['total_rats']}")
print(f"Surface rats: {stats['surface_rats']}")
print(f"Burrowed rats: {stats['burrowed_rats']}")
print("Rats by type:", stats['rats_by_type'])
```

Parameters:

- `directory` (str, default="."): Directory to count rats in
- `include_burrows` (bool, default=True): Whether to count rats inside burrows
- `rat_types` (List[str], default=None): List of rat types to count. If None, count all types

Returns a dictionary with statistics about the rat infestation.

#### The `visualize_infestation` Function

Visualize the rat infestation in text or ASCII art format.

```python
from ratpack import visualize_infestation

# Get a text visualization
text_report = visualize_infestation(output_format="text")
print(text_report)

# Get an ASCII art visualization
ascii_report = visualize_infestation(output_format="ascii")
print(ascii_report)
```

Parameters:

- `directory` (str, default="."): Directory to visualize rats in
- `output_format` (str, default="text"): Format of the output, either "text" or "ascii"
- `include_burrows` (bool, default=True): Whether to include rats inside burrows

Returns a string representation of the rat infestation.

#### The `exterminate` Function

Remove rat files from a specified directory.

```python
from ratpack import exterminate

# Remove all rats
stats = exterminate()
print(f"Removed {stats['rats_removed']} rats")

# Remove only specific rat types
stats = exterminate(rat_types=["sewer_rat"])

# Remove only burrows (not individual rats)
stats = exterminate(burrows_only=True)

# Perform a dry run without actually removing any files
stats = exterminate(dry_run=True)
```

Parameters:

- `directory` (str, default="."): Directory to remove rats from
- `rat_types` (List[str], default=None): List of rat types to remove. If None, remove all types
- `burrows_only` (bool, default=False): If True, only remove burrows and rats inside them
- `dry_run` (bool, default=False): If True, don't actually remove files, just report what would be removed

Returns a dictionary with statistics about the extermination.

### Example Program

Here's a complete example that demonstrates all RatPack functionality:

```python
import os
from ratpack import infest, count_rats, visualize_infestation, exterminate

def main():
    """Demonstrate the full RatPack workflow."""
    print("🐀 RatPack Demo 🐀")
    
    # Clean directory
    print("\n1. First, let's check for existing rats:")
    initial_stats = count_rats()
    print(visualize_infestation())
    
    if initial_stats["total_rats"] > 0:
        print("\nClearing out existing rats for a clean demo...")
        exterminate()
    
    # Create three different levels of infestation
    print("\n2. Let's create some rat infestations with different parameters:")
    
    print("\n--- Low Infestation ---")
    create_low_infestation()
    low_stats = count_rats()
    print(visualize_infestation())
    print(f"Created {low_stats['total_rats']} rats")
    
    print("\n--- Medium Infestation ---")
    create_medium_infestation()
    medium_stats = count_rats()
    print(visualize_infestation())
    print(f"Created {medium_stats['total_rats']} rats")
    
    print("\n--- High Infestation with Burrows ---")
    create_high_infestation_with_burrows()
    high_stats = count_rats()
    print(visualize_infestation(output_format="ascii"))
    print(f"Created {high_stats['total_rats']} rats")
    
    # Demonstrate filtering by rat type
    print("\n3. Let's count only sewer rats:")
    sewer_stats = count_rats(rat_types=["sewer_rat"])
    print(f"Found {sewer_stats['rats_by_type']['sewer_rat']} sewer rats")
    
    # Demonstrate removing specific rat types
    print("\n4. Let's remove only brown rats:")
    before_partial = count_rats()
    exterminate_stats = exterminate(rat_types=["brown_rat"])
    after_partial = count_rats()
    print(f"Removed {exterminate_stats['rats_removed']} brown rats")
    print(f"Rats before: {before_partial['total_rats']}, Rats after: {after_partial['total_rats']}")
    
    # Clean up all rats
    print("\n5. Finally, let's clean everything up:")
    final_exterminate = exterminate()
    print(f"Removed {final_exterminate['rats_removed']} rats and {final_exterminate['burrows_removed']} burrows")
    
    # Verify cleanliness
    final_check = count_rats()
    if final_check["total_rats"] == 0:
        print("\nAll clean! No more rats!")
    else:
        print(f"\nOh no! {final_check['total_rats']} rats escaped extermination!")

@infest(infestation_level=1, rat_types=["sewer_rat"])
def create_low_infestation():
    """Create a low-level infestation with only sewer rats."""
    return "Low infestation created"

@infest(infestation_level=3, rat_types=["brown_rat", "black_rat"])
def create_medium_infestation():
    """Create a medium-level infestation with brown and black rats."""
    return "Medium infestation created"

@infest(infestation_level=5, burrow_probability=0.8)
def create_high_infestation_with_burrows():
    """Create a high-level infestation with all rat types and high burrow probability."""
    return "High infestation with burrows created"

if __name__ == "__main__":
    main()
```

## Development Setup

To set up a development environment for RatPack:

1. Clone the repository:
```bash
git clone https://github.com/software-students-spring2025/3-python-package-team-1.git
cd 3-python-package-team-1
```

2. Install pipenv if you haven't already:
```bash
pip install pipenv
```

3. Install dependencies:
```bash
pipenv install --dev
```

4. Activate the virtual environment:
```bash
pipenv shell
```

### Running Tests

Run the tests using pytest:

```bash
pytest
```

### Building the Package

To build the package:

```bash
python -m build
```

This will create both source distribution and wheel files in the `dist/` directory.

### Publishing to PyPI

To publish the package to PyPI:

```bash
python -m twine upload dist/*
```

You'll need to provide your PyPI credentials.

## Project Structure

```
RatPack/
├── src/
│   └── ratpack/
│       ├── __init__.py          # Package initialization and imports
│       ├── infest.py            # Core functionality implementation
│       └── images/              # Images for rat files
│
├── tests/
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Test fixtures and utilities
│   ├── test_infest_decorator.py # Tests for @infest decorator
│   ├── test_count_rats.py       # Tests for count_rats function
│   ├── test_exterminate.py      # Tests for exterminate function
│   ├── test_visualize_infestation.py # Tests for visualize_infestation function
│   └── test_integration.py      # Integration tests
│
├── .github/
│   └── workflows/               # GitHub Actions workflows
│
├── README.md                    # Project documentation
├── LICENSE                      # Project license
├── Pipfile                      # Project dependencies
└── setup.py                     # Package configuration for distribution
```

## Environment Configuration

No special environment variables are needed to run RatPack. The package works directly with the file system as is.

## Contributors

- [Patrick Cao](https://github.com/Novrain7) - pc3135@nyu.edu
- [Helen Ho](https://github.com/hhelenho) - hth2016@nyu.edu
- [Noah Perelmuter](https://github.com/np2446) - np2446@nyu.edu
- [Apollo Wyndham](https://github.com/a-wyndham1) - acw8241@nyu.edu

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

RatPack creates files on your system but does not modify any existing files. The "rats" are just harmless image files with a `.rat` extension. While we've taken care to ensure these are benign, always be mindful when using packages that create files on your system.
