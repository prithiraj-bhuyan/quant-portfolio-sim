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
    price_paths = s0 * combined_yields

    predicted_prices = price_paths[-1, :]
    median = np.percentile(predicted_prices, 50, axis=None)
    var95 = np.percentile(predicted_prices, 5, axis=None)
    bull = np.percentile(predicted_prices, 95, axis=None)

    return price_paths, predicted_prices, median, var95, bull


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






