from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL database URL (Render)
DATABASE_URL = "postgresql://appreciate_7oil_user:3GWa9K8BhmOchwTkQKnPTIbD1dwzawzg@dpg-d3b6pit6ubrc739gdd5g-a/appreciate_7oil"

# No connect_args for PostgreSQL
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
