# tree3

![Tree3-](https://repository-images.githubusercontent.com/950726237/436e5063-14f9-42a0-923e-b22c8256ce1f)

[![PyPI](https://img.shields.io/pypi/v/tree3)](https://pypi.org/project/tree3/) ![License](https://img.shields.io/pypi/l/tree3) [![GitHub Repo stars](https://img.shields.io/github/stars/amirmazinani/tree3?style=flat&label=github%20stars&color=%2357d9a3)](https://github.com/amirmazinani/tree3)

A command-line utility to display and create directory structures.

## Installation

```bash
pip install tree3
```

## Usage

tree3 provides various options for displaying and managing directory structures.

### Display directory structure

```bash
tree3 [path]
```
#### Example output:
```
/
├── tree3/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── builder.py
│   │   ├── parser.py
│   │   └── tree.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── clipboard.py
│   │   ├── file_utils.py
│   │   └── gitignore.py
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── config.py
│   └── constants.py
├── LICENSE
├── pyproject.toml
├── README.md
└── setup.py
```

### Save directory structure to file

```bash
tree3 [path] -o output.txt
```

### Create directories from structure file

```bash
tree3 -i input.txt
```

### Respect .gitignore rules

```bash
tree3 -g
```

### Copy structure to clipboard

```bash
tree3 -c
```

### Get help

```bash
tree3 -h
```

## Examples

### Example 1: Display current directory structure

```bash
tree3
```

### Example 2: Save structure to file and copy to clipboard

```bash
tree3 myproject -o project-structure.txt -c
```

### Example 3: Create directory structure from file

```bash
tree3 -i project-structure.txt
```

## Contributing

Feel free to open issues and pull requests on the [GitHub repository](https://github.com/amirmazinani/tree3).

## License

This project is licensed under the MIT License.

---

Built with ♥ by [Amir Mazinani](https://amirmazinani.ir)!