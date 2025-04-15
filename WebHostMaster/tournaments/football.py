from models import Tournament, Match, Player, Score
from app import db
from config import FOOTBALL_CONFIG
from datetime import datetime

class FootballTournament:
    """Football Tournament logic implementation"""
    
    def __init__(self, tournament_id=None):
        self.tournament_id = tournament_id
        if tournament_id:
            self.tournament = Tournament.query.get(tournament_id)
        else:
            self.tournament = None
    
    def create_match(self, team1_name, team2_name):
        """Create a new football match"""
        # Get or create teams (represented as players in the database)
        team1 = Player.query.filter_by(name=team1_name).first()
        if not team1:
            team1 = Player(name=team1_name)
            db.session.add(team1)
            
        team2 = Player.query.filter_by(name=team2_name).first()
        if not team2:
            team2 = Player(name=team2_name)
            db.session.add(team2)
            
        db.session.commit()
        
        # Create new match
        match = Match(
            tournament_id=self.tournament_id,
            player1_id=team1.id,  # Team 1
            player2_id=team2.id,  # Team 2
            match_format=1  # Not applicable for football, but needed for database
        )
        db.session.add(match)
        db.session.commit()
        
        return match
    
    def update_score(self, match_id, team1_score, team2_score):
        """Update final score for a football match"""
        match = Match.query.get(match_id)
        if not match:
            return False, "Match not found"
        
        # Update match score by creating a single set with final scores
        match_set = MatchSet(
            match_id=match_id,
            set_number=1,
            player1_score=team1_score,
            player2_score=team2_score,
            completed=True
        )
        
        # Determine winner
        if team1_score > team2_score:
            match_set.winner_id = match.player1_id
            match.winner_id = match.player1_id
        elif team2_score > team1_score:
            match_set.winner_id = match.player2_id
            match.winner_id = match.player2_id
        # If draw, no winner is set
        
        match.completed_at = datetime.utcnow()
        db.session.add(match_set)
        db.session.commit()
        
        # Update tournament scores
        self.update_tournament_scores(match_id, team1_score, team2_score)
        
        return True, {
            "message": "Match completed", 
            "winner": match.winner.name if match.winner_id else "Draw"
        }
    
    def update_tournament_scores(self, match_id, team1_score, team2_score):
        """Update tournament scores after a match is completed"""
        match = Match.query.get(match_id)
        
        if not match.tournament_id:
            return False
        
        # Calculate points based on win/draw/loss
        team1_points = 0
        team2_points = 0
        
        if team1_score > team2_score:
            team1_points = FOOTBALL_CONFIG["POINTS_WIN"]
            team2_points = FOOTBALL_CONFIG["POINTS_LOSS"]
        elif team2_score > team1_score:
            team1_points = FOOTBALL_CONFIG["POINTS_LOSS"]
            team2_points = FOOTBALL_CONFIG["POINTS_WIN"]
        else:  # Draw
            team1_points = FOOTBALL_CONFIG["POINTS_DRAW"]
            team2_points = FOOTBALL_CONFIG["POINTS_DRAW"]
        
        # Update or create score for team1
        t1_score = Score.query.filter_by(
            player_id=match.player1_id, 
            tournament_id=match.tournament_id
        ).first()
        
        if not t1_score:
            t1_score = Score(
                player_id=match.player1_id,
                tournament_id=match.tournament_id,
                score=team1_points
            )
            db.session.add(t1_score)
        else:
            t1_score.score += team1_points
        
        # Update or create score for team2
        t2_score = Score.query.filter_by(
            player_id=match.player2_id, 
            tournament_id=match.tournament_id
        ).first()
        
        if not t2_score:
            t2_score = Score(
                player_id=match.player2_id,
                tournament_id=match.tournament_id,
                score=team2_points
            )
            db.session.add(t2_score)
        else:
            t2_score.score += team2_points
        
        db.session.commit()
        return True
