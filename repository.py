from sqlmodel import Session
from models import PortfolioItem
import yfinance as yf

def update_portfolio_position(ticker: str, amount: float, session: Session, trade: str = "na"):
    ticker = ticker.upper()
    try:
        yf_ticker = yf.Ticker(ticker)
        if not 'regularMarketPrice' in yf_ticker.info or (amount <= 0 and trade != "sell") or (amount >= 0 and trade == "sell"):
            return False
    except Exception as e:
        return False
    item = session.get(PortfolioItem, ticker)
    if item:
        item.quantity += amount
        if item.quantity <= 0:
            session.delete(item)
    
    else:
        if amount > 0:
            new_entry = PortfolioItem(ticker=ticker, quantity=amount)
            session.add(new_entry)
    session.commit()
    return True