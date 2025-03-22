# 🤖 Iva - AI Code Assistant

Iva is an intelligent code assistant that helps you generate file structures and code based on natural language descriptions.

## Features

- Generate code and project structures from natural language descriptions
- Interactive CLI with rich formatting
- Smart bug fixing capabilities
- Project scaffolding
- Cross-platform support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ItzCyzmiX/Iva.git
cd Iva
```

2. Install the package:
```bash
pip install -e .
```

## Usage

Run the assistant:
```bash
iva
```

Or import in your code:
```python
from iva_generator import AIFileGenerator

generator = AIFileGenerator()
generator.run("Create a Flask API")
```

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt

## License

MIT License