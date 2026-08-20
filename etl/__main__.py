"""Entrypoint for ``python -m etl build|approve|release``."""

import sys

from etl.main import main

if __name__ == "__main__":
    sys.exit(main())