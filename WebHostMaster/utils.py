from models import Tournament, Match, MatchSet, Player, Score, Team, Participant, Event, EventResult
from app import db
from sqlalchemy import func
from config import HISTORY_FILES
import os

def get_tournament_history():
    """Get tournament history from the database"""
    history = {}
    
    # Get all tournament types from the database
    tournament_types = db.session.query(Tournament.tournament_type).distinct().all()
    tournament_types = [t[0] for t in tournament_types if t[0] is not None]
    
    # Get history for each tournament type
    for tournament_type in tournament_types:
        if tournament_type != "OVERALL" and tournament_type != "COLLEGE_TOURNAMENT":
            try:
                tournaments = Tournament.query.filter_by(tournament_type=tournament_type).all()
                tournament_data = []
                
                for tournament in tournaments:
                    matches = Match.query.filter_by(tournament_id=tournament.id).all()
                    match_data = []
                    
                    for match in matches:
                        if match.winner_id:  # Only include completed matches
                            match_info = {
                                'id': match.id,
                                'player1': match.player1.name if match.player1 else "Unknown",
                                'player2': match.player2.name if match.player2 else "Unknown",
                                'winner': match.winner.name if match.winner else "Unknown",
                                'sets': []
                            }
                            
                            for match_set in match.sets:
                                match_info['sets'].append({
                                    'set_number': match_set.set_number,
                                    'player1_score': match_set.player1_score,
                                    'player2_score': match_set.player2_score,
                                    'winner': match_set.winner.name if match_set.winner else None
                                })
                            
                            match_data.append(match_info)
                    
                    tournament_data.append({
                        'id': tournament.id,
                        'name': tournament.name,
                        'matches': match_data
                    })
                
                history[tournament_type] = tournament_data
            except Exception as e:
                print(f"Error getting history for tournament type {tournament_type}: {str(e)}")
                # Add empty list for this tournament type
                history[tournament_type] = []
    
    return history

def get_overall_rankings():
    """Get overall player rankings across all tournaments"""
    # Calculate aggregated scores for each player across all tournaments
    scores = db.session.query(
        Player.id,
        Player.name,
        func.sum(Score.score).label('total_score'),
        func.count(Score.tournament_id.distinct()).label('tournaments_played')
    ).join(Score).group_by(Player.id).order_by(func.sum(Score.score).desc()).all()
    
    # Format the results
    rankings = []
    for idx, (player_id, player_name, total_score, tournaments_played) in enumerate(scores, 1):
        try:
            # Get tournament breakdown
            tournament_scores = db.session.query(
                Tournament.name,
                Score.score
            ).join(Score).filter(Score.player_id == player_id).all()
            
            tournaments = [{'name': t_name, 'score': t_score} for t_name, t_score in tournament_scores]
            
            rankings.append({
                'rank': idx,
                'player_id': player_id,
                'player_name': player_name,
                'total_score': total_score,
                'tournaments_played': tournaments_played,
                'tournaments': tournaments
            })
        except Exception as e:
            print(f"Error processing player {player_name}: {str(e)}")
            # Add a basic entry without tournament details if there's an error
            rankings.append({
                'rank': idx,
                'player_id': player_id,
                'player_name': player_name,
                'total_score': total_score or 0,
                'tournaments_played': tournaments_played or 0,
                'tournaments': []
            })
    
    return rankings

def get_college_tournament_rankings(tournament_id):
    """Get rankings for a specific college tournament"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament or tournament.tournament_type != 'COLLEGE_TOURNAMENT':
        return [], []
    
    # Get individual rankings
    individual_results = db.session.query(
        Participant.id,
        Participant.name,
        func.sum(EventResult.points_awarded).label('total_points'),
        func.count(Event.id.distinct()).label('events_participated')
    ).join(
        EventResult, 
        EventResult.participant_id == Participant.id
    ).join(
        Event, 
        EventResult.event_id == Event.id
    ).filter(
        Event.tournament_id == tournament_id,
        Participant.is_individual == True
    ).group_by(
        Participant.id
    ).order_by(
        func.sum(EventResult.points_awarded).desc()
    ).all()
    
    # Format individual rankings
    individual_rankings = []
    for idx, (participant_id, participant_name, total_points, events_participated) in enumerate(individual_results, 1):
        # Get event breakdown
        event_results = db.session.query(
            Event.name,
            EventResult.points_awarded,
            EventResult.rank
        ).join(
            EventResult,
            EventResult.event_id == Event.id
        ).filter(
            Event.tournament_id == tournament_id,
            EventResult.participant_id == participant_id
        ).all()
        
        events = [{'name': e_name, 'points': e_points, 'rank': e_rank} for e_name, e_points, e_rank in event_results]
        
        individual_rankings.append({
            'rank': idx,
            'participant_id': participant_id,
            'participant_name': participant_name,
            'total_points': total_points,
            'events_participated': events_participated,
            'events': events
        })
    
    # Get team rankings
    team_results = db.session.query(
        Team.id,
        Team.name,
        func.sum(EventResult.points_awarded).label('total_points'),
        func.count(Event.id.distinct()).label('events_participated')
    ).join(
        EventResult, 
        EventResult.team_id == Team.id
    ).join(
        Event, 
        EventResult.event_id == Event.id
    ).filter(
        Event.tournament_id == tournament_id
    ).group_by(
        Team.id
    ).order_by(
        func.sum(EventResult.points_awarded).desc()
    ).all()
    
    # Format team rankings
    team_rankings = []
    for idx, (team_id, team_name, total_points, events_participated) in enumerate(team_results, 1):
        # Get event breakdown
        event_results = db.session.query(
            Event.name,
            EventResult.points_awarded,
            EventResult.rank
        ).join(
            EventResult,
            EventResult.event_id == Event.id
        ).filter(
            Event.tournament_id == tournament_id,
            EventResult.team_id == team_id
        ).all()
        
        events = [{'name': e_name, 'points': e_points, 'rank': e_rank} for e_name, e_points, e_rank in event_results]
        
        # Get team members
        members = Participant.query.filter_by(team_id=team_id).all()
        member_names = [member.name for member in members]
        
        team_rankings.append({
            'rank': idx,
            'team_id': team_id,
            'team_name': team_name,
            'total_points': total_points,
            'events_participated': events_participated,
            'events': events,
            'members': member_names
        })
    
    return individual_rankings, team_rankings

def create_directories():
    """Create necessary directories if they don't exist"""
    # Create history directory if it doesn't exist
    os.makedirs('history', exist_ok=True)
    
    # Create empty history files if they don't exist
    for file_path in HISTORY_FILES.values():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('')

# Initialize necessary directories
create_directories()
