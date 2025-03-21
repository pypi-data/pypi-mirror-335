import argparse
import sys
from pathlib import Path

from . import __version__
from .constants import PROGRAM_NAME, PROGRAM_DESCRIPTION
from .core.tree import generate_tree
from .core.builder import build_from_file
from .utils.clipboard import copy_to_clipboard
from .utils.file_utils import write_to_file


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=PROGRAM_DESCRIPTION
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory path to display structure (default: current directory)"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{PROGRAM_NAME} {__version__}"
    )

    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Save the tree structure to the specified output file"
    )

    parser.add_argument(
        "-i", "--input",
        metavar="FILE",
        help="Create directory structure from the specified input file"
    )

    parser.add_argument(
        "-g", "--ignore",
        action="store_true",
        help="Consider .gitignore rules when generating the tree"
    )

    parser.add_argument(
        "-c", "--copy",
        action="store_true",
        help="Copy the tree structure to clipboard"
    )

    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()

    try:
        # Case 1: Create structure from input file
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                print(
                    f"Error: Input file '{args.input}'\
                        does not exist.", file=sys.stderr)
                sys.exit(1)

            build_from_file(input_path)
            print(f"Successfully created directory "
                  f"structure from '{args.input}'.")
            return

        # Case 2: Generate and display tree structure
        path = Path(args.path)
        if not path.exists():
            print(
                f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
            sys.exit(1)

        tree_structure = generate_tree(path, use_gitignore=args.ignore)

        # Print to console
        print(tree_structure)

        # Save to output file if specified
        if args.output:
            write_to_file(tree_structure, args.output)
            print(f"Tree structure saved to '{args.output}'.")

        # Copy to clipboard if requested
        if args.copy:
            copy_to_clipboard(tree_structure)
            print("Tree structure copied to clipboard.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
