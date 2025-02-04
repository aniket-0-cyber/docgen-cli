# DocGen CLI

An AI-powered documentation generator that automatically creates comprehensive documentation for any programming language.

## Features

- 🤖 AI-powered documentation generation
- 🌐 Language-agnostic code analysis
- 📝 Markdown and docstring generation
- 🔄 Git integration for tracking code changes
- ⚡ Asynchronous batch processing
- 💾 Smart caching system
- 🔑 API key management
- 📊 Usage tracking

## Installation
bash
pip install docgen-cli

## Quick Start

1. Get your API key from our website
2. Login with your API key:

```bash
docgen auth login --key YOUR_API_KEY
```

3. Generate documentation for a file or directory:

```bash
docgen generate -f path/to/file.py
# or
docgen generate --current-dir
```

4. Update documentation for changed files:

```bash
docgen update
```

## Usage

### Basic Commands

- `docgen generate`: Generate documentation for files or directories
- `docgen update`: Update docs for changed files (Git-aware)
- `docgen analyze`: Analyze code structure and complexity
- `docgen auth`: Manage API authentication
- `docgen config`: Configure settings
- `docgen clean`: Remove generated documentation

### Examples

```bash
# Generate docs for current directory
docgen generate --current-dir

# Generate docs for a specific file
docgen g -f src/main.py

# Update documentation for changed files
docgen update

# Configure output format
docgen config output_format html
```

## Configuration

Create a `.docgen.json` file in your project root:

```json
{
    "output_format": "markdown",
    "output_dir": "docs",
    "exclude_patterns": ["**/test/*", "**/*.test.*"],
    "language_settings": {
        "python": {
            "docstring_style": "google"
        }
    }
}
```

## Supported Languages

- Python
- JavaScript/TypeScript
- Java
- And more...

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
