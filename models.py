from sqlmodel import Field, SQLModel, create_engine
from datetime import datetime

class Portfolio(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str | None
    created_at: datetime = Field(default_factory=datetime.now)

class Position(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    portfolio_id: int = Field(foreign_key="portfolio.id")
    ticker: str = Field(index=True)
    shares: float

class PriceHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    date: datetime = Field(index=True)
    close_price: float

sqlite_file = "database.db"
sqlite_url = f"sqlite:///{sqlite_file}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
    print("Database and tables created successfully!")