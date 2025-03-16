# Mathematica Documentation MCP server

## General & Usage

Made with [mcp-python-sdk](https://github.com/modelcontextprotocol/python-sdk)

> [!IMPORTANT]  
> if you are still using FastMCP version of this mcp server, please consider pull this repo again and update to newer versions as FastMCP is already deprecated.

Requirements: `pip install -r requirements.txt` and have Mathematica installed (or at least `wolframscript` callable from terminal, e.g. via [free wolfram engine for developers](https://www.wolfram.com/engine/index.php.en)).

Run `mcp dev path/to/mcp-mma-doc.py` to initialize the server.

Run `mcp install path/to/mcp-mma-doc.py` to install to claude or add following to claude/cline config:

```json
"mathematica-docs": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "mcp",
        "run",
        "/path/to/mcp-mma-doc.py"
      ]
    }
```

> [!NOTE]
> Currently using `uv` with `mcp` seems to break certain Linux/macOS version of Claude-desktop, you might need to set as:
> ```json
> "mathematica-docs": {
>       "command": "/path/to/mcp",
>       "args": [
>         "run",
>         "/path/to/mcp-mma-doc.py"
>       ]
>     }
> ```
> instead, with `/path/to/mcp` got from running `which mcp` in terminal

## Custom wolframscript install path

If you need custom path to `wolframscript`, or it is not in system path, you can set via environmental variable by
```bash
export WOLFRAMSCRIPT_PATH="/usr/bin/wolframscript"
```
or set as an `env` key in mcp config
```json
"mathematica-docs": {
      "command": ...,
      "args": ....
      "env": {
        "WOLFRAMSCRIPT_PATH": "/usr/bin/wolframscript"
      }
    }
```

## Tools

The plugin provides the following commands:

- get_docs: support factory functions, function via an addon, and function via a package.
  - Basic usage: get_docs("Plot")
  - With package: get_docs("WeightSystem", packages=["LieART"])
  - With addon: get_docs("FCFeynmanParametrize", packages=["FeynCalc"], load_addons=["FeynArts"])
- list_package_symbols: list all symbols/functions in a package.
  - Basic usage: list_package_symbols("FeynCalc")

## Known issues

- If you see things like `INFO Processing request of type __init__.py:431 ListToolsRequest` in cline, you can ignore them as this will not affect it from working, this is because cline parse tool list together with console debug infos, and current python-sdk cannot disable console messages. This will not affect any function calling part other than seeing this warning.
- Some MMA docs may contain complex styling format, and is not easy to remove with simple regex, your llm may be influenced by this, please instruct it to ignore the styling format and write in InputForm only.

## Screenshots

![screenshot](image.png)
