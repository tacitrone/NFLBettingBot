"""
    NFL Betting Bot
    Author: Tyler Citrone

    Description:
    ------------
    A Python-based sports analytics tool that generates NFL betting recommendations
    using a combination of Elo ratings and live sportsbook odds.

    Features:
    - Builds Elo ratings from recent NFL game results (accounts for home-field advantage).
    - Fetches live betting lines from The Odds API across multiple bookmakers.
    - Converts American odds to probabilities and compares them to Elo model predictions.
    - Identifies value bets by calculating the "edge" between model probability and implied odds.
    - Uses the Kelly criterion to recommend optimal bet sizes based on user bankroll.
    - Interactive CLI: users can select teams, set Elo history window, define minimum edge thresholds,
        and manage bankroll assumptions.

    Tech Stack:
        Python, Pandas, NumPy, Requests, nfl_data_py, dotenv

"""


import os
import sys
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv

# ---- Helper functions  ---- #
def american_to_prob(odds):
    if odds is None or pd.isna(odds):
        return np.nan
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return -odds / (-odds + 100.0)

def prob_to_american(p):
    if p <= 0 or p >= 1:
        return np.nan
    dec = 1.0 / p
    if dec >= 2.0:
        return (dec - 1.0) * 100.0
    return -100.0 / (dec - 1.0)

def kelly_fraction(p, odds):
    if odds is None or pd.isna(odds) or p <= 0 or p >= 1:
        return 0.0
    dec = 1 + (odds/100.0 if odds > 0 else 100.0 / -odds)
    b = dec - 1.0
    q = 1.0 - p
    return max(0.0, (b*p - q)/b)

# ---- Elo model bits ---- #
HOME_FIELD_ELO = 55.0
BASE_K = 20.0

def import_recent_games(season, weeks_back):
    import nfl_data_py as nfl
    seasons = [season-1, season]
    sched = nfl.import_schedules(seasons)
    sched = sched.query("game_type=='REG' and home_score.notnull() and away_score.notnull()").copy()
    sched["game_datetime"] = pd.to_datetime(sched["gameday"])
    current_week = int(sched.query("season==@season")["week"].max())
    min_week = max(1, current_week-weeks_back+1)
    return sched.query("season==@season and week>=@min_week")

def build_elo(games):
    teams = pd.unique(pd.concat([games["home_team"], games["away_team"]]))
    elo = {t:1500 for t in teams}
    for _,r in games.sort_values("game_datetime").iterrows():
        h,a,hs,as_ = r["home_team"],r["away_team"],float(r["home_score"]),float(r["away_score"])
        rh,ra = elo[h],elo[a]
        exp_h = 1/(1+10**(-((rh+HOME_FIELD_ELO)-ra)/400))
        act_h = 1 if hs>as_ else 0 if hs<as_ else 0.5
        k = BASE_K*(1+min(3,abs(hs-as_)/7))
        elo[h] = rh + k*(act_h-exp_h)
        elo[a] = ra + k*((1-act_h)-(1-exp_h))
    return elo

def elo_home_prob(home, away, elo):
    return 1/(1+10**(-((elo.get(home,1500)+HOME_FIELD_ELO)-elo.get(away,1500))/400))

# ---- Odds API ---- #
def fetch_odds(api_key):
    url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
    params = {"api_key": api_key,"regions":"us","markets":"h2h","oddsFormat":"american"}
    r = requests.get(url,params=params,timeout=30)
    r.raise_for_status()
    return pd.DataFrame([{
        "home_team": g["home_team"],
        "away_team": g["away_team"],
        "book": bk["title"],
        "home_price": next((o["price"] for o in mk["outcomes"] if o["name"]==g["home_team"]),None),
        "away_price": next((o["price"] for o in mk["outcomes"] if o["name"]==g["away_team"]),None)
    } for g in r.json() for bk in g["bookmakers"] for mk in bk["markets"] if mk["key"]=="h2h"])

# ---- Main ---- #
def main():
    load_dotenv()
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        api_key = input("Enter your Odds API key: ").strip()

    # Ask user interactively
    home = input("Enter HOME team (full name): ").strip()
    away = input("Enter AWAY team (full name): ").strip()
    weeks_back = int(input("How many recent weeks to use for Elo? (default 10): ") or 10)
    min_edge = float(input("Minimum edge percentage to recommend? (default 1.0): ") or 1.0)
    stake = float(input("Bankroll size to compute Kelly stake (default 100): ") or 100)

    season = datetime.now(timezone.utc).year
    elo = build_elo(import_recent_games(season,weeks_back))
    odds = fetch_odds(api_key)

    game = odds[(odds["home_team"].str.contains(home,case=False)) &
                (odds["away_team"].str.contains(away,case=False))]

    if game.empty:
        print("Game not found in current odds feed.")
        sys.exit(0)

    p_home = elo_home_prob(home,away,elo)
    p_away = 1-p_home

    recs=[]
    for _,r in game.iterrows():
        hp,ap = r["home_price"],r["away_price"]
        imp_home,imp_away = american_to_prob(hp),american_to_prob(ap)
        edge_home,edge_away = (p_home-imp_home)*100,(p_away-imp_away)*100
        k_home,k_away = kelly_fraction(p_home,hp),kelly_fraction(p_away,ap)

        if edge_home>=min_edge:
            recs.append((r["book"],"Home ML",home,hp,round(p_home,3),round(edge_home,2),round(k_home*stake,2)))
        if edge_away>=min_edge:
            recs.append((r["book"],"Away ML",away,ap,round(p_away,3),round(edge_away,2),round(k_away*stake,2)))

    if not recs:
        print("No positive-edge bets for that matchup.")
    else:
        print("\nRecommended Bets:")
        print("Book | Side | Team | Odds | ModelProb | Edge% | KellyStake")
        for r in recs:
            print(" | ".join(map(str,r)))

if __name__=="__main__":
    main()
