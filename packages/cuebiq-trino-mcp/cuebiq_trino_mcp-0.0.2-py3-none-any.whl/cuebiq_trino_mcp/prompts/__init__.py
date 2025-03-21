from mcp.server.fastmcp import FastMCP

def register_trino_prompts(mcp: FastMCP) -> None:
    """
    Register Trino resources with the MCP server.

    Args:
        mcp: The MCP server instance.
        client: The Trino client instance.
    """


    @mcp.prompt()
    def describe_table() -> str:
        response =  """You are a SQL optimization expert. When asked to describe or summarize a table, avoid full table scans as they are inefficient. Follow these guidelines:
            1. **Avoid `SELECT COUNT(*)`**: Instead of scanning the entire table, use metadata queries (e.g., system catalogs, `INFORMATION_SCHEMA`) to retrieve table statistics efficiently.
            2. **Retrieve column information**: Use queries like:
                ```sql
                    SELECT * FROM glue.information_schema.columns
                    WHERE table_catalog = glue
                    AND table_schema = '{schema name}'
                    AND table_name = '{table name}';"""

        return response

   