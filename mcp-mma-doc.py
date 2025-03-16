from mcp.server.fastmcp import FastMCP
from typing import Optional, List
from pydantic import Field
import subprocess

wolframscript='wolframscript'

# Create the MCP server
mcp = FastMCP(
    "Mathematica Documentation Search 📚",
    dependencies=["pydantic"]
)

def run_wolframscript(cmd: str) -> str:
    """Run a wolframscript command and return its output"""
    try:
        full_cmd = [wolframscript, '-code', cmd]
        
        # Run the command and capture output
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing Mathematica command: {e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def get_docs(
    symbol: str = Field(..., description="The Mathematica symbol or function to look up (e.g., 'Plot', 'FCFeynmanParametrize')"),
    packages: Optional[List[str]] = Field(
        None,
        description="Optional list of packages to load before looking up documentation (e.g., ['FeynCalc'])"
    ),
    load_addons: Optional[List[str]] = Field(
        None,
        description="Optional list of addons to load (e.g., ['FeynArts'])"
    )
) -> str:
    """
    Get documentation for a Mathematica symbol or function using wolframscript CLI.
    Can optionally load packages and addons before looking up documentation.
    
    Examples:
    - Basic usage: get_docs("Plot")
    - With package: get_docs("WeightSystem", packages=["LieART"])
    - With addon: get_docs("FCFeynmanParametrize", packages=["FeynCalc"], load_addons=["FeynArts"])
    """
    # Build the Mathematica command
    cmd_parts = []
    
    # Add addons if specified
    if load_addons:
        addons_list = "{" + ",".join(f'"{addon}"' for addon in load_addons) + "}"
        cmd_parts.append(f'$LoadAddOns = {addons_list};')
    
    # Add packages to load
    if packages:
        for package in packages:
            cmd_parts.append(f'<< {package}`')
    
    # Add the documentation query
    cmd_parts.append(f'?{symbol}')
    
    # Join all parts with semicolons
    cmd = "; ".join(cmd_parts)
    
    # Get the documentation
    result = run_wolframscript(cmd)
    
    if not result:
        return f"No documentation found for {symbol}. Make sure the symbol exists and any required packages are specified."
        
    # Format the output
    markdown = f"# Documentation for `{symbol}`\n\n"
    markdown += "```\n"  # Use code block for preserving formatting
    markdown += result
    markdown += "\n```\n\n**Notices for AI assistents: The Doc above may contain format related functions like `DisplayForm[...]` or some `*Box[...]` e.g. RowBox, StyleBox, they are NOT relevant for getting the final result and SHOULD NOT be included in your final code!!! The reason is because Mathematica will automatically render InputForm or StandardForm into this DisplayForm in their frontend, so the users are not suppose to see and use these 'format related functions'. So please ALWAYS FIRST convert the doc from this 'unrendered DisplayForm' format to StandardForm in your mind and always ONLY write your code in StandardForm to user.**\n\n"
    
    # Add loading information if applicable
    if packages or load_addons:
        markdown += "\n*Documentation retrieved after loading:*\n"
        if packages:
            markdown += f"- Packages: {', '.join(packages)}\n"
        if load_addons:
            markdown += f"- Addons: {', '.join(load_addons)}\n"
            
    return markdown

@mcp.tool()
async def list_package_symbols(
    package: str = Field(..., description="The Mathematica package to list symbols from (e.g., 'FeynCalc')"),
    load_addons: Optional[List[str]] = Field(
        None,
        description="Optional list of addons to load before listing symbols (e.g., ['FeynArts'])"
    )
) -> str:
    """
    List all available symbols from a specific Mathematica package using wolframscript CLI.
    
    Example:
    - List FeynCalc symbols: list_package_symbols("FeynCalc", load_addons=["FeynArts"])
    """
    # Build the Mathematica command
    cmd_parts = []
    
    # Add addons if specified
    if load_addons:
        addons_list = "{" + ",".join(f'"{addon}"' for addon in load_addons) + "}"
        cmd_parts.append(f'$LoadAddOns = {addons_list};')
    
    # Load package and get symbols
    cmd_parts.extend([
        f'<< {package}`',
        f'Names["{package}`*"]'
    ])
    
    # Join commands
    cmd = "; ".join(cmd_parts)
    
    # Get the symbols
    result = run_wolframscript(cmd)
    
    if not result or result.startswith("Error"):
        return f"Error listing symbols from package {package}: {result}"
        
    # Parse the output (it comes as a Mathematica list)
    # Remove curly braces and split by commas
    symbols = result.strip("{}").split(",")
    symbols = [s.strip().strip('"') for s in symbols]
    
    # Format the output
    markdown = f"# Symbols available in {package}\n\n"
    for symbol in sorted(symbols):
        markdown += f"- `{symbol}`\n"
        
    if load_addons:
        markdown += f"\n*Symbols listed after loading addons: {', '.join(load_addons)}*\n"
            
    return markdown