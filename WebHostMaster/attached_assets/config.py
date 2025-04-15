# Configuration settings for the College Tournament System

# Tournament Types
TOURNAMENT_TYPES = {
    "TABLE_TENNIS": "Table Tennis",
    "FOOTBALL": "Football",
    "MATH_QUIZ": "Mathematics Quiz"
}

# Table Tennis Configuration
TABLE_TENNIS_CONFIG = {
    "POINTS_TO_WIN_SET": 11,
    "MIN_POINT_DIFFERENCE": 2,
    "SETS_TO_WIN": {
        "3": 2,  # Best of 3
        "5": 3,  # Best of 5
        "7": 4   # Best of 7
    }
}

# Football Configuration
FOOTBALL_CONFIG = {
    "TEAM_SIZE": 5,
    "NUM_TEAMS": 2,
    "MATCH_DURATION": 90,  # minutes
    "POINTS_WIN": 3,
    "POINTS_DRAW": 1,
    "POINTS_LOSS": 0
}

# Math Quiz Configuration
MATH_QUIZ_CONFIG = {
    "QUESTIONS_PER_ROUND": 10,
    "TIME_PER_QUESTION": 60,  # seconds
    "POINTS_CORRECT": 10,
    "POINTS_WRONG": 0,
    "ROUNDS_PER_MATCH": 3
}

# History file paths
HISTORY_FILES = {
    "TABLE_TENNIS": "history/table_tennis_history.txt",
    "FOOTBALL": "history/football_history.txt",
    "MATH_QUIZ": "history/math_quiz_history.txt",
    "OVERALL": "history/tournament_history.txt"
}