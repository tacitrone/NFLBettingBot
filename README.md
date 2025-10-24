# 🏈 NFL Betting Bot
**Author:** Tyler Citrone  
**Description:** A Python-based sports analytics tool that generates NFL betting recommendations using a combination of Elo ratings and live sportsbook odds.

## 🚀 Features
- **Elo Rating Model**: Calculates dynamic team strengths from recent NFL game results, including home-field advantage and score margins.  
- **Live Odds Integration**: Fetches up-to-date betting lines from [The Odds API](https://the-odds-api.com) across multiple sportsbooks.  
- **Probability Conversion**: Converts American odds into implied probabilities and compares them with model predictions.  
- **Value Betting Detection**: Identifies positive expected value (EV) bets where model probability exceeds bookmaker implied odds.  
- **Kelly Criterion Staking**: Recommends optimal bet sizes based on user bankroll and Kelly fraction.  
- **Interactive CLI**: Users can specify teams, number of recent weeks for Elo, minimum edge thresholds, and bankroll size.

## 🛠 Tech Stack
- **Python 3.9+**  
- Pandas – data handling  
- NumPy – probability & math utilities  
- Requests – API calls  
- nfl_data_py – NFL game data  
- python-dotenv – API key management  

## 📦 Installation
1. Clone the repository:
   git clone https://github.com/yourusername/nfl-betting-bot.git
   cd nfl-betting-bot

2. Create and activate a virtual environment (optional but recommended):
   python3 -m venv venv
   source venv/bin/activate   # On Mac/Linux
   venv\Scripts\activate      # On Windows

3. Install dependencies:
   pip install -r requirements.txt

4. Create a .env file in the root directory and add your Odds API key:
   ODDS_API_KEY=your_api_key_here

## ▶️ Usage
Run the bot:
   python nfl_betting_bot.py

The program will:
- Ask for home and away teams (full names, e.g., New England Patriots).  
- Ask how many recent weeks to use for Elo ratings (default: 10).  
- Ask for minimum edge percentage to trigger a recommendation (default: 1.0).  
- Ask for bankroll size to calculate Kelly stakes (default: 100).  

Example output:
Recommended Bets:
Book         | Side   | Team                 | Odds  | ModelProb | Edge% | KellyStake
FanDuel      | Home ML| New England Patriots | -110  | 0.55      | 3.2   | 7.8
DraftKings   | Away ML| Buffalo Bills        | +120  | 0.47      | 2.1   | 5.0

## 📊 Example Workflow
1. The bot builds Elo ratings from recent NFL games.  
2. It fetches live odds from multiple sportsbooks.  
3. It compares model probabilities vs. bookmaker implied probabilities.  
4. If an edge ≥ minimum threshold is found, it outputs a recommended bet with a Kelly stake size.

## ⚠️ Disclaimer
This tool is for educational and research purposes only. It is not financial advice. Always gamble responsibly.  

