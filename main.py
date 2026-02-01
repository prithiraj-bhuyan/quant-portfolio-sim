from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session
from database import yield_session
from repository import update_portfolio_position
from portfolio_service import get_simulation_inputs
from engine import simulate_portfolio
from contextlib import asynccontextmanager
from database import engine, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/portfolio/trade/buy")
def trade(ticker: str, amount: float, session: Session = Depends(yield_session)):
    if update_portfolio_position(ticker=ticker, amount=amount, session=session):
        return {"message": f"Successfully increased {ticker} by {amount} shares."}
    else:
        return {f"Error: {ticker} is not a valid ticker symbol or quantity is invalid."}

@app.post("/portfolio/trade/sell")
def trade(ticker: str, amount: float, session: Session = Depends(yield_session)):
    if update_portfolio_position(ticker=ticker, amount=(-1)*amount, session=session, trade="sell"):
        return {"message": f"Successfully decreased {ticker} by {amount} shares."}
    else:
        return {f"Error: {ticker} is not a valid ticker symbol or quantity is invalid."}

@app.get("/portfolio/simulate")
def run_simulation(sims: int = 10000, session: Session = Depends(yield_session)):
    inputs = get_simulation_inputs(session=session)
    if isinstance(inputs, str) or not inputs:
        raise HTTPException(status_code=400, detail="Add stocks to your portfolio first!")
    
    returns_df = inputs["returns_df"]
    curr_prices = inputs["current_prices"]
    results = simulate_portfolio(returns_df=returns_df, current_prices=curr_prices, days=252, sims=sims, time_step=1)

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
    quantities = inputs["quantities"]

    return {
        "empty": False,
        "tickers": tickers,
        "current_prices": curr_prices,
        "weights": weights,
        "total_val": total_val,
        "quantities": quantities
    }