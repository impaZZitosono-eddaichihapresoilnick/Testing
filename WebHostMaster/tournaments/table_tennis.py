from models import Tournament, Match, MatchSet, Player, Score
from app import db
from config import TABLE_TENNIS_CONFIG
from datetime import datetime

class TableTennisTournament:
    """Table Tennis Tournament logic implementation"""
    
    def __init__(self, tournament_id=None):
        self.tournament_id = tournament_id
        if tournament_id:
            self.tournament = Tournament.query.get(tournament_id)
        else:
            self.tournament = None
    
    def create_match(self, player1_name, player2_name, match_format=3):
        """Create a new table tennis match"""
        # Get or create players
        player1 = Player.query.filter_by(name=player1_name).first()
        if not player1:
            player1 = Player(name=player1_name)
            db.session.add(player1)
            
        player2 = Player.query.filter_by(name=player2_name).first()
        if not player2:
            player2 = Player(name=player2_name)
            db.session.add(player2)
            
        db.session.commit()
        
        # Create new match
        match = Match(
            tournament_id=self.tournament_id,
            player1_id=player1.id,
            player2_id=player2.id,
            match_format=match_format
        )
        db.session.add(match)
        db.session.commit()
        
        # Create first set
        match_set = MatchSet(
            match_id=match.id,
            set_number=1,
            player1_score=0,
            player2_score=0
        )
        db.session.add(match_set)
        db.session.commit()
        
        return match
    
    def update_score(self, match_id, player_id):
        """Update score for a player in the current set"""
        match = Match.query.get(match_id)
        if not match:
            return False, "Match not found"
        
        # Find current active set
        current_set = MatchSet.query.filter_by(match_id=match_id, completed=False).first()
        if not current_set:
            return False, "No active set found"
        
        # Update score for the player
        if player_id == match.player1_id:
            current_set.player1_score += 1
        elif player_id == match.player2_id:
            current_set.player2_score += 1
        else:
            return False, "Player not in this match"
        
        db.session.commit()
        
        # Check if set is complete
        set_winner = self.check_set_winner(match_id, current_set.id)
        if set_winner:
            # Check if match is complete
            match_winner = self.check_match_winner(match_id)
            if match_winner:
                return True, {"message": f"Match won by {match_winner.name}", "match_complete": True}
            
            # Create new set
            next_set = MatchSet(
                match_id=match_id,
                set_number=current_set.set_number + 1,
                player1_score=0,
                player2_score=0
            )
            db.session.add(next_set)
            db.session.commit()
            
            return True, {"message": f"Set won by {set_winner.name}", "match_complete": False}
        
        return True, {"message": "Score updated", "match_complete": False}
    
    def check_set_winner(self, match_id, set_id):
        """Check if there's a winner for the current set"""
        match = Match.query.get(match_id)
        current_set = MatchSet.query.get(set_id)
        
        player1_score = current_set.player1_score
        player2_score = current_set.player2_score
        
        # Check win conditions
        if ((player1_score >= TABLE_TENNIS_CONFIG["POINTS_TO_WIN_SET"]) and 
            (player1_score - player2_score >= TABLE_TENNIS_CONFIG["MIN_POINT_DIFFERENCE"])):
            current_set.winner_id = match.player1_id
            current_set.completed = True
            db.session.commit()
            return match.player1
        
        if ((player2_score >= TABLE_TENNIS_CONFIG["POINTS_TO_WIN_SET"]) and 
            (player2_score - player1_score >= TABLE_TENNIS_CONFIG["MIN_POINT_DIFFERENCE"])):
            current_set.winner_id = match.player2_id
            current_set.completed = True
            db.session.commit()
            return match.player2
        
        return None
    
    def check_match_winner(self, match_id):
        """Check if there's a winner for the match"""
        match = Match.query.get(match_id)
        
        # Count sets won by each player
        player1_sets = MatchSet.query.filter_by(match_id=match_id, winner_id=match.player1_id).count()
        player2_sets = MatchSet.query.filter_by(match_id=match_id, winner_id=match.player2_id).count()
        
        # Check win conditions based on match format
        sets_to_win = TABLE_TENNIS_CONFIG["SETS_TO_WIN"][str(match.match_format)]
        
        if player1_sets >= sets_to_win:
            match.winner_id = match.player1_id
            match.completed_at = datetime.utcnow()
            db.session.commit()
            self.update_tournament_scores(match_id)
            return match.player1
        
        if player2_sets >= sets_to_win:
            match.winner_id = match.player2_id
            match.completed_at = datetime.utcnow()
            db.session.commit()
            self.update_tournament_scores(match_id)
            return match.player2
        
        return None
    
    def update_tournament_scores(self, match_id):
        """Update tournament scores after a match is completed"""
        match = Match.query.get(match_id)
        
        if not match.tournament_id:
            return False
            
        # Count sets won by each player
        player1_sets_won = MatchSet.query.filter_by(match_id=match_id, winner_id=match.player1_id).count()
        player2_sets_won = MatchSet.query.filter_by(match_id=match_id, winner_id=match.player2_id).count()
        
        # Update or create score for player1
        p1_score = Score.query.filter_by(
            player_id=match.player1_id, 
            tournament_id=match.tournament_id
        ).first()
        
        if not p1_score:
            p1_score = Score(
                player_id=match.player1_id,
                tournament_id=match.tournament_id,
                score=player1_sets_won
            )
            db.session.add(p1_score)
        else:
            p1_score.score += player1_sets_won
        
        # Update or create score for player2
        p2_score = Score.query.filter_by(
            player_id=match.player2_id, 
            tournament_id=match.tournament_id
        ).first()
        
        if not p2_score:
            p2_score = Score(
                player_id=match.player2_id,
                tournament_id=match.tournament_id,
                score=player2_sets_won
            )
            db.session.add(p2_score)
        else:
            p2_score.score += player2_sets_won
        
        db.session.commit()
        return True
