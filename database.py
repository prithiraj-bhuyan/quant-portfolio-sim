from sqlmodel import SQLModel, Session
import models


def init_db(engine):
    """
    Creates all tables defined in the SQLModel metadata.
    If the tables already exist, this function does nothing.
    """
    SQLModel.metadata.create_all(engine)

def yield_session():
    with Session(models.engine) as session:
        yield session