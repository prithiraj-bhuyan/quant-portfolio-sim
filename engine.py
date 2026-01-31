import data_service
import numpy as np
import matplotlib.pyplot as plt

def simulate_price_paths(log_returns, days_to_predict, time_step, num_simulations, s0):
    mean = log_returns.mean()
    var = log_returns.var()
    vol = log_returns.std()
    #random matrix
    Z = np.random.standard_normal((days_to_predict, num_simulations))
    # daily growth factor
    g_factor = np.exp((mean - 0.5 * var) * time_step + (vol * Z * np.sqrt(time_step)))
    yield_paths = np.cumprod(g_factor, axis=0)
    day_zero = np.ones((1, num_simulations))
    combined_yields = np.vstack([day_zero, yield_paths])
    # Geometric Brownian Motion (GBM)
    price_paths = s0 * combined_yields

    predicted_prices = price_paths[-1, :]
    median = np.percentile(predicted_prices, 50, axis=None)
    lower = np.percentile(predicted_prices, 5, axis=None)
    upper = np.percentile(predicted_prices, 95, axis=None)

    return price_paths, predicted_prices, median, lower, upper

def simulate_portfolio(returns_df, current_prices, days, sims, time_step):
    cov_matrix = returns_df.cov() 
    avg_returns = returns_df.mean().values.reshape(1, 1, -1)
    num_stocks = len(current_prices)

    L = np.linalg.cholesky(cov_matrix)
    Z = np.random.standard_normal((days, sims, num_stocks))

    Z_correlated = Z @ L.T

    vol_all_tickers = np.sqrt(np.diag(cov_matrix)).reshape(1, 1, -1)


    G_factor = np.exp((avg_returns - 0.5 * np.square(vol_all_tickers)) * time_step + (vol_all_tickers * Z_correlated * np.sqrt(time_step)))
    yield_paths = np.cumprod(G_factor, axis=0)
    day_zero = np.ones((1, sims, num_stocks))
    combined_yields = np.vstack([day_zero, yield_paths])

    prices_arr = np.array(current_prices).reshape(1, 1, num_stocks)

    # Individual Price Paths (3D: days, sims, stocks)
    price_paths = prices_arr * combined_yields
    # portfolio_paths is 2D (days, sims)
    portfolio_paths = np.sum(price_paths, axis=2)

    # list of total portfolio values on each day
    median_line = np.percentile(portfolio_paths, 50, axis=1)
    lower_line = np.percentile(portfolio_paths, 5, axis=1)
    upper_line = np.percentile(portfolio_paths, 95, axis=1)

    initial_val = portfolio_paths[0, 0]
    ending_median = median_line[-1]
    ending_lower = lower_line[-1]
    ending_upper = upper_line[-1]

    return {
        "chart-data": {
            "labels": list(range(len(median_line))), #days
            "median": median_line.tolist(),
            "lower": lower_line.tolist(),
            "upper": upper_line.tolist()
        },
        "summary": {
            "initial_value": float(initial_val),
            "expected_ending_value": float(ending_median),
            "var95_dollar": max(0, float(initial_val - ending_lower)),
            "max_potential_gain": float(ending_upper - initial_val),
            "expected_roi_percent": float(((ending_median / initial_val) - 1) * 100)
        },
        "correlations": returns_df.corr().to_dict()
    }


def plot_simulation(price_paths, s0, median, var95, bull):
    plt.figure(figsize=(12, 6))
    
    plt.plot(price_paths[:, :100], color='gray', alpha=0.1)
    
    plt.axhline(y=s0, color='red', linestyle='--', label=f'Start Price: ${s0:.2f}')
    
    days = len(price_paths) - 1
    plt.scatter([days], [median], color='green', zorder=5, label=f'Median: ${median:.2f}')
    plt.scatter([days], [var95], color='orange', zorder=5, label=f'VaR95: ${var95:.2f}')
    plt.scatter([days], [bull], color='blue', zorder=5, label=f'95th: ${bull:.2f}')

    plt.title("Monte Carlo Price Prediction (1 Year)")
    plt.xlabel("Days into Future")
    plt.ylabel("Stock Price ($)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

def plot_histogram(predicted_prices):
    plt.figure(figsize=(10, 5))
    plt.hist(predicted_prices, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title("Distribution of Ending Prices")
    plt.xlabel("Price ($)")
    plt.ylabel("Frequency")
    plt.show()

if __name__ == "__main__":
    log_returns, s0 = data_service.get_returns_series("MSFT")
    price_paths, predicted_prices, median, var95, bull = simulate_price_paths(log_returns, 252, 1, 1000, s0)
    # plot_simulation(price_paths, s0, median, var95, bull)
    # plot_histogram(predicted_prices)






