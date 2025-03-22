"""
Cortellis MCP Server main entry point.
"""
import os
import sys
from mcp.server.fastmcp import FastMCP
from . import search_drugs, explore_ontology

def main():
    # Check required environment variables
    required_vars = ['CORTELLIS_USERNAME', 'CORTELLIS_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    # Initialize the MCP server
    mcp = FastMCP("Cortellis MCP")
    
    # Register tools
    mcp.tool()(search_drugs)
    mcp.tool()(explore_ontology)
    
    print("Initializing Cortellis MCP Server...")
    # Start the server - this will block and listen for JSON-RPC messages
    mcp.run()

if __name__ == "__main__":
    main() 