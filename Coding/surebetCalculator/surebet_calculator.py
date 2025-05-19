import streamlit as st
import pandas as pd
import numpy as np
from itertools import product

# Sidebar for the number of bookmakers
st.sidebar.header("Configuration")
num_bookmakers = st.sidebar.number_input(
    "Number of bookmakers", min_value=1, max_value=15, value=1, step=1
)

# Create initial data for the odds and deposits dataframe
@st.cache_data
def create_initial_data(num_bookmakers):
    return pd.DataFrame({
        "Bookmaker": [f"Bookmaker {i + 1}" for i in range(num_bookmakers)],
        "Outcome 1": [1.0] * num_bookmakers,
        "Draw": [1.0] * num_bookmakers,
        "Outcome 2": [1.0] * num_bookmakers,
        "Deposit Amount": [500] * num_bookmakers,
    })

# Initialize the dataframe in session state
if 'initial_data' not in st.session_state:
    st.session_state.initial_data = create_initial_data(num_bookmakers)

# Adjust the dataframe based on the number of bookmakers
if num_bookmakers != len(st.session_state.initial_data):
    st.session_state.initial_data = create_initial_data(num_bookmakers)

# Allow the user to edit the dataframe
st.header("Enter Odds and Deposit Amounts")
edited_df = st.data_editor(st.session_state.initial_data, num_rows="dynamic")

# Function to calculate potential wins for all combinations
@st.cache_data
def calculate_all_potential_wins(odds, deposits):
    outcomes = range(3)
    all_combinations = np.array(list(product(outcomes, repeat=len(deposits))))
    potential_wins = np.zeros((len(all_combinations), 3))
    individual_wins = np.zeros((len(all_combinations), len(deposits), 3))

    for i, combination in enumerate(all_combinations):
        for bookmaker_idx, outcome_idx in enumerate(combination):
            win_amount = deposits[bookmaker_idx] * odds[bookmaker_idx, outcome_idx]
            potential_wins[i, outcome_idx] += win_amount
            individual_wins[i, bookmaker_idx, outcome_idx] = win_amount

    return all_combinations, potential_wins, individual_wins

# Function to find the optimal distribution
def optimal_distribution(odds, deposits):
    all_combinations, potential_wins, individual_wins = calculate_all_potential_wins(odds, deposits)
    variances = np.var(potential_wins, axis=1)
    best_idx = np.argmin(variances)
    return all_combinations[best_idx], individual_wins[best_idx]

# Process the data
odds = edited_df[["Outcome 1", "Draw", "Outcome 2"]].values
deposits = edited_df["Deposit Amount"].values

# Calculate the optimal distribution
optimal_combination, individual_wins = optimal_distribution(odds, deposits)

# Display the results
st.header("Optimal Bet Distribution")
optimal_bets_df = pd.DataFrame(individual_wins, columns=["Outcome 1", "Draw", "Outcome 2"])
optimal_bets_df["Bookmaker"] = edited_df["Bookmaker"]
optimal_bets_df.set_index("Bookmaker", inplace=True)

# Calculate total potential wins for each outcome
total_potential_wins = optimal_bets_df.sum()

# Add a row for the sum of potential wins
total_row = pd.DataFrame(total_potential_wins).T
total_row.index = ["Total"]
optimal_bets_df = pd.concat([optimal_bets_df, total_row])

# Display the optimal bet distribution with total potential wins
st.dataframe(optimal_bets_df.style.format("{:.2f}"))

st.header("Total Potential Wins for Each Outcome")
st.write(f"**Total Potential Win if Outcome 1 Wins**: {total_potential_wins['Outcome 1']:.2f}")
st.write(f"**Total Potential Win if Draw**: {total_potential_wins['Draw']:.2f}")
st.write(f"**Total Potential Win if Outcome 2 Wins**: {total_potential_wins['Outcome 2']:.2f}")
