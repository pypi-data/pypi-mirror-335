from dataclasses import dataclass
import textwrap
import time
from typing import Optional, cast

from relationalai.clients.snowflake import Provider

@dataclass
class Task:
    provider: Provider
    name: str
    database: str
    schema: str
    procedure: str
    last_execution_time: Optional[str] = None
    logs_table: Optional[str] = None

    def create(self, args=[], warehouse='MAIN_WH'):
        arg_string = ", ".join(f"'{arg}'" if isinstance(arg, str) else str(arg) for arg in args)
        sql_query = textwrap.dedent(f"""
        CREATE OR REPLACE TASK {self.database}.{self.schema}.{self.name}
        WAREHOUSE = {warehouse}
        AS
        CALL {self.database}.{self.schema}.{self.procedure}({arg_string});
        """)
        return self.provider.sql(sql_query)
    
    def exec_sync(self, log=print):
        log("Task created.")
        self.last_execution_time = self.get_current_timestamp()
        log("Executing task...")
        self.execute()
        log("Polling task...")
        return self.poll(self.last_execution_time, log=log)

    def execute(self):
        self.last_execution_time = self.get_current_timestamp()
        sql_query = f"EXECUTE TASK {self.database}.{self.schema}.{self.name};"
        return self.provider.sql(sql_query)

    def delete(self):
        sql_query = f"""
        DROP TASK {self.database}.{self.schema}.{self.name};
        """
        try:
            return self.provider.sql(sql_query)
        except Exception as e:
            if "does not exist" in str(e).lower():
                return None
            raise e
    
    def get_current_timestamp(self) -> str:
        sql_query = "SELECT CURRENT_TIMESTAMP() AS ts;"
        response = self.provider.sql(sql_query)
        return cast(str, response[0]["TS"])
    
    def check(self, scheduled_after=None):
        if scheduled_after is None:
            scheduled_after = self.last_execution_time
        sql_query = f"""
        SELECT *
        FROM TABLE(SANDBOX.INFORMATION_SCHEMA.TASK_HISTORY(
            SCHEDULED_TIME_RANGE_START => CAST(DATEADD('second', -1, TIMESTAMP '{scheduled_after}') AS TIMESTAMP_LTZ),
            TASK_NAME => '{self.name}'
        ));
        """
        return self.provider.sql(sql_query)

    def poll(self, scheduled_after = None, timeout=300, interval=5, log=print):
        if scheduled_after is None:
            scheduled_after = self.last_execution_time
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = cast(list, self.check(scheduled_after))
            if response:
                log("Task scheduled...")
                latest = response[-1]
                if latest["COMPLETED_TIME"]:
                    log("Task completed")
                    return latest.as_dict()
            else:
                log("Task not found in history yet...")
            time.sleep(interval)
        log("Timeout reached. Task not found in history.")
        return None
    
    def get_server_logs(self, filename:str, table_name: Optional[str] = None, all=False, log=print):
        "Save logs from Snowflake to a local SQLite database."
        if table_name is None:
            table_name = self.logs_table or "logs"
        if not self.logs_table:
            raise ValueError("Logs table not provided.")

        # if your table doesn't have a `timestamp` column, specify `all` as True
        where_clause = (
            f"where timestamp > '{self.last_execution_time}'"
            if not all or self.last_execution_time is None
            else ""
        )
        sql_query = f"select * from {self.database}.{self.schema}.{self.logs_table} {where_clause};"
        logs = [row.as_dict() for row in cast(list, self.provider.sql(sql_query))]
        log(f"{len(logs)} logs retrieved")
        if not logs:
            return
        from sqlite_utils import Database
        from sqlite_utils.db import Table
        db = Database(filename)
        cast(Table, db[table_name]).insert_all(logs)
        db.close()
        log(f"Logs saved from {table_name} in Snowflake to {filename} locally.")


def format_task_history(row):
    return (
        f"""error message: {row["ERROR_MESSAGE"]}"""
        if row["ERROR_MESSAGE"]
        else f"""successfully completed at: {row["COMPLETED_TIME"]}"""
    )