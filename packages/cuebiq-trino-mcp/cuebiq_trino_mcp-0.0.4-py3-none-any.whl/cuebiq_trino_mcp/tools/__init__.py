"""
MCP tools for executing operations on Trino.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from mcp.server.fastmcp import Context, FastMCP

from cuebiq_trino_mcp.trino_client import TrinoClient


def register_trino_tools(mcp: FastMCP, client: TrinoClient) -> None:
    """
    Register Trino tools with the MCP server.

    Args:
        mcp: The MCP server instance.
        client: The Trino client instance.
    """

    @mcp.tool()
    def execute_query(
            sql: str,
            catalog: Optional[str] = None,
            schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a SQL query against Trino.
        Args:
            sql: The SQL query to execute.
            catalog: Optional catalog name to use for the query.
            schema: Optional schema name to use for the query.
        Returns:
            Dict[str, Any]: Query results including metadata.
        """
        logger.info(f"Executing query: {sql}")

        try:
            result = client.execute_query(sql, catalog, schema)

            # Format the result in a structured way
            formatted_result = {
                "query_id": result.query_id,
                "columns": result.columns,
                "row_count": result.row_count,
                "query_time_ms": result.query_time_ms
            }

            # Add preview of results (first 20 rows)
            preview_rows = []
            max_preview_rows = min(20, len(result.rows))

            for i in range(max_preview_rows):
                row_dict = {}
                for j, col in enumerate(result.columns):
                    row_dict[col] = result.rows[i][j]
                preview_rows.append(row_dict)

            formatted_result["preview_rows"] = preview_rows

            # Include a resource path for full results
            formatted_result["resource_path"] = f"trino://query/{result.query_id}"

            cancel_query(result.query_id)

            return formatted_result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Query execution failed: {error_msg}")
            return {
                "error": error_msg,
                "query": sql
            }

    @mcp.tool()
    def cancel_query(query_id: str) -> Dict[str, Any]:
        """
        Cancel a running query.

        Args:
            query_id: ID of the query to cancel.

        Returns:
            Dict[str, Any]: Result of the cancellation operation.
        """
        logger.info(f"Cancelling query: {query_id}")

        try:
            success = client.cancel_query(query_id)

            if success:
                return {
                    "success": True,
                    "message": f"Query {query_id} cancelled successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to cancel query {query_id}"
                }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Query cancellation failed: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "query_id": query_id
            }


