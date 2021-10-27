from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine

from app.config import DATABASE_URL


engine = create_engine(str(DATABASE_URL), connect_args={'check_same_thread': False})

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    return Session()
