from models import PortfolioItem
from sqlmodel import Session, select
from data_service import get_portfolio_data
import numpy as np

def get_simulation_inputs(session: Session):
    items = session.exec(select(PortfolioItem)).all()
    if not items:
        return None
    
    ticker_list = [item.ticker for item in items]
    quantities = np.array([item.quantity for item in items])
    quantity_map = {ticker: float(q) for ticker, q in zip(ticker_list, quantities)}

    returns_df, curr_prices = get_portfolio_data(ticker_list)
    curr_prices = np.array(curr_prices)

    ticker_values = quantities * curr_prices
    portfolio_total_val = np.sum(ticker_values)

    weights = ticker_values/portfolio_total_val

    return {
        "returns_df": returns_df,
        "weights": weights,
        "current_prices": ticker_values,
        "total_value": portfolio_total_val,
        "tickers": ticker_list,
        "quantities": quantity_map
    }
    

