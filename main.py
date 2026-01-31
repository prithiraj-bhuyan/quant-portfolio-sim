from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session
from database import yield_session
from repository import update_portfolio_position
from portfolio_service import get_simulation_inputs
from engine import simulate_portfolio

app = FastAPI()

@app.post("/portfolio/trade")
def trade(ticker: str, amount: float, session: Session = Depends(yield_session)):
    update_portfolio_position(ticker=ticker, amount=amount, session=session)
    return {"message": f"Successfully updated {ticker} by {amount} shares."}

@app.get("/portfolio/simulate")
def run_simulation(sims: int = 10000, session: Session = Depends(yield_session)):
    inputs = get_simulation_inputs(session=session)
    if isinstance(inputs, str) or not inputs:
        raise HTTPException(status_code=400, detail="Add stocks to your portfolio first!")
    
    returns_df = inputs["returns_df"]
    weights = inputs["weights"]
    curr_prices = inputs["curr_prices"]
    results = simulate_portfolio(returns_df=returns_df, current_prices=curr_prices, weights=weights, days=252, sims=sims, time_step=1/252)

    return results

@app.get("/portfolio/summary")
def portfolio_summary(session: Session = Depends(yield_session)):
    inputs = get_simulation_inputs(session=session)
    if not inputs:
        return {
            "empty": True,
            "tickers": [],
            "weights": [],
            "total_val": 0.0
        }
    weights = inputs["weights"].tolist()
    total_val = float(inputs["total_value"])
    curr_prices = inputs["current_prices"].tolist()
    tickers = inputs["tickers"]

    return {
        "empty": False,
        "tickers": tickers,
        "current_prices": curr_prices,
        "weights": weights,
        "total_val": total_val
    }