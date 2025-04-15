# Configuration settings for the College Tournament System

# Tournament Types
TOURNAMENT_TYPES = {
    "INDIVIDUAL": "Individual Tournament",
    "TEAM": "Team Tournament"
}

# Table Tennis Configuration has been removed as requested

# Event Types
EVENT_TYPES = {
    "SPORTS": "Sports",
    "ACADEMIC": "Academic",
    "CREATIVE": "Creative",
    "TECHNICAL": "Technical",
    "GAMING": "Gaming"
}

# Event Format
EVENT_FORMATS = {
    "INDIVIDUAL": "Individual",
    "TEAM": "Team"
}

# Default Points System
# Points awarded based on rank in each event
DEFAULT_POINTS_SYSTEM = {
    1: 10,  # 1st place: 10 points
    2: 7,   # 2nd place: 7 points
    3: 5,   # 3rd place: 5 points
    4: 3,   # 4th place: 3 points
    5: 2,   # 5th place: 2 points
    6: 1    # 6th place: 1 point
}

# Tournament Configuration
TOURNAMENT_CONFIG = {
    "TEAM": {
        "MAX_TEAMS": 4,
        "TEAM_SIZE": 5,
        "POINTS_SYSTEM": DEFAULT_POINTS_SYSTEM
    },
    "INDIVIDUAL": {
        "MAX_INDIVIDUALS": 20,
        "POINTS_SYSTEM": DEFAULT_POINTS_SYSTEM
    }
}

# Team Tournament Events
TEAM_EVENTS = [
    {
        "name": "Football",
        "type": "SPORTS",
        "is_team_event": True,
        "description": "College football tournament with 5-player teams",
        "scoring_system": "Win = 3 points, Draw = 1 point, Loss = 0 points. Teams ranked by total points."
    },
    {
        "name": "Dodgeball",
        "type": "SPORTS",
        "is_team_event": True,
        "description": "Team dodgeball competition with elimination format",
        "scoring_system": "Win = advance to next round. Final rankings determine points (1st = 10pts, 2nd = 7pts, 3rd = 5pts)."
    },
    {
        "name": "Debate",
        "type": "ACADEMIC",
        "is_team_event": True,
        "description": "Structured debate on assigned topic with teams of 5",
        "scoring_system": "Judges score on argumentation (40pts), rebuttal (30pts), presentation (20pts), and teamwork (10pts)."
    }
]

# Individual Tournament Events
INDIVIDUAL_EVENTS = [
    {
        "name": "Math Quiz",
        "type": "ACADEMIC",
        "is_team_event": False,
        "description": "Individual math problem-solving competition with time limits",
        "scoring_system": "Each correct answer = 1 point. Tie-breaker based on completion time."
    },
    {
        "name": "100m Sprint",
        "type": "SPORTS",
        "is_team_event": False,
        "description": "100-meter sprint race on a standard track",
        "scoring_system": "Participants ranked by finish time. Points awarded based on finishing position."
    }
]

# Combined Sample Events (used for tournament creation)
SAMPLE_EVENTS = TEAM_EVENTS + INDIVIDUAL_EVENTS

# History file paths
HISTORY_FILES = {
    "INDIVIDUAL": "history/individual_tournament_history.txt",
    "TEAM": "history/team_tournament_history.txt",
    "OVERALL": "history/tournament_history.txt"
}