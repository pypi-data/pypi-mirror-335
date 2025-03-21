from pathlib import Path

from ..constants import ELBOW, TEE, PIPE_PREFIX, SPACE_PREFIX
from ..utils.gitignore import GitIgnoreFilter


def generate_tree(directory_path, prefix="", use_gitignore=False):
    """
    Generate a string representation of the directory structure.

    Args:
        directory_path (Path): Path to the directory
        prefix (str): Prefix for the current line
        use_gitignore (bool): Whether to use .gitignore rules

    Returns:
        str: String representation of the directory structure
    """
    # Convert to Path object if it's a string
    directory_path = Path(directory_path)

    # Get the directory name for the root level
    if prefix == "":  # Root level
        tree_str = f"{directory_path.name}/\n"
    else:
        tree_str = ""

    # Create gitignore filter if requested
    gitignore_filter = None
    if use_gitignore:
        gitignore_filter = GitIgnoreFilter(directory_path)

    # Get all entries in the directory
    entries = sorted(list(directory_path.iterdir()),
                     key=lambda e: (not e.is_dir(), e.name.lower()))

    # Filter out hidden files and directories (starting with .)
    entries = [e for e in entries if not e.name.startswith('.')]

    # Filter entries according to gitignore if requested
    if use_gitignore and gitignore_filter:
        entries = [e for e in entries if not gitignore_filter.is_ignored(e)]

    # Process each entry
    entries_count = len(entries)
    for i, entry in enumerate(entries):
        is_last = i == entries_count - 1
        connector = ELBOW if is_last else TEE

        # Add the current entry to the tree string
        tree_str += f"{prefix}{connector} {entry.name}"

        # Add a trailing slash for directories
        if entry.is_dir():
            tree_str += "/\n"

            # Extend prefix for the next level
            extension = SPACE_PREFIX if is_last else PIPE_PREFIX

            # Recursively process subdirectories
            tree_str += generate_tree(
                entry,
                prefix=f"{prefix}{extension}",
                use_gitignore=use_gitignore
            )
        else:
            tree_str += "\n"

    return tree_str
