from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    participants = db.relationship('Participant', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('Participant', backref='team', lazy=True)
    event_results = db.relationship('EventResult', backref='team', lazy=True)
    
    def __repr__(self):
        return f'<Team {self.name}>'


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    is_individual = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    event_participations = db.relationship('EventParticipant', backref='participant', lazy=True)
    event_results = db.relationship('EventResult', backref='participant', lazy=True)
    
    def __repr__(self):
        if self.is_individual:
            return f'<Individual {self.name}>'
        else:
            return f'<Team Member {self.name} of {self.team.name}>'


# Legacy classes for backwards compatibility
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    matches_as_player1 = db.relationship('Match', foreign_keys='Match.player1_id', backref='player1', lazy=True)
    matches_as_player2 = db.relationship('Match', foreign_keys='Match.player2_id', backref='player2', lazy=True)
    scores = db.relationship('Score', backref='player', lazy=True)
    
    def __repr__(self):
        return f'<Player {self.name}>'


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tournament_type = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    max_teams = db.Column(db.Integer, default=4)
    max_individuals = db.Column(db.Integer, default=20)
    
    # Relationships
    matches = db.relationship('Match', backref='tournament', lazy=True)
    scores = db.relationship('Score', backref='tournament', lazy=True)
    events = db.relationship('Event', backref='tournament', lazy=True)
    
    def __repr__(self):
        return f'<Tournament {self.name}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(32), nullable=False)  # ACADEMIC, SPORTS, CREATIVE, etc.
    is_team_event = db.Column(db.Boolean, default=False)
    event_date = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scoring_system = db.Column(db.Text, nullable=True)  # Description of how scoring works for this event
    
    # Relationships
    participants = db.relationship('EventParticipant', backref='event', lazy=True)
    results = db.relationship('EventResult', backref='event', lazy=True)
    
    def __repr__(self):
        event_type = 'Team' if self.is_team_event else 'Individual'
        return f'<{event_type} Event {self.name} for {self.tournament.name}>'


class EventParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Participant {self.participant.name} in Event {self.event.name}>'


class EventResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    rank = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, default=0)
    points_awarded = db.Column(db.Integer, default=0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        if self.team_id:
            return f'<Result: Team {self.team.name} ranked {self.rank} in {self.event.name}>'
        else:
            return f'<Result: {self.participant.name} ranked {self.rank} in {self.event.name}>'


class PointsSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    is_team_event = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        event_type = 'Team' if self.is_team_event else 'Individual'
        return f'<{event_type} Points: Rank {self.rank} = {self.points} points>'


# Legacy models for backwards compatibility
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=True)
    player1_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    match_format = db.Column(db.Integer, default=3)  # Best of 3, 5, or 7
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sets = db.relationship('MatchSet', backref='match', lazy=True)
    winner = db.relationship('Player', foreign_keys=[winner_id])
    
    def __repr__(self):
        return f'<Match {self.id}: {self.player1.name} vs {self.player2.name}>'


class MatchSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    player1_score = db.Column(db.Integer, default=0)
    player2_score = db.Column(db.Integer, default=0)
    winner_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    
    # Relationship
    winner = db.relationship('Player', foreign_keys=[winner_id])
    
    def __repr__(self):
        return f'<Set {self.set_number} of Match {self.match_id}>'


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Score {self.player.name} in {self.tournament.name}: {self.score}>'
