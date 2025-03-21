from .parser import TreeParser
from ..utils.file_utils import read_file


def build_from_file(input_file):
    """
    Build directory structure from an input file.

    Args:
        input_file (str or Path): Path to the input file
    """
    # Read the input file
    tree_content = read_file(input_file)

    # Parse the tree content
    parser = TreeParser(tree_content)
    root_dir, paths = parser.parse()

    # Create directories and files
    for path in paths:
        # Simple heuristic to detect files (has extension)
        if '.' in path.name:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            # Create an empty file if it doesn't exist
            if not path.exists():
                path.touch()
        else:
            # Create directory if it doesn't exist
            path.mkdir(parents=True, exist_ok=True)

    return root_dir, paths
