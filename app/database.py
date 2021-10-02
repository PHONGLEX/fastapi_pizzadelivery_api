import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config


engine = create_engine(os.getenv('CONNECTION_STRING', 'postgresql://mbvpfycs:jZbPHD9ETANF1SchMG4d27KPP_NBSFhQ@arjuna.db.elephantsql.com/mbvpfycs'), echo=True)

Base = declarative_base()

Session=sessionmaker()