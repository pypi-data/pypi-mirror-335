# Cmd Clever

A command-line tool for generating terminal commands using AI.

## Installation

```bash
pip install cmd-clever
```

## Usage

### Command-line Arguments

```bash
# Basic usage with a query
cmd-clever 查找大于100MB的日志文件

# Specify API key and base URL
cmd-clever --api-key your-api-key --api-base your-api-base 查找最近修改的文件

# Use a different model ID
cmd-clever --model-id different-model-id 创建一个新的目录并将文件移动到其中

# Disable streaming output
cmd-clever --no-stream 查找包含特定文本的文件
```

### Interactive Mode

If you don't provide a query, Cmd Clever enters interactive mode:

```bash
cmd-clever
```

You can then input your queries one by one and get responses. Type "exit" or "quit" to leave interactive mode.

### Environment Variables

Cmd Clever looks for the following environment variables:

- `AGNO_API_KEY`: Your API key
- `AGNO_API_BASE`: Your API base URL

You can set these in your shell configuration (e.g., `.bashrc`, `.zshrc`) to avoid specifying them on each run:

```bash
export AGNO_API_KEY="your-api-key"
export AGNO_API_BASE="your-api-base"
```

## Features

- Accepts queries in Chinese
- Generates safe and reliable terminal commands
- Automatically adapts commands for Linux/macOS
- Warns about potentially dangerous operations
- Supports command explanations
- Interactive and one-off query modes

## License

MIT 