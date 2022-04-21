from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=32, max_overflow=32, isolation_level="AUTOCOMMIT")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_database() -> Generator:
    db = SessionLocal()

    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()
        engine.dispose()