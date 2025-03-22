# 🤖 Iva - AI Code Assistant

[![PyPI version](https://badge.fury.io/py/iva-generator.svg)](https://badge.fury.io/py/iva-generator)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Iva is a powerful AI-powered code assistant that helps developers generate code and project structures using natural language descriptions.

## ✨ Features

-   🚀 Generate complete project structures from natural language
-   💻 Interactive CLI with rich formatting
-   🔧 Smart code generation and bug fixing
-   📁 Project scaffolding for various frameworks
-   🌐 Cross-platform support

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install iva-generator
```

### From Source

1. Clone the repository:

```bash
git clone https://github.com/ItzCyzmiX/Iva.git
cd Iva
```

2. Install in development mode:

```bash
pip install -e .
```

## 🚀 Quick Start

### Using the CLI

```bash
# If installed from PyPI
iva

# If installed from source
python -m iva
```

### Using in Your Code

```python
from iva_generator import AIFileGenerator

# Initialize the generator
generator = AIFileGenerator()

# Generate code
generator.run("Create a Flask API with authentication", output_dir="my_project")
```

## 💡 Examples

### Creating a Basic API

```bash
$ iva
What would you like me to do? Create a FastAPI backend with user authentication
Output directory: ./my_api
✅ Files generated successfully!
```

### Generating a React Component

```bash
$ iva
What would you like me to do? Create a React todo list component with TypeScript
Output directory: ./components
✅ Files generated successfully!
```

## 🔑 Environment Variables

1. Create a `.env` file in your working directory (where you'll run the `iva` command):

```env
GROQ_API_KEY=your-api-key-here
```

2. Or set environment variables in your system:

Windows (PowerShell):

```powershell
$env:GROQ_API_KEY="your-api-key-here"
```

Windows (Command Prompt):

```cmd
set GROQ_API_KEY=your-api-key-here
```

Linux/MacOS:

```bash
export GROQ_API_KEY="your-api-key-here"
```

3. Or set them in your Python code:

```python
import os
os.environ["GROQ_API_KEY"] = "your-api-key-here"

from iva_generator import AIFileGenerator
generator = AIFileGenerator()
```

> **Note**: Get your Groq API key from [Groq's website](https://groq.com/). Never commit your `.env` file or share your API key.

> **Tip**: For permanent setup on Windows, you can set the environment variable through:
>
> 1. Search for "Environment Variables" in Windows
> 2. Click "Environment Variables..."
> 3. Under "User variables" click "New"
> 4. Variable name: `GROQ_API_KEY`
> 5. Variable value: `your-api-key-here`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

-   Built with [LangChain](https://github.com/hwchase17/langchain)
-   Powered by [Groq](https://groq.com/)

## 📫 Contact

ItzCyzmiX - [@ItzCyzmiX](https://github.com/ItzCyzmiX) - itzmedigamingx@gmail.com

Project Link: [https://github.com/ItzCyzmiX/Iva](https://github.com/ItzCyzmiX/Iva)
