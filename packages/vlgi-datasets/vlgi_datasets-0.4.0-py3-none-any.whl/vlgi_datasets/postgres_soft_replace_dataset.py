from typing import Any, Dict

import pandas as pd
from kedro.extras.datasets.pandas import SQLTableDataSet
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy

class PostgresSoftReplaceFactory:
    def build(self):
        def postgres_upsert(table, conn, keys, dataframe_values):
            """
            Example
            -------
            test = pd.DataFrame({"name": ["Teste"]})

            replace_method_factory = PostgresSoftReplaceFactory()
            replace_method = replace_method_factory.build('roles_unique_name')
            df.to_sql('roles',
                engine,schema='public',
                if_exists='append',
                index=False,
                method=replace_method)

            See
            ----
            https://stackoverflow.com/questions/55187884/insert-into-postgresql-table-from-pandas-with-on-conflict-update
            https://pandas.pydata.org/docs/user_guide/io.html#io-sql-method
            """
            delete_statement = sqlalchemy.delete(table.table)
            conn.execute(delete_statement)

            data = [dict(zip(keys, row)) for row in dataframe_values]
            insert_statement = insert(table.table).values(data)
            conn.execute(insert_statement)

        return postgres_upsert

class PostgresSoftReplaceDataSet(SQLTableDataSet):
    def __init__(
        self,
        table_name: str,
        credentials: Dict[str, Any],
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
    ) -> None:
        super().__init__(
            table_name, credentials, load_args, save_args
        )

    def _save(self, data: pd.DataFrame) -> None:
        replace_method_factory = PostgresSoftReplaceFactory()
        replace_method = replace_method_factory.build()
        engine = self.engines[self._connection_str]  # type: ignore
        data.to_sql(con=engine, **self._save_args, method=replace_method)
