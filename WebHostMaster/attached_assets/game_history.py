from datetime import datetime
from config import HISTORY_FILES

class GameHistory:
    @staticmethod
    def save_match(player1, player2, set_scores, winner):
        """Save match results to history file"""
        try:
            with open(HISTORY_FILES["TABLE_TENNIS"], 'a') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                match_summary = (
                    f"\n=== Match: {timestamp} ===\n"
                    f"Players: {player1} vs {player2}\n"
                    f"Set Scores:\n"
                )

                for player, sets in set_scores.items():
                    match_summary += f"{player}: {sets}\n"

                match_summary += f"Winner: {winner}\n"
                f.write(match_summary)
                return True
        except Exception as e:
            print(f"Error saving match history: {e}")
            return False

    @staticmethod
    def get_match_history():
        """Retrieve match history"""
        try:
            with open(HISTORY_FILES["TABLE_TENNIS"], 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "No match history found."
        except Exception as e:
            return f"Error reading match history: {e}"