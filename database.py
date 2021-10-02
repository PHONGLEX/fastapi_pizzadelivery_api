from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config

engine = create_engine(config('DATABASE_URL'), echo=True)

Base = declarative_base()

Session=sessionmaker()