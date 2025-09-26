from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL database URL (Render)
DATABASE_URL = "postgresql://appreciate_user:kHIMjfKLG7aMAU7bdKxJYPGU8SCWcZmD@dpg-d394lj0dl3ps73akuh00-a/appreciate"

# No connect_args for PostgreSQL
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
