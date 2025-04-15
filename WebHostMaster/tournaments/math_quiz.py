from models import Tournament, Match, MatchSet, Player, Score
from app import db
from config import MATH_QUIZ_CONFIG
from datetime import datetime

class MathQuizTournament:
    """Math Quiz Tournament logic implementation"""
    
    def __init__(self, tournament_id=None):
        self.tournament_id = tournament_id
        if tournament_id:
            self.tournament = Tournament.query.get(tournament_id)
        else:
            self.tournament = None
    
    def create_match(self, player1_name, player2_name):
        """Create a new Math Quiz match"""
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
            match_format=MATH_QUIZ_CONFIG["ROUNDS_PER_MATCH"]
        )
        db.session.add(match)
        db.session.commit()
        
        # Create first round as a 'set'
        match_set = MatchSet(
            match_id=match.id,
            set_number=1,
            player1_score=0,
            player2_score=0
        )
        db.session.add(match_set)
        db.session.commit()
        
        return match
    
    def update_score(self, match_id, player_id, correct_answers):
        """Update score for a quiz round"""
        match = Match.query.get(match_id)
        if not match:
            return False, "Match not found"
        
        # Find current active round
        current_round = MatchSet.query.filter_by(match_id=match_id, completed=False).first()
        if not current_round:
            return False, "No active round found"
        
        # Calculate points
        points = correct_answers * MATH_QUIZ_CONFIG["POINTS_CORRECT"]
        
        # Update score for the player
        if player_id == match.player1_id:
            current_round.player1_score += points
        elif player_id == match.player2_id:
            current_round.player2_score += points
        else:
            return False, "Player not in this match"
        
        # Mark round as completed for this player
        # We'll use a custom field to track whether both players have submitted
        player_submitted = getattr(current_round, f'player{1 if player_id == match.player1_id else 2}_submitted', False)
        setattr(current_round, f'player{1 if player_id == match.player1_id else 2}_submitted', True)
        
        # If both players have submitted their answers, complete the round
        other_player_submitted = getattr(current_round, f'player{2 if player_id == match.player1_id else 1}_submitted', False)
        if other_player_submitted:
            round_winner = self.determine_round_winner(match_id, current_round.id)
            
            # Check if match is complete
            if current_round.set_number >= MATH_QUIZ_CONFIG["ROUNDS_PER_MATCH"]:
                match_winner = self.determine_match_winner(match_id)
                return True, {
                    "message": f"Match completed. Winner: {match_winner.name if match_winner else 'Draw'}",
                    "match_complete": True
                }
            
            # Create new round
            next_round = MatchSet(
                match_id=match_id,
                set_number=current_round.set_number + 1,
                player1_score=0,
                player2_score=0
            )
            db.session.add(next_round)
            db.session.commit()
            
            return True, {
                "message": f"Round {current_round.set_number} completed. Winner: {round_winner.name if round_winner else 'Draw'}",
                "match_complete": False
            }
        
        db.session.commit()
        return True, {"message": "Score submitted, waiting for other player", "match_complete": False}
    
    def determine_round_winner(self, match_id, round_id):
        """Determine the winner of a quiz round"""
        match = Match.query.get(match_id)
        current_round = MatchSet.query.get(round_id)
        
        if current_round.player1_score > current_round.player2_score:
            current_round.winner_id = match.player1_id
        elif current_round.player2_score > current_round.player1_score:
            current_round.winner_id = match.player2_id
        # If tied, no winner
        
        current_round.completed = True
        db.session.commit()
        
        return current_round.winner if current_round.winner_id else None
    
    def determine_match_winner(self, match_id):
        """Determine the winner of the match"""
        match = Match.query.get(match_id)
        
        # Count rounds won by each player
        player1_rounds = MatchSet.query.filter_by(match_id=match_id, winner_id=match.player1_id).count()
        player2_rounds = MatchSet.query.filter_by(match_id=match_id, winner_id=match.player2_id).count()
        
        if player1_rounds > player2_rounds:
            match.winner_id = match.player1_id
        elif player2_rounds > player1_rounds:
            match.winner_id = match.player2_id
        # If tied, no winner
        
        match.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Update tournament scores
        self.update_tournament_scores(match_id)
        
        return match.winner if match.winner_id else None
    
    def update_tournament_scores(self, match_id):
        """Update tournament scores after a match is completed"""
        match = Match.query.get(match_id)
        
        if not match.tournament_id:
            return False
        
        # Calculate total points for each player across all rounds
        player1_total = sum([s.player1_score for s in match.sets])
        player2_total = sum([s.player2_score for s in match.sets])
        
        # Update or create score for player1
        p1_score = Score.query.filter_by(
            player_id=match.player1_id, 
            tournament_id=match.tournament_id
        ).first()
        
        if not p1_score:
            p1_score = Score(
                player_id=match.player1_id,
                tournament_id=match.tournament_id,
                score=player1_total
            )
            db.session.add(p1_score)
        else:
            p1_score.score += player1_total
        
        # Update or create score for player2
        p2_score = Score.query.filter_by(
            player_id=match.player2_id, 
            tournament_id=match.tournament_id
        ).first()
        
        if not p2_score:
            p2_score = Score(
                player_id=match.player2_id,
                tournament_id=match.tournament_id,
                score=player2_total
            )
            db.session.add(p2_score)
        else:
            p2_score.score += player2_total
        
        db.session.commit()
        return True
