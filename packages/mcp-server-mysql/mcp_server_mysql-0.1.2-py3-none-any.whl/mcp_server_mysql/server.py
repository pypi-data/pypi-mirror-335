import mysql.connector
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from pydantic_settings import BaseSettings

class MySQLSettings(BaseSettings):
    MYSQL_HOST: str = Field(description="MySQL host")
    MYSQL_PORT: str = Field(description="MySQL port")
    MYSQL_USER: str = Field(description="MySQL user")
    MYSQL_PASSWORD: str = Field(description="MySQL password")
    MYSQL_DATABASE: str = Field(description="MySQL database name")

try:
    settings = MySQLSettings()
except Exception as e:
    raise ValueError(f"Failed to load MySQL settings: {e}")

conn = mysql.connector.connect(
    host=settings.MYSQL_HOST,
    port=settings.MYSQL_PORT,
    user=settings.MYSQL_USER,
    password=settings.MYSQL_PASSWORD,
    database=settings.MYSQL_DATABASE,
)
conn.autocommit = False

mcp = FastMCP(
    "MySQL",
    instructions="You are a MySQL database manager. You can execute queries, create tables, and insert data into the database.",
)


@mcp.tool()
def execute_query(query: str) -> str:
    """Execute an arbitrary SQL query. Returns results for SELECT, or a success message for others."""
    cursor = conn.cursor()
    cursor.execute(query)
    command = query.strip().split()[0].lower()
    if command == "select" or command == "show" or command == "describe":
        rows = cursor.fetchall()
        return str(rows)
    else:
        conn.commit()
        return f"Query executed successfully. Rows affected: {cursor.rowcount}"


@mcp.tool()
def create_table(name: str, schema: str) -> str:
    """Create a new table with the given name and schema (column definitions)."""
    cursor = conn.cursor()
    query = f"CREATE TABLE {name} ({schema})"
    cursor.execute(query)
    conn.commit()
    return f"Table '{name}' created."


@mcp.tool()
def insert_data(table: str, data: dict) -> str:
    """Insert a row of data into the specified table. `data` is a dict of column values."""
    cursor = conn.cursor()
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = list(data.values())

    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    return f"Data inserted into table '{table}'. Row ID: {cursor.lastrowid}"


@mcp.tool()
def fetch_data(query: str) -> str:
    """Fetch data by executing a SELECT query and returning the results."""
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return str(rows)


@mcp.tool()
def list_tables() -> str:
    """List all tables in the current database."""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    return str([table[0] for table in tables])


@mcp.tool()
def describe_table(table: str) -> str:
    """Show the structure of a specific table."""
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table}")
    columns = cursor.fetchall()
    return str(columns)


if __name__ == "__main__":
    mcp.run()
