import numpy as np

def calculate_bets(odds_data, deposits_bonuses):
    outcomes = ['win', 'draw', 'lose']
    bets = {}

    for bk, odds in odds_data.items():
        # Skip bookmakers with any None values in their odds
        if any(odds[o] is None for o in outcomes):
            continue

        # Retrieve the total funds available for betting
        total_funds = deposits_bonuses.get(bk, {}).get('Deposit', 0) + deposits_bonuses.get(bk, {}).get('Bonus', 0)

        # Evenly distribute funds across the available outcomes
        valid_outcomes = [o for o in outcomes if odds[o] is not None]
        funds_per_outcome = total_funds // len(valid_outcomes)
        bets[bk] = {o: funds_per_outcome for o in valid_outcomes}

        # Distribute any leftover funds due to integer division
        leftover = total_funds - funds_per_outcome * len(valid_outcomes)
        for i in range(leftover):
            bets[bk][valid_outcomes[i]] += 1

    # Calculate potential returns for each outcome
    potential_returns = {o: sum(bets.get(bk, {}).get(o, 0) * odds_data[bk][o]
                                for bk in bets if o in bets[bk])
                         for o in outcomes}

    return bets, potential_returns

# Example usage
# odds_data = {
#     "Unibet": {"win": 1.88, "draw": 3.25, "lose": 4.7},
#     "ComeOn": {"win": 1.97, "draw": 3.23, "lose": 4.47},
# }
# deposits_bonuses = {
#     "Unibet": {"Deposit": 1000, "Bonus": 1000},
#     "ComeOn": {"Deposit": 500, "Bonus": 500},
# }
# print(calculate_bets(odds_data, deposits_bonuses))
