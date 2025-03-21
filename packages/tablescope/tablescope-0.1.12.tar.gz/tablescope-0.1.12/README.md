# Tablescope

A lightweight tool for viewing DataFrames in your browser using Tabulator.js. Supports any DataFrame types that are compatible with Narwhals, including pandas and Polars.

## Features

- Interactive table view of your DataFrame
- Full-text search across all columns
- Column-specific filters
- Column sorting and reordering
- Cell editing (double-click to edit)
- Export to CSV or JSON

## Installation

```sh
pip install tablescope
```

## Usage

### Python API

Here's a simple example using a Polars DataFrame:

```python
import polars as pl
from tablescope import show

df = pl.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'London', 'Paris']
})

# Open the table in your browser
show(df)
```

### Command Line Interface

You can also use tablescope from the command line by piping JSON data to it:

```bash
# View a JSON array of objects
echo '[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]' | tablescope

# Or pipe from a JSON file
cat data.json | tablescope
```

The CLI accepts JSON input from stdin and displays it in your browser using the same interactive table interface.

## Development

To set up the development environment:

1. Clone the repository
2. Install development dependencies:
```bash
rye sync
```

1. Download Tabulator.js files:
1. Download the required Tabulator.js files:

```sh
wget https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator.min.js -O static/tabulator.min.js
wget https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator.min.css -O static/tabulator.min.css
```

## License

MIT License
