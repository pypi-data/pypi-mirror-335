from typing import Any, Dict

import numpy as np
import pandas as pd
from kedro.extras.datasets.pandas import SQLTableDataSet
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

class PostgresUpsertFactory:
    def build(self, constraint, overwrite_columns):
        if not isinstance(overwrite_columns, bool):
            raise ValueError(
                f"The 'overwrite_columns' parameter must be True or False, but received: {overwrite_columns}"
            )
        def postgres_upsert(table, conn, keys, dataframe_values):
            """
            Example
            -------
            test = pd.DataFrame({"name": ["Teste"]})

            upsert_method_factory = PostgresUpsertFactory()
            upsert_method = upsert_method_factory.build('roles_unique_name')
            df.to_sql('roles',
                engine,schema='public',
                if_exists='append',
                index=False,
                method=upsert_method)

            See
            ----
            https://stackoverflow.com/questions/55187884/insert-into-postgresql-table-from-pandas-with-on-conflict-update
            https://pandas.pydata.org/docs/user_guide/io.html#io-sql-method
            """
            data = [dict(zip(keys, row)) for row in dataframe_values]

            insert_statement = insert(table.table).values(data)
            if overwrite_columns == True:
                upsert_statement = insert_statement.on_conflict_do_update(
                    constraint=constraint,
                    set_={c.key: c for c in insert_statement.excluded},
                )
            elif overwrite_columns == False:
                upsert_statement = insert_statement.on_conflict_do_update(
                    constraint=constraint,
                    set_={c.key: func.coalesce(table.table.columns[c.key], c) for c in insert_statement.excluded},
                )
            conn.execute(upsert_statement)

        return postgres_upsert

class PostgresTableUpsertDataSet(SQLTableDataSet):
    def __init__(
        self,
        table_name: str,
        credentials: Dict[str, Any],
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
    ) -> None:
        self.constraint = save_args.pop("constraint")
        self.chunk_size = save_args.pop("chunk_size", None)
        self.overwrite_columns = save_args.pop("overwrite_columns", True)
        super().__init__(
            table_name, credentials, load_args, save_args
        )

    def _save(self, data: pd.DataFrame) -> None:
        upsert_method_factory = PostgresUpsertFactory()
        upsert_accounts_method = upsert_method_factory.build(self.constraint, self.overwrite_columns)
        engine = self.engines[self._connection_str]  # type: ignore

        if self.chunk_size and self.chunk_size > 0:
            for chunk in np.array_split(data, len(data) // self.chunk_size + 1):
                chunk.to_sql(con=engine, **self._save_args, method=upsert_accounts_method)
        else:
            data.to_sql(con=engine, **self._save_args, method=upsert_accounts_method)
