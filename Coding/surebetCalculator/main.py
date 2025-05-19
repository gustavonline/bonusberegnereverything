from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from itertools import product

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OddsInput(BaseModel):
    num_bookmakers: int
    odds: list
    deposits: list

def create_initial_data(num_bookmakers):
    return pd.DataFrame({
        "Bookmaker": [f"Bookmaker {i + 1}" for i in range(num_bookmakers)],
        "Outcome 1": [1.0] * num_bookmakers,
        "Draw": [1.0] * num_bookmakers,
        "Outcome 2": [1.0] * num_bookmakers,
        "Deposit Amount": [500] * num_bookmakers,
    })

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

def optimal_distribution(odds, deposits):
    all_combinations, potential_wins, individual_wins = calculate_all_potential_wins(odds, deposits)
    variances = np.var(potential_wins, axis=1)
    best_idx = np.argmin(variances)
    return all_combinations[best_idx], individual_wins[best_idx]

@app.post("/optimize")
def optimize(data: OddsInput):
    odds = np.array(data.odds)
    deposits = np.array(data.deposits)
    optimal_combination, individual_wins = optimal_distribution(odds, deposits)
    return {"optimal_combination": optimal_combination.tolist(), "individual_wins": individual_wins.tolist()}
