from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, SelectMultipleField, FieldList, FormField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional, NumberRange
from models import User, Team, Participant, Tournament, Event
from config import TOURNAMENT_TYPES, EVENT_TYPES, EVENT_FORMATS, TOURNAMENT_CONFIG

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# Legacy forms - kept for backward compatibility
class PlayerForm(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired(), Length(min=2, max=64)])
    submit = SubmitField('Add Player')

class TournamentForm(FlaskForm):
    name = StringField('Tournament Name', validators=[DataRequired(), Length(min=3, max=64)])
    tournament_type = SelectField('Tournament Type', choices=[(k, v) for k, v in TOURNAMENT_TYPES.items()], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Create Tournament')

class MatchForm(FlaskForm):
    tournament_id = SelectField('Tournament', coerce=int, validators=[DataRequired()])
    player1_name = StringField('Player 1 Name', validators=[DataRequired(), Length(min=2, max=64)])
    player2_name = StringField('Player 2 Name', validators=[DataRequired(), Length(min=2, max=64)])
    match_format = SelectField('Match Format', choices=[(3, 'Best of 3'), (5, 'Best of 5'), (7, 'Best of 7')], coerce=int, default=3)
    register_players = BooleanField('Register these players to your account')
    submit = SubmitField('Create Match')
    
    def validate_player2_name(self, player2_name):
        if self.player1_name.data == player2_name.data:
            raise ValidationError('Player 2 must be different from Player 1.')

# New forms for the college tournament system
class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(min=2, max=64)])
    submit = SubmitField('Create Team')
    
    def validate_name(self, name):
        team = Team.query.filter_by(name=name.data).first()
        if team is not None:
            raise ValidationError('A team with this name already exists. Please choose a different name.')

class CreateTeamForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired(), Length(min=2, max=64)])
    members = StringField('Team Members (comma-separated)', validators=[DataRequired()], 
                        description='Enter exactly 5 members, separated by commas')
    register_team = BooleanField('Register this team to your account')
    submit = SubmitField('Create Team')
    
    def validate_team_name(self, team_name):
        team = Team.query.filter_by(name=team_name.data).first()
        if team is not None:
            raise ValidationError('A team with this name already exists. Please choose a different name.')
            
    def validate_members(self, members):
        member_list = [m.strip() for m in members.data.split(',') if m.strip()]
        if len(member_list) != 5:
            raise ValidationError('You must provide exactly 5 team members.')
        
        for member in member_list:
            if len(member) < 2 or len(member) > 64:
                raise ValidationError('Each member name must be between 2 and 64 characters.')

class ParticipantForm(FlaskForm):
    name = StringField('Participant Name', validators=[DataRequired(), Length(min=2, max=64)])
    is_individual = BooleanField('Register as Individual Participant', default=True)
    team_id = SelectField('Team (if not individual)', coerce=int, validators=[Optional()], default=None)
    submit = SubmitField('Register Participant')

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired(), Length(min=2, max=64)])
    tournament_id = SelectField('Tournament', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    event_type = SelectField('Event Type', choices=[(k, v) for k, v in EVENT_TYPES.items()], validators=[DataRequired()])
    is_team_event = BooleanField('Team Event', default=False)
    event_date = StringField('Event Date (YYYY-MM-DD)', validators=[Optional()])
    scoring_system = TextAreaField('Scoring System', validators=[Optional()], 
                              description='Describe how scoring works for this event. For example: "Win = 3 points, Draw = 1 point, Loss = 0 points"')
    submit = SubmitField('Create Event')

class EventParticipantForm(FlaskForm):
    event_id = SelectField('Event', coerce=int, validators=[DataRequired()])
    participant_id = SelectField('Participant', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register for Event')

class EventResultForm(FlaskForm):
    event_id = SelectField('Event', coerce=int, validators=[DataRequired()])
    participant_id = SelectField('Participant', coerce=int, validators=[Optional()])
    team_id = SelectField('Team', coerce=int, validators=[Optional()])
    rank = IntegerField('Rank/Position (1st, 2nd, 3rd, etc.)', validators=[DataRequired(), NumberRange(min=1)])
    score = IntegerField('Score (optional)', validators=[Optional()])
    submit = SubmitField('Record Result')

class PointsSystemForm(FlaskForm):
    tournament_id = SelectField('Tournament', coerce=int, validators=[DataRequired()])
    is_team_event = BooleanField('Team Event Points', default=False)
    points_string = StringField('Points (comma-separated)', 
                               validators=[DataRequired()],
                               description='Enter points for ranks 1-6, separated by commas (e.g., "10,7,5,3,2,1")')
    submit = SubmitField('Set Points System')
    
    def validate_points_string(self, points_string):
        try:
            points = [int(p.strip()) for p in points_string.data.split(',') if p.strip()]
            if len(points) > 6:
                raise ValidationError('Please provide at most 6 point values (ranks 1-6).')
            if any(p < 0 for p in points):
                raise ValidationError('Point values must be non-negative integers.')
        except ValueError:
            raise ValidationError('Please enter only numbers separated by commas.')

class TeamTournamentForm(FlaskForm):
    name = StringField('Tournament Name', validators=[DataRequired(), Length(min=3, max=64)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    max_teams = IntegerField('Maximum Teams', validators=[DataRequired(), NumberRange(min=1)], default=TOURNAMENT_CONFIG["TEAM"]["MAX_TEAMS"])
    submit = SubmitField('Create Team Tournament')
    
class IndividualTournamentForm(FlaskForm):
    name = StringField('Tournament Name', validators=[DataRequired(), Length(min=3, max=64)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    max_individuals = IntegerField('Maximum Individual Participants', validators=[DataRequired(), NumberRange(min=1)], default=TOURNAMENT_CONFIG["INDIVIDUAL"]["MAX_INDIVIDUALS"])
    submit = SubmitField('Create Individual Tournament')
