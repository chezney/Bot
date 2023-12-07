# monte_carlo.py
import numpy as np

# This function runs the Monte Carlo simulations to generate possible future price scenarios
# for the asset based on its historical volatility and other factors.
def run_monte_carlo_simulations(preprocessed_data, num_simulations=1000000, forecast_hours=24):
    # The 'lastTradedPrice' is used as the starting price for the simulations.
    start_price = preprocessed_data['lastTradedPrice']
    
    # Historical volatility (annualized) should be calculated from historical price data.
    # Here, we use a placeholder value for demonstration purposes.
    volatility = 0.2
    
    # The risk-free rate is a factor in the drift calculation for the simulations.
    # Again, we use a placeholder value here.
    risk_free_rate = 0.01
    
    # The drift and volatility factors are calculated for the simulations.
    # Drift represents the expected return of the asset, and vol_factor represents
    # the random component of the price movement.
    drift = (risk_free_rate - 0.5 * volatility ** 2) * (1 / 365) * (1 / 24)
    vol_factor = volatility * np.sqrt(1 / 365) * np.sqrt(1 / 24)
    
    # We initialize an array to store the simulated price paths.
    simulated_price_paths = np.zeros((num_simulations, forecast_hours))
    
    # We simulate the price paths using a geometric Brownian motion model.
    for i in range(num_simulations):
        simulated_price_paths[i, 0] = start_price  # The first price is the last traded price.
        for j in range(1, forecast_hours):
            # Each price is calculated using the previous price and a random shock
            # based on the drift and volatility factors.
            random_shock = np.random.normal(drift, vol_factor)
            simulated_price_paths[i, j] = simulated_price_paths[i, j - 1] * np.exp(random_shock)
    
    # Calculate additional statistics
    percentile_5 = np.percentile(simulated_price_paths[:, -1], 5)
    percentile_95 = np.percentile(simulated_price_paths[:, -1], 95)
    var = np.percentile(simulated_price_paths[:, -1], 1)
    expected_shortfall = simulated_price_paths[:, -1][simulated_price_paths[:, -1] <= var].mean()

    # Calculate the mean expected price at the end of the forecast period across all simulations.
    mean_expected_price = np.mean(simulated_price_paths[:, -1])

    # The function returns the full distribution, mean expected price, and additional statistics
    return simulated_price_paths, mean_expected_price, percentile_5, percentile_95, var, expected_shortfall
