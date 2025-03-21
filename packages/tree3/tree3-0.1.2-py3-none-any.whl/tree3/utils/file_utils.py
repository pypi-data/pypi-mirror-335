def read_file(file_path):
    """
    Read content from a file.

    Args:
        file_path (str or Path): Path to the file

    Returns:
        str: Content of the file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def write_to_file(content, file_path):
    """
    Write content to a file.

    Args:
        content (str): Content to write
        file_path (str or Path): Path to the file
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
