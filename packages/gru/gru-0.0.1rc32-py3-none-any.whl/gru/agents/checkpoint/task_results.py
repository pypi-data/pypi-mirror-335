from enum import StrEnum

from gru.agents.checkpoint.postgres import PostgresAsyncConnectionPool


CREATE_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS canso_task_results (
        agent_name varchar(64) NOT NULL,
        prompt_id varchar(64) NOT NULL,
        task_type varchar(64) NOT NULL,
        run_id varchar(64) NOT NULL,
        status varchar(32) NOT NULL,
        result TEXT,
        PRIMARY KEY (agent_name, prompt_id, task_type, run_id)
    )
"""

INSERT_QUERY = """
    INSERT INTO canso_task_results (agent_name, prompt_id, task_type, run_id, status, result)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (agent_name, prompt_id, task_type, run_id) 
    DO UPDATE SET 
        status = EXCLUDED.status,
        result = EXCLUDED.result;
"""

select_query = """
    SELECT status, result 
    FROM canso_task_results 
    WHERE agent_name = %s AND prompt_id = %s AND task_type = %s AND run_id = %s
"""


class TaskStatus(StrEnum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"


class TaskResultsRepository:

    async def setup(self):
        connection_pool = PostgresAsyncConnectionPool().get()
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(CREATE_TABLE_QUERY)

    async def update(
        self,
        agent_name: str,
        prompt_id: str,
        task_type: str,
        run_id: str,
        status: TaskStatus,
        result: str = None,
    ):
        connection_pool = PostgresAsyncConnectionPool().get()
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    INSERT_QUERY,
                    (agent_name, prompt_id, task_type, run_id, status, result),
                )

    async def get_result(
        self, agent_name: str, prompt_id: str, task_type: str, run_id: str
    ):
        connection_pool = PostgresAsyncConnectionPool().get()
        async with connection_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    select_query, (agent_name, prompt_id, task_type, run_id)
                )
                row = await cur.fetchone()

                if row is None:
                    return None

                return row[0], row[1]
