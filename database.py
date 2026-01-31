from sqlmodel import Session
from models import engine

def yield_session():
    with Session(engine) as session:
        yield session