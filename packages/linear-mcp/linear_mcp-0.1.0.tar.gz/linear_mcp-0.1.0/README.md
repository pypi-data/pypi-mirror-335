# Linear MCP

A Linear API integration for MCP.

## Installation


### Using pipx (Recommended for Global Installation)

If you want to install the package globally and use it as a command-line tool, you can use `pipx`:

```bash
# MacOS
brew install pipx

# Linux
apt install pipx

# Set up PATH
pipx ensurepath
```

Then, install the `linear-mcp` command globally using `pipx`:
```
pipx install -e . --force
```

After installation, you can run the tool from anywhere using:
```bash
linear-mcp --linear-api-key "..."
```

### Cursor Setup

If you have installed the `linear-mcp` command globally, you can configure an MCP server in Cursor by creating a new MCP server with the following command:

`linear-mcp --linear-api-key "..."`

You may have to globally path the `linear-mcp` command.
Execute `which linear-mcp` to determine the full path to the command, for example:

`/Users/USER/.local/bin/linear-mcp --linear-api-key "..."`

### Windsurf Setup

If you have installed the `linear-mcp` command globally, you can create a Custom MCP server with configuration like the following:

```json
{
  "mcpServers": {
    "linear": {
      "command": "linear-mcp",
      "args": [
        "--linear-api-key",
        "..."
      ]
    }
  }
}
```

### Using Docker

```bash
# Build the image
docker build -t linear-mcp .

# Run the container
docker run -it --rm -e LINEAR_API_KEY=... linear-mcp
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/context-labs/linear-mcp
cd linear-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install build dependencies:
```bash
pip install -r requirements-build.txt
```

4. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Install the package in development mode:
```bash
pip install -e .
```

### Development: Local Installation Using Virtual Environment

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install build dependencies:
```bash
pip install -r requirements-build.txt
```

3. Install the package:
```bash
# Install in development mode with all development dependencies
pip install -e ".[dev]"

# Or install in production mode
pip install -e .
```

## License

MIT License
