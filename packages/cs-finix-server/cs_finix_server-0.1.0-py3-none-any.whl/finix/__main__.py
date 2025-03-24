# finix/__main__.py
from mcp.server.fastmcp import FastMCP
import yaml

mcp = FastMCP("Creditsafe Finix App")

def load_yaml_config(file_path: str = "portfolios-api.yaml") -> dict:
    """Load configuration from a YAML file."""
    print(f"Loading configuration from {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return {}

@mcp.tool()
def get_api_docs(name: str) -> str:
    print(f"Getting API docs for {name}")
    return load_yaml_config("portfolios-api.yaml")

def main():
    """Start the Creditsafe Finix MCP server"""
    print("Starting Creditsafe Finix MCP Server...")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
