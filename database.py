from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


#DATABASE_URL = "sqlite:///data/dongi.db"
DATABASE_URL = "sqlite:////tmp/database.db"

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()