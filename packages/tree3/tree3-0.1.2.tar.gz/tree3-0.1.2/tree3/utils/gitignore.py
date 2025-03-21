import fnmatch


class GitIgnoreFilter:
    """Filter for ignoring files and directories based on .gitignore rules."""

    def __init__(self, root_dir):
        """
        Initialize the GitIgnore filter.

        Args:
            root_dir (Path): Root directory for the tree
        """
        self.root_dir = root_dir
        self.rules = []
        self.default_ignores = [
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            ".DS_Store"
        ]

        # Load rules from .gitignore if it exists
        gitignore_path = root_dir / '.gitignore'
        if gitignore_path.exists():
            self._load_rules(gitignore_path)

        # Add default ignores that most Python projects would want
        for pattern in self.default_ignores:
            self.rules.append((pattern, False))

    def _load_rules(self, gitignore_path):
        """
        Load rules from a .gitignore file.

        Args:
            gitignore_path (Path): Path to the .gitignore file
        """
        with open(gitignore_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Process the rule
                is_negation = line.startswith('!')
                if is_negation:
                    line = line[1:].strip()

                self.rules.append((line, is_negation))

    def is_ignored(self, path):
        """
        Check if a path should be ignored.

        Args:
            path (Path): Path to check

        Returns:
            bool: True if path should be ignored, False otherwise
        """
        # Convert path to relative path from root
        rel_path = path.relative_to(self.root_dir)
        rel_path_str = str(rel_path).replace('\\', '/')

        # Check if path or any of its parts matches __pycache__
        # or other special directories
        path_parts = rel_path_str.split('/')
        for part in path_parts:
            if (part == '__pycache__'
                    or part.endswith('.pyc')
                    or part.endswith('.pyo')
                    or part.endswith('.pyd')):
                return True

        # Special case for directories - we need to check with trailing slash
        is_dir = path.is_dir()
        dir_path_str = f"{rel_path_str}/" if is_dir else None

        # Initialize ignored status
        ignored = False

        # Apply rules in order
        for pattern, is_negation in self.rules:
            matched = False

            # Clean pattern and prepare for matching
            clean_pattern = pattern.rstrip('/')

            # Check if pattern starts with /
            # which means it should match from project root
            if pattern.startswith('/'):
                pattern = pattern[1:]  # Remove leading /
                # Match exact path from root
                matched = self._match_path(pattern, rel_path_str) or \
                    (is_dir and self._match_path(pattern, dir_path_str))
            else:
                # Check if the pattern matches the full path
                matched = self._match_path(pattern, rel_path_str) or \
                    (is_dir and self._match_path(pattern, dir_path_str))

                # If not matched directly, check each directory level
                # (for patterns that should match anywhere)
                if not matched:
                    for i in range(len(path_parts)):
                        subpath = '/'.join(path_parts[i:])
                        if self._match_path(pattern, subpath):
                            matched = True
                            break

            # If matched, update ignored status based on negation
            if matched:
                ignored = not is_negation

        return ignored

    def _match_path(self, pattern, path_str):
        """
        Check if a pattern matches a path using fnmatch-style globbing.

        Args:
            pattern (str): GitIgnore pattern
            path_str (str): Path string to check

        Returns:
            bool: True if the pattern matches the path
        """
        if not path_str:
            return False

        # Check exact match first
        if pattern == path_str:
            return True

        # Handle directory-only pattern (ending with /)
        if pattern.endswith('/'):
            if not path_str.endswith('/'):
                path_str_with_slash = path_str + '/'
            else:
                path_str_with_slash = path_str
            # Remove trailing slash for matching
            pattern_without_slash = pattern[:-1]

            # Try matching with and without trailing slash
            if (fnmatch.fnmatch(path_str_with_slash, pattern)
                    or fnmatch.fnmatch(path_str, pattern_without_slash)):
                return True

        # Special handling for patterns with **/
        if '**/' in pattern:
            parts = pattern.split('**/')
            if len(parts) == 2:
                # Handle /**/pattern (matches any level)
                prefix, suffix = parts
                if not prefix or path_str.startswith(prefix):
                    # Check if any part of the path matches the suffix
                    path_parts = path_str.split('/')
                    for i in range(len(path_parts)):
                        subpath = '/'.join(path_parts[i:])
                        if fnmatch.fnmatch(subpath, suffix):
                            return True

        # Standard glob matching
        return fnmatch.fnmatch(path_str, pattern)
