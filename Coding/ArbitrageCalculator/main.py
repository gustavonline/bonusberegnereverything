import streamlit as st
import pandas as pd
import json

from calculations import calculate_bets

def load_config(filename='bookmakers.json'):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_config(config, filename='bookmakers.json'):
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)

def save_odds(odds):
    """Save the odds data to a JSON file."""
    try:
        with open('odds.json', 'w') as f:
            json.dump(odds, f, indent=4)
        st.success("Odds data saved successfully!")
    except Exception as e:
        st.error(f"Failed to save odds: {str(e)}")

def main():
    st.set_page_config(page_title="Arbitrage Bonus Profit Calculator", layout="wide")
    config = load_config()
    odds = load_config('odds.json')

    if 'odds_data' not in st.session_state:
        st.session_state['odds_data'] = odds  # Initialize session state with loaded odds

    page = st.sidebar.selectbox("Navigate", ["Bookmaker Settings", "Enter Match Details", "Enter Odds", "Calculate Bets"])

    if page == "Bookmaker Settings":
        st.header("Edit and Exclude Bookmaker Settings")
        excluded_bookmakers = st.multiselect("Select bookmakers to exclude from calculations:", list(config.keys()))
        for bk, details in config.items():
            with st.expander(f"{bk} settings"):
                details['bonus_type'] = st.text_input("Bonus Type", details.get('bonus_type', ''), key=f"{bk}_bonus_type")
                details['activation'] = st.text_input("Activation", details.get('activation', ''), key=f"{bk}_activation")
                details['conditions'] = st.text_area("Conditions", details.get('conditions', ''), key=f"{bk}_conditions")
                details['min_odds'] = st.number_input("Minimum Odds", value=float(details.get('min_odds', 1.0)), key=f"{bk}_min_odds")
                details['max_deposit'] = st.number_input("Maximum Deposit", value=float(details.get('max_deposit', 100)), key=f"{bk}_max_deposit")
        if st.button("Save Changes"):
            save_config(config)
            st.success("Settings and exclusions saved!")

    elif page == "Enter Match Details":
        st.header("Match Details")
        team1 = st.text_input("Enter the name of Team 1:")
        team2 = st.text_input("Enter the name of Team 2:")
        match_date = st.date_input("Date of the match:")
        match_time = st.time_input("Time of the match:")
        if st.button("Save Match Details"):
            match_details = {"team1": team1, "team2": team2, "date": str(match_date), "time": str(match_time)}
            st.session_state['match_details'] = match_details
            save_config(match_details, 'match_details.json')
            st.success("Match details saved successfully!")

    elif page == "Enter Odds":
        st.header("Enter Odds for Each Bookmaker")
        included_bookmakers = [bk for bk in config if bk not in st.session_state.get('excluded_bookmakers', [])]
        odds_data = {}
        for bookmaker in included_bookmakers:
            with st.expander(f"{bookmaker} Odds"):
                win = st.number_input(f"{bookmaker} - Odds that {st.session_state['match_details']['team1']} wins:", value=st.session_state['odds_data'].get(bookmaker, {}).get('win', 1.0), key=f"{bookmaker}_win")
                draw = st.number_input(f"{bookmaker} - Odds for draw:", value=st.session_state['odds_data'].get(bookmaker, {}).get('draw', 1.0), key=f"{bookmaker}_draw")
                lose = st.number_input(f"{bookmaker} - Odds that {st.session_state['match_details']['team2']} wins:", value=st.session_state['odds_data'].get(bookmaker, {}).get('lose', 1.0), key=f"{bookmaker}_lose")
                odds_data[bookmaker] = {"win": win, "draw": draw, "lose": lose}
        if st.button("Save Odds"):
            save_odds(odds_data)
            st.session_state['odds_data'] = odds_data

    elif page == "Calculate Bets":
        if 'odds_data' in st.session_state:
            deposits_bonuses = {bk: {'Deposit': config[bk]['Deposit'], 'Bonus': config[bk]['Bonus']} for bk in config}
            results = calculate_bets(st.session_state['odds_data'], deposits_bonuses)
            if "Error" not in results:
                st.subheader("Suggested Bets:")
                data = {bk: [results[bk].get(outcome, 0) for outcome in ['win', 'draw', 'lose']] for bk in results}
                df = pd.DataFrame(data, index=["Team 1 Wins", "Draw", "Team 2 Wins"]).T
                df['Total'] = df.sum(axis=1)
                total_per_outcome = df.sum(axis=0)
                df.loc['Total'] = total_per_outcome
                st.table(df)
            else:
                st.error(results["Error"])
        else:
            st.error("Please enter the required odds and match details first.")

if __name__ == "__main__":
    main()