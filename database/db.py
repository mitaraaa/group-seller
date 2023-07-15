import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models import Base

sqlite_file_path = os.getenv("DATABASE_PATH")
engine = create_engine(f"sqlite:///{sqlite_file_path}")
Base.metadata.create_all(bind=engine)
session = Session(engine)
