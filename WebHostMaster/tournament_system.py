from config import TOURNAMENT_TYPES
from tournaments.table_tennis import TableTennisTournament
from tournaments.football import FootballTournament
from tournaments.math_quiz import MathQuizTournament
import sys

class CollegeTournamentSystem:
    def __init__(self):
        self.current_tournament = None
        self.players = {}  # Global players database
        self.tournament_scores = {
            "TABLE_TENNIS": {},
            "FOOTBALL": {},
            "MATH_QUIZ": {}
        }

    def display_welcome(self):
        print("\n=== College Tournament System ===")
        print("Welcome to the College Tournament System!")
        print("\nAvailable Tournaments:")
        for key, name in TOURNAMENT_TYPES.items():
            print(f"- {name}")
        print("\n")

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

    def select_tournament(self):
        print("\nSelect Tournament:")
        for i, (_, name) in enumerate(TOURNAMENT_TYPES.items(), 1):
            print(f"{i}. {name}")
        print("4. View Overall Rankings")
        print("5. Exit")

        choice = self.get_input("\nEnter your choice (1-5): ")
        return choice

    def update_tournament_scores(self, tournament_key, scoring_function):
        """Update tournament scores using the tournament's scoring function"""
        for player_name in self.players:
            score = scoring_function(player_name)
            if player_name not in self.tournament_scores[tournament_key]:
                self.tournament_scores[tournament_key][player_name] = 0
            self.tournament_scores[tournament_key][player_name] = score

    def display_overall_rankings(self):
        print("\n=== Overall Tournament Rankings ===")
        # Calculate total scores for each player across all tournaments
        total_scores = {}
        for tournament_scores in self.tournament_scores.values():
            for player, score in tournament_scores.items():
                if player not in total_scores:
                    total_scores[player] = 0
                total_scores[player] += score

        # Display rankings
        if not total_scores:
            print("No scores recorded yet.")
            return

        print("\nPlayer Rankings:")
        for i, (player, score) in enumerate(
            sorted(total_scores.items(), key=lambda x: x[1], reverse=True), 1
        ):
            print(f"{i}. {player}: {score} points")

    def run(self):
        try:
            self.display_welcome()

            while True:
                choice = self.select_tournament()

                if not choice or choice not in "12345":
                    print("Invalid choice. Please select 1-5.")
                    continue

                if choice == "5":
                    print("\nThank you for using the College Tournament System!")
                    break
                elif choice == "4":
                    self.display_overall_rankings()
                    continue
                else:
                    tournament_index = int(choice) - 1
                    tournament_key = list(TOURNAMENT_TYPES.keys())[tournament_index]
                    print(f"\nLaunching {TOURNAMENT_TYPES[tournament_key]}...")

                    # Create and run the appropriate tournament
                    if tournament_key == "TABLE_TENNIS":
                        tournament = TableTennisTournament()
                    elif tournament_key == "FOOTBALL":
                        tournament = FootballTournament()
                    elif tournament_key == "MATH_QUIZ":
                        tournament = MathQuizTournament()

                    # Run the tournament and get its scoring function
                    scoring_function = tournament.run()
                    # Update tournament scores using the scoring function
                    if scoring_function:
                        self.update_tournament_scores(tournament_key, scoring_function)

        except Exception as e:
            print(f"Fatal error: {str(e)}")
            return 1

        return 0

if __name__ == "__main__":
    sys.exit(CollegeTournamentSystem().run())