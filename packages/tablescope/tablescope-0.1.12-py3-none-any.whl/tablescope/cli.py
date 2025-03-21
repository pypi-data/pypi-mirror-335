#!/usr/bin/env python3

import sys
import json
from . import show

def main():
    """Read JSON from stdin and display it using tablescope."""
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, list):
            data = [data]  # Wrap single object in a list
        show(data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 