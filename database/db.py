from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
import os

load_dotenv()

pool = ConnectionPool(
    conninfo= os.getenv("DATABASE_URL"),
    min_size=1,
    max_size=10,
)

def db():
    with pool.connection() as conn:
        yield conn