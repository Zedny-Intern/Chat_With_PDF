from sqlalchemy import create_engine, text
from config.settings import DB_USER, DB_PASS, DB_HOST, DB_NAME

# Create root engine (no DB name)
engine_root = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/", future=True)

with engine_root.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"))
    conn.commit()

engine_root.dispose()
print("Database created successfully!")
