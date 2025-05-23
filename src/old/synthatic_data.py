"""
Synthetic Data Generation for Hornsgatan Calibration

This script generates synthetic vehicle speed and time data based on real sensor data
using Random Forest regression. The generated data is intended for use in calibrating
machine learning models for traffic flow prediction.

The process involves:
1. Loading and filtering real sensor data for a specific detector ('e2w_in').
2. Engineering features based on previous vehicle speed and time.
3. Training Random Forest models to predict current speed and time.
4. Generating a synthetic sequence of speed and time by iteratively using the trained models.
5. Visualizing and comparing the distributions and time series of real and synthetic data.
"""

import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


# Define the detector ID to filter the real data
detector = "e2w_in"

# 1. Load and prepare real data
# Load the raw data from the specified CSV file
real_df = pd.read_csv('data/daily_splitted_data/data_2020-01-01.csv')
# Filter data for the chosen detector
real_df =  real_df[real_df["detector_id"]==detector]
# Sort data by time to ensure correct sequence for calculating previous values
real_df = real_df.sort_values('time_detector_real')
# Normalize time by subtracting the first detection time
first_time = real_df.iloc[0]["time_detector_real"]
real_df["time_detector_real"] = real_df["time_detector_real"] - first_time

# 2. Feature engineering
# Calculate previous speed and time
real_df['speed_prev'] = real_df['speed_detector_real'].shift(1)
real_df['time_prev'] = real_df['time_detector_real'].shift(1)
# Drop the first row which will have NaN for previous values
real_df = real_df.dropna()

# Save the processed real data (optional, for inspection)
real_df.to_csv('data/synthatic/real_data_{detector}.csv', index=False)

# Get the number of vehicles in the real data for generating the same number of synthetic vehicles
ll = len(real_df)

# 3. Fit regression models
# Define features (X) and targets (y) for the models
# X includes speed and time of the previous vehicle
X = real_df[['speed_prev', 'time_prev']]
# y_speed is the current vehicle's speed
y_speed = real_df['speed_detector_real']
# y_gap was intended here, but the code uses y_gap for the current time, which is different from gap.
# Let's assume y_gap here means the target for time prediction based on previous speed and time.
# It seems the intention was to predict the next time *directly*, not the gap.
# Let's rename the target variable for clarity if we are predicting time directly.
y_time = real_df['time_detector_real'] # Target is the current vehicle's time

# Initialize and train Random Forest Regressor models for speed and time
model_speed = RandomForestRegressor(n_estimators=100, random_state=42)
model_time = RandomForestRegressor(n_estimators=100, random_state=42)

model_speed.fit(X, y_speed)
model_time.fit(X, y_time)

# Get residual standard deviation for adding noise during generation
speed_resid_std = np.std(y_speed - model_speed.predict(X))
# It seems gap_resid_std is calculated from y_gap, which is current time, not gap.
# Let's rename for clarity and ensure it's std of residuals for time prediction.
time_resid_std = np.std(y_time - model_time.predict(X))

# 4. Generate synthetic data
# Set the number of synthetic vehicles to generate (same as real data)
num_vehicles = ll
rows = [] # List to store generated vehicle data

# Initialize with values from the first row of the processed real data
# These will be the 'previous' values for the first synthetic vehicle
idx = 0 # Start with the first processed real data point
last_speed = real_df.iloc[idx]['speed_prev']
last_time = real_df.iloc[idx]['time_prev']

# Loop to generate data for each synthetic vehicle
for _ in range(num_vehicles):
    # Predict the *next* speed and time based on the *last* generated values
    # Add random noise based on model residuals
    next_speed = model_speed.predict([[last_speed, last_time]])[0] + np.random.normal(0, speed_resid_std)
    next_time = model_time.predict([[last_speed, last_time]])[0] + np.random.normal(0, time_resid_std) # Use time_resid_std
    # Ensure speed and time are non-negative
    next_speed = max(0, next_speed)
    next_time = max(0, next_time)

    # Append the generated data to the rows list
    rows.append({
        'synthatic_time': next_time,
        'syntatic_speed': next_speed,
    })

    # Update the 'last' values for the next iteration
    last_speed = next_speed
    last_time = next_time

# Convert the list of rows into a pandas DataFrame
synthetic_df = pd.DataFrame(rows)
# Save the synthetic data to a CSV file
synthetic_df.to_csv('data/synthatic/synthetic_data_{detector}.csv', index=False)

# Visual comparison
# Extract real data for plotting
real_speed = real_df['speed_detector_real']
real_time = real_df['time_detector_real']
# Extract synthetic data for plotting
synth_time = synthetic_df['synthatic_time']
synth_speed = synthetic_df['syntatic_speed']

# Plotting distributions (Histograms)
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.hist(real_speed, bins=30, alpha=0.5, label='Real Speed')
plt.hist(synth_speed, bins=30, alpha=0.5, label='Synthetic Speed')
plt.xlabel('Speed')
plt.ylabel('Frequency')
plt.title('Speed Distribution')
plt.legend()

plt.subplot(1, 2, 2)
plt.hist(real_time, bins=30, alpha=0.5, label='Real time')
plt.hist(synth_time, bins=30, alpha=0.5, label='Synthetic time')
plt.xlabel('time (s)')
plt.ylabel('Frequency')
plt.title('time Distribution')
plt.legend()

plt.tight_layout()
# Save histogram plot
plt.savefig('data/synthatic/compare_hist.png')
# Display the plot
plt.show()

# Time series comparison (first 200 points)
plt.figure(figsize=(12, 5))
plt.subplot(2, 1, 1)
plt.plot(real_speed[:200].reset_index(drop=True), label='Real Speed')
plt.plot(synth_speed[:200].reset_index(drop=True), label='Synthetic Speed')
plt.ylabel('Speed')
plt.title('Speed Time Series (First 200)')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(real_time[:200].reset_index(drop=True), label='Real time')
plt.plot(synth_time[:200].reset_index(drop=True), label='Synthetic time')
plt.ylabel('time (s)')
plt.title('time Time Series (First 200)')
plt.legend()

plt.tight_layout()
# Save time series plot
plt.savefig('data/synthatic/compare_timeseries.png')
# Display the plot
plt.show()
