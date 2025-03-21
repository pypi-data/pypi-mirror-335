import narwhals as nw
import json
import webbrowser
import tempfile
from importlib import resources
import numbers
from typing import Union, List, Dict, Any
from string import Template

def show(data_source: Union[Any, List[Dict[str, Any]]]):
    """Displays data in a browser using Tabulator.js.
    
    Args:
        data_source: Either a Narwhals-compatible DataFrame or a list of dictionaries with common keys.
        
    Raises:
        ValueError: If data_source is neither a DataFrame nor a list of dictionaries.
    """
    # Validate input
    if not (isinstance(data_source, list) or hasattr(data_source, 'columns')):
        raise ValueError("data_source must be either a DataFrame or a list of dictionaries")
    
    if isinstance(data_source, list) and (not data_source or not isinstance(data_source[0], dict)):
        raise ValueError("If data_source is a list, it must be non-empty and contain dictionaries")

    # Handle list of dictionaries directly or convert DataFrame to rows
    if isinstance(data_source, list):
        raw_data = data_source
        # Get columns from first dictionary while preserving order
        columns = list(raw_data[0].keys()) if raw_data else []
    else:
        raw_data = nw.from_native(data_source).iter_rows(named=True)
        # Get columns directly from DataFrame
        columns = list(data_source.columns)
    
    data = []
    
    # Process the data
    for row in raw_data:
        serializable_row = {}
        for key in columns:  # Use ordered columns list
            value = row.get(key)
            if isinstance(value, (type(None), bool)):
                serializable_row[key] = value
            elif isinstance(value, str):
                serializable_row[key] = value
            elif isinstance(value, complex):
                # Special handling for complex numbers
                serializable_row[key] = f"{value.real:g}{value.imag:+g}j"
            elif isinstance(value, numbers.Number):
                # Preserve numeric types for better table sorting/filtering
                serializable_row[key] = float(value)
            else:
                # Convert any other types to their string representation
                serializable_row[key] = str(value)
        data.append(serializable_row)

    # If no data, ensure we at least have column definitions if available from DataFrame
    if not isinstance(data_source, list) and not data and hasattr(data_source, 'columns'):
        columns = list(data_source.columns)
    
    # Load Tabulator resources
    tabulator = {}
    for ext in ['js', 'css']:
        # Try installed package location first
        try:
            with resources.files('tablescope').joinpath(f'static/tabulator.min.{ext}').open('r') as f:
                tabulator[ext] = f.read()
        except (FileNotFoundError, OSError):
            # Fall back to development location
            try:
                with open(f'static/tabulator.min.{ext}', 'r') as f:
                    tabulator[ext] = f.read()
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    f"Could not find tabulator.min.{ext} in either the installed package "
                    "or the development directory. Make sure the static files are present."
                ) from e

    # Dynamically generate column definitions with appropriate editors
    column_defs = []
    for col in columns:  # Use ordered columns list
        # Get a sample value to determine type, safely handling empty data
        sample = data[0][col] if data and col in data[0] else None
        
        col_def = {
            "title": col,
            "field": col,
            "editor": True,
            "resizable": True,
            "headerFilter": True,
            "minWidth": 125,
            "maxWidth": 250,
            "widthGrow": 1,
        }
        
        if isinstance(sample, (int, float)):
            col_def["editor"] = "number"
            col_def["editorParams"] = {
                "selectContents": True  # Select all content when editing
            }
            col_def["headerFilter"] = "minMax"
            col_def["headerFilterFunc"] = "minMaxFilterFunction"
            col_def["headerFilterLiveFilter"] = False
        else:
            col_def["editor"] = "input"
            col_def["editorParams"] = {
                "selectContents": True
            }
        
        column_defs.append(col_def)

    # Generate column options for the group-by dropdown
    column_options = ' '.join(f'<option value="{col["field"]}">{col["title"]}</option>' for col in column_defs)

    # Load and format the HTML template
    try:
        with resources.files('tablescope').joinpath('static/table_view.html.jinja').open('r') as f:
            template = Template(f.read())
    except (FileNotFoundError, OSError):
        # Fall back to development location
        try:
            with open('static/table_view.html.jinja', 'r') as f:
                template = Template(f.read())
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Could not find table_view.html.jinja template in either the installed package "
                "or the development directory. Make sure the template file is present."
            ) from e

    html = template.substitute(
        tabulator_css=tabulator['css'],
        tabulator_js=tabulator['js'],
        column_options=column_options,
        table_data=json.dumps(data),
        column_defs=json.dumps(column_defs)
    )

    with tempfile.NamedTemporaryFile(mode='w', suffix=".html", delete=False) as f:
        f.write(html)
        filepath = f.name

    try:
        if webbrowser.open(f"file://{filepath}"):
            return

    except Exception as e:
        print(f"Error opening browser: {e}")
        print(f"Please open this file in your browser: {filepath}")
