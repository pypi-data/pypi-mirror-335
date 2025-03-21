from __future__ import annotations
from typing import Optional, List
from langchain.utilities.sql_database import SQLDatabase as SQL
from sqlalchemy import create_engine


class SQLDatabase(SQL):
    @classmethod
    def from_uri_args(
            cls,
            database_uri: str,
            engine_args: Optional[dict] = None,
            schema: Optional[str] = None,
            metadata: Optional[List[str]] = None,
            ignore_tables: Optional[List[str]] = None,
            include_tables: Optional[List[str]] = None,
            sample_rows_in_table_info: int = 3,
            indexes_in_table_info: bool = False,
            custom_table_info: Optional[dict] = None,
            view_support: bool = False,
            max_string_length: int = 300,
    ) -> SQLDatabase:
        """Construct a SQLAlchemy engine from URI."""
        _engine_args = engine_args or {}
        _schema = schema or None
        return cls(create_engine(database_uri, **_engine_args),
                   _schema,
                   metadata,
                   ignore_tables,
                   include_tables,
                   sample_rows_in_table_info,
                   indexes_in_table_info,
                   custom_table_info,
                   view_support,
                   max_string_length)
