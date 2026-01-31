from sqlmodel import Session, select
from models import PortfolioItem
import models

def update_portfolio_position(ticker: str, amount: float, session: Session):
    ticker = ticker.upper()
    item = session.get(PortfolioItem, ticker)
    if item:
        item.quantity += amount
        if item.quantity <= 0:
            session.delete(item)
    
    else:
        if amount > 0:
            new_entry = models.PortfolioItem(ticker=ticker, quantity=amount)
            session.add(new_entry)
    session.commit()