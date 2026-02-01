import yfinance as yf
import models
from sqlmodel import Session, select
import pandas as pd
import numpy as np

def sync_ticker(ticker_symbol: str):
    df = yf.download(ticker_symbol, period="15y")
    id = 1
    with Session(models.engine) as session:
        for dt, row in df.iterrows():
            id += 1
            new_entry = models.PriceHistory(ticker=ticker_symbol, date=dt, close_price=float(row["Close"][ticker_symbol]))

            session.add(new_entry)
        session.commit()
    print(f"Synced {ticker_symbol} successfully!")

# sync_ticker(ticker_symbol="MSFT")

def get_returns_series(ticker_symbol: str):
    with Session(models.engine) as session:
        query = select(models.PriceHistory).where(models.PriceHistory.ticker == ticker_symbol).order_by(models.PriceHistory.date)
        results = session.exec(query).all()

        if not results:
            sync_ticker(ticker_symbol)
            results = session.exec(query).all()
        
        if not results:
            raise ValueError(f"Could not find or sync data for {ticker_symbol}")

        prices = pd.Series(data=[r.close_price for r in results], index=[r.date for r in results])
        log_returns = np.log(prices/prices.shift(1)).dropna()

        return log_returns, prices.iloc[-1]
    
def get_portfolio_data(tickers: list[str]):
    log_returns_list = []
    curr_prices = []
    for t in tickers:
        log_returns, s0 = get_returns_series(t)
        log_returns_list.append(log_returns)
        curr_prices.append(s0)
    all_tickers_returns_df = pd.concat(log_returns_list, axis=1, keys=tickers).dropna()
    return all_tickers_returns_df, curr_prices