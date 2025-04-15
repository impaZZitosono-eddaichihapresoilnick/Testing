from config import TABLE_TENNIS_CONFIG
from game_history import GameHistory
import sys

class TableTennisScoringSystem:
    def __init__(self):
        self.players = {}
        self.set_scores = {}
        self.current_set = 1
        self.match_format = None
        self.sets_to_win = None

    def display_welcome(self):
        print("\n=== Table Tennis Tournament ===")
        print("Rules:")
        print("- Each set is won by the first player to reach 11 points")
        print("- A 2-point lead is required to win a set")
        print("- Match can be configured as best of 3, 5, or 7 sets\n")

    def get_input(self, prompt, allow_empty=False):
        """Safe input handling with EOF and interrupt handling"""
        try:
            print(prompt, end='', flush=True)
            value = input().strip()
            if not allow_empty and not value:
                return None
            return value
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)

    def configure_match(self):
        while True:
            format_choice = self.get_input("Select match format (3/5/7) [default: 3]: ", allow_empty=True) or "3"
            if format_choice in TABLE_TENNIS_CONFIG["SETS_TO_WIN"]:
                self.match_format = int(format_choice)
                self.sets_to_win = TABLE_TENNIS_CONFIG["SETS_TO_WIN"][format_choice]
                print(f"Match format set to best of {format_choice} sets")
                return True
            print("Invalid format. Please choose 3, 5, or 7.")

    def add_players(self):
        while True:
            player1 = self.get_input("Enter Player 1 name: ")
            if not player1:
                print("Error: Please enter a name for Player 1.")
                continue

            player2 = self.get_input("Enter Player 2 name: ")
            if not player2:
                print("Error: Please enter a name for Player 2.")
                continue

            if player1 == player2:
                print("Error: Players must have different names.")
                continue

            self.players = {player1: 0, player2: 0}
            self.set_scores = {player1: [], player2: []}
            print(f"Players {player1} and {player2} added successfully!")
            return True

    def update_score(self, player):
        if player not in self.players:
            print(f"Error: Player '{player}' not found.")
            return False

        self.players[player] += 1
        self.display_scores()
        self.check_set_winner()
        return True

    def check_set_winner(self):
        for player, score in self.players.items():
            opponent_score = min([s for p, s in self.players.items() if p != player])
            if (score >= TABLE_TENNIS_CONFIG["POINTS_TO_WIN_SET"] and 
                abs(score - opponent_score) >= TABLE_TENNIS_CONFIG["MIN_POINT_DIFFERENCE"]):
                self.set_scores[player].append(score)
                print(f"\nSet {self.current_set} won by {player}!")

                if self.sets_to_win and len(self.set_scores[player]) >= self.sets_to_win:
                    self.end_match(player)
                else:
                    self.start_new_set()
                return True
        return False

    def start_new_set(self):
        self.current_set += 1
        for player in self.players:
            self.players[player] = 0
        print(f"\nStarting Set {self.current_set}!")

    def end_match(self, winner):
        print(f"\n🏆 Match Winner: {winner}! 🏆")
        try:
            GameHistory.save_match(
                list(self.players.keys())[0],
                list(self.players.keys())[1],
                self.set_scores,
                winner
            )
        except Exception as e:
            print(f"Warning: Could not save match history - {str(e)}")

        self.display_final_scores()
        self.reset_match()

    def reset_match(self):
        self.players = {}
        self.set_scores = {}
        self.current_set = 1
        self.match_format = None
        self.sets_to_win = None

    def display_scores(self):
        print(f"\nSet {self.current_set} Scores:")
        for player, score in self.players.items():
            print(f"{player}: {score} points ({len(self.set_scores[player])} sets won)")

    def display_final_scores(self):
        print("\nFinal Match Results:")
        for player in self.set_scores:
            print(f"{player}: {len(self.set_scores[player])} sets won")
            print(f"Set scores: {self.set_scores[player]}")

    def display_history(self):
        print("\n=== Match History ===")
        history = GameHistory.get_match_history()
        print(history)

    def run(self):
        try:
            self.display_welcome()

            while True:
                if not self.match_format:
                    self.configure_match()
                    self.add_players()

                print("\nOptions:")
                print("1. Score point for Player 1")
                print("2. Score point for Player 2")
                print("3. View match history")
                print("4. Start new match")
                print("5. Exit")

                choice = self.get_input("Choose an option (1-5): ")

                if not choice:
                    print("Please enter a valid option (1-5).")
                    continue

                if choice in ["1", "2"]:
                    player = list(self.players.keys())[int(choice) - 1]
                    self.update_score(player)
                elif choice == "3":
                    self.display_history()
                elif choice == "4":
                    self.reset_match()
                elif choice == "5":
                    print("\nThanks for using the Table Tennis Scoring System!")
                    break
                else:
                    print("Invalid option. Please choose 1-5.")

        except Exception as e:
            print(f"Fatal error: {str(e)}")
            return 1

        return 0

if __name__ == "__main__":
    sys.exit(TableTennisScoringSystem().run())