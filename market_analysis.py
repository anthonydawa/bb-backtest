import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the original CSV file
input_file = 'market_analysis\TEST-BTCUSDT-1h-1 sep, 2017-None.csv'  # Replace with the path to your input CSV file
# Read the CSV file and select only the "PNL" column
df = pd.read_csv(input_file, usecols=['PNL'])

# Split the DataFrame into groups of 288 rows
grouped = df.groupby(df.index // (24 * 30))

# Initialize variables for maximum positive and negative differences
max_positive_difference = float('-inf')
max_negative_difference = float('inf')

# Initialize counters for negative and positive streaks
max_negative_streak = 0
current_negative_streak = 0

max_positive_streak = 0
current_positive_streak = 0

# Initialize a list to store the individual differences
individual_differences = []

# Initialize the final PNL variable
final_pnl = None

# Compute the difference between the last row and the first row in each group
for group, data in grouped:
    pnl_difference = data.iloc[-1]['PNL'] - data.iloc[0]['PNL']
    individual_differences.append(pnl_difference)
    
    if pnl_difference < 0:
        current_negative_streak += 1
        current_positive_streak = 0
        max_negative_streak = max(max_negative_streak, current_negative_streak)
        max_negative_difference = min(max_negative_difference, pnl_difference)
    elif pnl_difference > 0:
        current_positive_streak += 1
        current_negative_streak = 0
        max_positive_streak = max(max_positive_streak, current_positive_streak)
        max_positive_difference = max(max_positive_difference, pnl_difference)
    else:
        current_negative_streak = 0
        current_positive_streak = 0

    # Set the final PNL
    final_pnl = data.iloc[-1]['PNL']
    
    print(f'Group {group}: PNL Difference = {pnl_difference}')

# Calculate the average difference, median difference, and win rate
average_difference = sum(individual_differences) / len(individual_differences)
median_difference = np.median(individual_differences)
win_rate = (len([p for p in individual_differences if p > 0]) / len(individual_differences)) * 100

# Print results
print(f'\nNumber of Negative PNL Differences = {len([p for p in individual_differences if p < 0])}')
print(f'Number of Positive PNL Differences = {len([p for p in individual_differences if p > 0])}')
print(f'Average PNL Difference = {average_difference}')
print(f'Maximum Winning Streak = {max_positive_streak}')
print(f'Maximum Losing Streak = {max_negative_streak}')
print(f'Largest Positive Difference = {max_positive_difference}')
print(f'Largest Negative Difference = {max_negative_difference}')
print(f'Median Difference = {median_difference}')
print(f'Win Rate = {win_rate}%')
print(f'Final PNL = {final_pnl}')

# Plotting the PNL differences with grids
plt.figure(figsize=(10, 6))
plt.plot(individual_differences, label='PNL Differences')
plt.axhline(y=median_difference, color='r', linestyle='--', label='Median Difference')
plt.xlabel('Group Index')
plt.ylabel('PNL Difference')
plt.title('PNL Differences')
plt.legend()
plt.grid(True)

plt.show()

# Plotting the PNL differences as a bar chart
plt.figure(figsize=(10, 6))
plt.bar(range(len(individual_differences)), individual_differences, color='blue', alpha=0.7)
plt.axhline(y=median_difference, color='r', linestyle='--', label='Median Difference')
plt.xlabel('Sequence')
plt.ylabel('PNL Difference')
plt.title('PNL Differences Bar Chart')
plt.legend()
plt.grid(True)

plt.show()