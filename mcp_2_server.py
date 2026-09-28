from mcp.server.mcpserver import MCPServer

# Initialize the MCP server using the 2.x syntax
mcp = MCPServer("user-db-mcp")

@mcp.tool()
def get_user_schema() -> str:
    """Returns the database schema for the users table."""
    return "TABLE users (id INT PRIMARY KEY, username VARCHAR(50), email VARCHAR(50), is_active BOOLEAN)"

@mcp.tool()
def query_active_users() -> list[dict]:
    """Securely fetches a list of active users."""
    # In a real app, this queries the actual DB.
    return [
        {"id": 1, "username": "alice_admin", "email": "alice@company.com"},
        {"id": 2, "username": "bob_dev", "email": "bob@company.com"}
    ]

if __name__ == "__main__":
    mcp.run()
