from connectus.tools.structure.data import VariableData
from ...base import BaseNode
from .configuration import Configuration
import asyncpg
import asyncio

class TimeScaleDB(BaseNode, Configuration):
    def __init__(self, node_config: dict[str, any], stop_event: asyncio.Event):
        BaseNode.__init__(self, stop_event)
        Configuration.__init__(self, node_config)
        self.pool = None  # Connection pool

    async def connect(self):
        """Initialize the connection pool."""
        try:
            self.pool = await asyncpg.create_pool(self.url)  # Use connection pool
            async with self.pool.acquire() as conn:
                query = self._create_table(self.table_name, self.columns)
                await conn.execute(query)
        except Exception as e:
            print(f"An error occurred while connecting to the database: {e}")

    async def write(self, data: VariableData, table_name: str= None):
        """
        Insert data into the specified table with validation against the table's schema.

        Args:
            table_name (str): The name of the table to insert data into.
            data (list[dict[str, any]]): A list of dictionaries, where each dictionary represents a row to insert.
                                         Keys in the dictionary should match column names in the table.

        Raises:
            ValueError: If column names in the data do not match the table's schema.
        """
        table_name = table_name or self.table_name

        if not data:
            print("No data to write.")
            return
        
        data = data.plain_model()

        async with self.pool.acquire() as conn:
            try:
                # Fetch the table schema
                query = f"""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = $1;
                """
                result = await conn.fetch(query, table_name.lower())
                valid_columns = {row['column_name'] for row in result}

                # Get column names from the first dictionary in the data
                data_columns = set(data.keys())

                # Check for invalid columns
                invalid_columns = data_columns - valid_columns
                if invalid_columns:
                    await self._alter_table(conn, table_name, invalid_columns)

                # Prepare columns and placeholders
                column_names = ", ".join(data_columns)
                placeholders = ", ".join(f"${i+1}" for i in range(len(data_columns)))

                # Construct the query
                query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

                # Prepare the data for insertion
                values = [
                    tuple(str(data[col]) if col != 'timestamp' else data[col] for col in data_columns)
                ]

                # Execute the query for each row of data
                for value_set in values:
                    await conn.execute(query, *value_set)

            except ValueError as ve:
                print(f"Validation error: {ve}")
            except Exception as e:
                print(f"An error occurred while inserting data into {table_name}: {e}")

    async def disconnect(self):
        """Close the connection pool properly."""
        if self.pool:
            await self.pool.close()

    def read(self):
        pass

    def _create_table(self, name: str, columns: list[tuple[str, str]]):
        """
        Create a table with the given name and columns.
        
        Args:
            name (str): The name of the table to create.
            columns (list[tuple[str, str]]): A list of tuples, where each tuple contains a column name and its SQL type.
        
        Example:
            columns = [
                ('time', 'TIMESTAMPTZ NOT NULL'),
                ('exp_id', 'TEXT NOT NULL'),
                ('name', 'TEXT NOT NULL'),
                ('value', 'TEXT'),
                ('type', 'TEXT NOT NULL')
            ]
        """
        try:
            columns_def = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns])
            query = f"CREATE TABLE IF NOT EXISTS {name} ({columns_def});"
            return query
        except Exception as e:
            print(f"An error occurred while creating the table {name}: {e}")
            
    async def _alter_table(self, conn, table_name: str, new_columns: set[str]):
        """
        Alter the table to add new columns if they do not exist.
        """
        try:
            query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = $1;
            """
            result = await conn.fetch(query, table_name.lower())
            existing_columns = {row['column_name'] for row in result}

            columns_to_add = new_columns - existing_columns
            if not columns_to_add:
                return

            for column in columns_to_add:
                alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column} TEXT;"
                await conn.execute(alter_query)

        except Exception as e:
            print(f"An error occurred while altering the table {table_name}: {e}")