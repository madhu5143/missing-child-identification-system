from sqlalchemy import create_engine, select, Table, MetaData
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
metadata = MetaData()
users = Table("users", metadata, autoload_with=engine)

with engine.connect() as conn:
    stmt = select(users)
    result = conn.execute(stmt)
    for row in result:
        print(row)
