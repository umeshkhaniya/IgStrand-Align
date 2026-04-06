"""Legacy compatibility entry point.

This script preserves the historical command:

    python3 src/main_script.py -f <file> -d <dimension>

Internally it now delegates to the modular package CLI in
``igstrand_align.cli`` so there is a single maintained execution path.
"""

from igstrand_align.cli import main as modular_main


def main():
    """Delegate execution to the modular package CLI."""
    return modular_main()


if __name__ == "__main__":
    raise SystemExit(main())
