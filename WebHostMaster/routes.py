from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from models import (User, Player, Tournament, Match, MatchSet, Score, 
                   Team, Participant, Event, EventParticipant, EventResult, PointsSystem)
from forms import (LoginForm, RegistrationForm, PlayerForm, TournamentForm, MatchForm,
                  TeamForm, CreateTeamForm, ParticipantForm, EventForm, EventParticipantForm,
                  EventResultForm, PointsSystemForm, TeamTournamentForm, IndividualTournamentForm)
from config import (TOURNAMENT_TYPES, EVENT_TYPES, EVENT_FORMATS,
                   TOURNAMENT_CONFIG, SAMPLE_EVENTS, DEFAULT_POINTS_SYSTEM,
                   TEAM_EVENTS, INDIVIDUAL_EVENTS)
from utils import get_tournament_history, get_overall_rankings, get_college_tournament_rankings
from datetime import datetime
import logging
import json

# Home route
@app.route('/')
def index():
    tournaments = Tournament.query.filter_by(is_active=True).all()
    recent_matches = Match.query.order_by(Match.created_at.desc()).limit(5).all()
    
    # Get tournaments by type
    individual_tournaments = Tournament.query.filter_by(tournament_type='INDIVIDUAL', is_active=True).all()
    team_tournaments = Tournament.query.filter_by(tournament_type='TEAM', is_active=True).all()
    
    events = Event.query.order_by(Event.event_date.desc()).limit(5).all()
    return render_template('index.html', 
                           tournaments=tournaments, 
                           recent_matches=recent_matches,
                           individual_tournaments=individual_tournaments,
                           team_tournaments=team_tournaments,
                           events=events,
                           tournament_types=TOURNAMENT_TYPES)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))
    
    return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

# User profile
@app.route('/profile')
@login_required
def profile():
    player_records = Player.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', 
                           title='Profile', 
                           player_records=player_records)

# Tournament routes
@app.route('/tournaments')
def tournaments():
    active_tournaments = Tournament.query.filter_by(is_active=True).all()
    completed_tournaments = Tournament.query.filter_by(is_active=False).all()
    return render_template('tournaments/index.html', 
                           title='Tournaments',
                           active_tournaments=active_tournaments,
                           completed_tournaments=completed_tournaments)

@app.route('/tournaments/create', methods=['GET', 'POST'])
@login_required
def create_tournament():
    form = TournamentForm()
    if form.validate_on_submit():
        tournament = Tournament(
            name=form.name.data,
            tournament_type=form.tournament_type.data,
            description=form.description.data
        )
        db.session.add(tournament)
        db.session.commit()
        
        flash(f'Tournament "{form.name.data}" has been created!', 'success')
        return redirect(url_for('tournaments'))
    
    return render_template('tournaments/create.html', 
                           title='Create Tournament', 
                           form=form)

@app.route('/tournaments/<int:tournament_id>')
def tournament_detail_legacy(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    matches = Match.query.filter_by(tournament_id=tournament_id).order_by(Match.created_at.desc()).all()
    scores = Score.query.filter_by(tournament_id=tournament_id).order_by(Score.score.desc()).all()
    
    # For legacy tournament types, direct to their specific templates
    if tournament.tournament_type not in ['INDIVIDUAL', 'TEAM']:
        return render_template(f'tournaments/{tournament.tournament_type.lower()}.html',
                           title=tournament.name,
                           tournament=tournament,
                           matches=matches,
                           scores=scores)
    # For new tournament types, redirect to our detailed view
    else:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))

# Table Tennis routes
# The table tennis section has been removed as requested

# Rankings and history
@app.route('/rankings')
def rankings():
    rankings = get_overall_rankings()
    return render_template('tournaments/rankings.html', 
                           title='Overall Rankings',
                           rankings=rankings)

@app.route('/history')
def history():
    tournament_history = get_tournament_history()
    return render_template('tournaments/history.html',
                           title='Tournament History',
                           history=tournament_history)

# Tournament Routes
@app.route('/tournaments/individual')
def individual_tournaments():
    active_tournaments = Tournament.query.filter_by(tournament_type='INDIVIDUAL', is_active=True).all()
    completed_tournaments = Tournament.query.filter_by(tournament_type='INDIVIDUAL', is_active=False).all()
    return render_template('college/index.html', 
                          title='Individual Tournaments',
                          active_tournaments=active_tournaments,
                          completed_tournaments=completed_tournaments)

@app.route('/tournaments/team')
def team_tournaments():
    active_tournaments = Tournament.query.filter_by(tournament_type='TEAM', is_active=True).all()
    completed_tournaments = Tournament.query.filter_by(tournament_type='TEAM', is_active=False).all()
    return render_template('college/index.html', 
                          title='Team Tournaments',
                          active_tournaments=active_tournaments,
                          completed_tournaments=completed_tournaments)

@app.route('/tournaments/individual/create', methods=['GET', 'POST'])
@login_required
def create_individual_tournament():
    if not current_user.is_admin:
        flash('You need administrator privileges to create tournaments.', 'danger')
        return redirect(url_for('individual_tournaments'))
        
    form = IndividualTournamentForm()
    if form.validate_on_submit():
        tournament = Tournament(
            name=form.name.data,
            tournament_type='INDIVIDUAL',
            description=form.description.data,
            max_individuals=form.max_individuals.data
        )
        db.session.add(tournament)
        db.session.commit()
        
        # Create default points system for the tournament
        for rank, points in DEFAULT_POINTS_SYSTEM.items():
            # For individual events
            individual_points = PointsSystem(
                tournament_id=tournament.id,
                rank=rank,
                points=points,
                is_team_event=False
            )
            db.session.add(individual_points)
        
        # Create specific individual events (Math Quiz and 100m Sprint)
        for event_data in INDIVIDUAL_EVENTS:
            event = Event(
                name=event_data['name'],
                tournament_id=tournament.id,
                description=event_data['description'],
                event_type=event_data['type'],
                is_team_event=False,
                event_date=datetime.now(),
                scoring_system=event_data.get('scoring_system', '')
            )
            db.session.add(event)
        
        db.session.commit()
        
        flash(f'Individual Tournament "{form.name.data}" has been created with events and points system!', 'success')
        return redirect(url_for('tournament_detail', tournament_id=tournament.id))
    
    return render_template('college/create_individual_tournament.html', 
                          title='Create Individual Tournament', 
                          form=form)

@app.route('/tournaments/team/create', methods=['GET', 'POST'])
@login_required
def create_team_tournament():
    if not current_user.is_admin:
        flash('You need administrator privileges to create tournaments.', 'danger')
        return redirect(url_for('team_tournaments'))
        
    form = TeamTournamentForm()
    if form.validate_on_submit():
        tournament = Tournament(
            name=form.name.data,
            tournament_type='TEAM',
            description=form.description.data,
            max_teams=form.max_teams.data
        )
        db.session.add(tournament)
        db.session.commit()
        
        # Create default points system for the tournament
        for rank, points in DEFAULT_POINTS_SYSTEM.items():
            # For team events
            team_points = PointsSystem(
                tournament_id=tournament.id,
                rank=rank,
                points=points,
                is_team_event=True
            )
            db.session.add(team_points)
        
        # Create specific team events (Football, Dodgeball, and Debate)
        for event_data in TEAM_EVENTS:
            event = Event(
                name=event_data['name'],
                tournament_id=tournament.id,
                description=event_data['description'],
                event_type=event_data['type'],
                is_team_event=True,
                event_date=datetime.now(),
                scoring_system=event_data.get('scoring_system', '')
            )
            db.session.add(event)
        
        db.session.commit()
        
        flash(f'Team Tournament "{form.name.data}" has been created with events and points system!', 'success')
        return redirect(url_for('tournament_detail', tournament_id=tournament.id))
    
    return render_template('college/create_team_tournament.html', 
                          title='Create Team Tournament', 
                          form=form)

@app.route('/tournaments/<int:tournament_id>/details')
def tournament_detail(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    
    events = Event.query.filter_by(tournament_id=tournament_id).order_by(Event.event_date).all()
    
    if tournament.tournament_type == 'TEAM':
        teams = Team.query.join(Participant).filter_by(is_individual=False).all()
        return render_template('college/tournament_detail.html',
                             title=tournament.name,
                             tournament=tournament,
                             events=events,
                             teams=teams,
                             is_team_tournament=True)
    elif tournament.tournament_type == 'INDIVIDUAL':
        individuals = Participant.query.filter_by(is_individual=True).all()
        return render_template('college/tournament_detail.html',
                             title=tournament.name,
                             tournament=tournament,
                             events=events,
                             individuals=individuals,
                             is_team_tournament=False)
    else:
        # Legacy tournament types
        return render_template('tournaments/detail.html',
                             title=tournament.name,
                             tournament=tournament)
                             
@app.route('/tournaments/<int:tournament_id>/delete', methods=['POST'])
@login_required
def delete_tournament(tournament_id):
    if not current_user.is_admin:
        flash('You need administrator privileges to delete tournaments.', 'danger')
        return redirect(url_for('tournaments'))
    
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament_name = tournament.name
    
    # Delete related events first (which will cascade to event participants and results)
    events = Event.query.filter_by(tournament_id=tournament_id).all()
    for event in events:
        # Delete event participants
        EventParticipant.query.filter_by(event_id=event.id).delete()
        
        # Delete event results
        EventResult.query.filter_by(event_id=event.id).delete()
        
        # Delete the event
        db.session.delete(event)
    
    # Delete points system
    PointsSystem.query.filter_by(tournament_id=tournament_id).delete()
    
    # Delete any scores related to this tournament
    Score.query.filter_by(tournament_id=tournament_id).delete()
    
    # Delete any matches and match sets related to this tournament
    matches = Match.query.filter_by(tournament_id=tournament_id).all()
    for match in matches:
        MatchSet.query.filter_by(match_id=match.id).delete()
        db.session.delete(match)
    
    # Delete the tournament
    db.session.delete(tournament)
    db.session.commit()
    
    flash(f'Tournament "{tournament_name}" and all associated data have been deleted.', 'success')
    
    if tournament.tournament_type == 'TEAM':
        return redirect(url_for('team_tournaments'))
    else:
        return redirect(url_for('individual_tournaments'))

@app.route('/teams')
def teams():
    all_teams = Team.query.all()
    return render_template('college/teams.html', 
                          title='Teams',
                          teams=all_teams)

@app.route('/teams/create', methods=['GET', 'POST'])
@login_required
def create_team():
    form = CreateTeamForm()
    if form.validate_on_submit():
        # Create the team
        team = Team(name=form.team_name.data)
        db.session.add(team)
        db.session.commit()
        
        # Parse and create team members
        member_list = []
        if form.members.data:
            member_list = [m.strip() for m in form.members.data.split(',') if m.strip()]
        
        for member_name in member_list:
            member = Participant(
                name=member_name,
                user_id=current_user.id if form.register_team.data else None,
                team_id=team.id,
                is_individual=False
            )
            db.session.add(member)
        
        db.session.commit()
        
        flash(f'Team "{form.team_name.data}" has been created with {len(member_list)} members!', 'success')
        return redirect(url_for('team_detail', team_id=team.id))
    
    return render_template('college/create_team.html', 
                          title='Create Team', 
                          form=form)

@app.route('/teams/<int:team_id>')
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    members = Participant.query.filter_by(team_id=team.id).all()
    event_results = EventResult.query.filter_by(team_id=team.id).all()
    
    return render_template('college/team_detail.html',
                          title=f'Team: {team.name}',
                          team=team,
                          members=members,
                          event_results=event_results)

@app.route('/participants')
def participants():
    individuals = Participant.query.filter_by(is_individual=True).all()
    return render_template('college/participants.html', 
                          title='Individual Participants',
                          participants=individuals)

@app.route('/participants/register', methods=['GET', 'POST'])
@login_required
def register_participant():
    form = ParticipantForm()
    
    # Get all teams
    teams = Team.query.all()
    if teams:
        form.team_id.choices = [('0', 'None')] + [(str(t.id), t.name) for t in teams]
    else:
        form.team_id.choices = [('0', 'None')]
    
    if form.validate_on_submit():
        participant = Participant(
            name=form.name.data,
            user_id=current_user.id,
            team_id=form.team_id.data if not form.is_individual.data and form.team_id.data != 0 else None,
            is_individual=form.is_individual.data
        )
        db.session.add(participant)
        db.session.commit()
        
        if form.is_individual.data:
            flash(f'Individual participant "{form.name.data}" has been registered!', 'success')
            return redirect(url_for('participant_detail', participant_id=participant.id))
        else:
            flash(f'Team member "{form.name.data}" has been registered!', 'success')
            return redirect(url_for('team_detail', team_id=form.team_id.data))
    
    return render_template('college/register_participant.html', 
                          title='Register Participant', 
                          form=form)

@app.route('/participants/<int:participant_id>')
def participant_detail(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    event_results = EventResult.query.filter_by(participant_id=participant.id).all()
    
    return render_template('college/participant_detail.html',
                          title=f'Participant: {participant.name}',
                          participant=participant,
                          event_results=event_results)

@app.route('/events')
def events():
    all_events = Event.query.all()
    return render_template('college/events.html', 
                          title='Events',
                          events=all_events)

@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if not current_user.is_admin:
        flash('You need administrator privileges to create events.', 'danger')
        return redirect(url_for('events'))
    
    # Check if there are any tournaments
    tournaments = Tournament.query.filter(Tournament.tournament_type.in_(['INDIVIDUAL', 'TEAM'])).all()
    if not tournaments:
        flash('No tournaments found. Create a tournament first.', 'info')
        return redirect(url_for('create_individual_tournament'))
        
    form = EventForm()
    form.tournament_id.choices = [(str(t.id), t.name) for t in tournaments]
    
    if form.validate_on_submit():
        event = Event(
            name=form.name.data,
            tournament_id=form.tournament_id.data,
            description=form.description.data,
            event_type=form.event_type.data,
            is_team_event=form.is_team_event.data,
            event_date=datetime.strptime(form.event_date.data, '%Y-%m-%d') if form.event_date.data else None,
            scoring_system=form.scoring_system.data if form.scoring_system.data else None
        )
        db.session.add(event)
        db.session.commit()
        
        flash(f'Event "{form.name.data}" has been created!', 'success')
        return redirect(url_for('event_detail', event_id=event.id))
    
    return render_template('college/create_event.html', 
                          title='Create Event', 
                          form=form)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    participants = EventParticipant.query.filter_by(event_id=event.id).all()
    results = EventResult.query.filter_by(event_id=event.id).order_by(EventResult.rank).all()
    
    return render_template('college/event_detail.html',
                          title=f'Event: {event.name}',
                          event=event,
                          participants=participants,
                          results=results)
                          
@app.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin:
        flash('You need administrator privileges to delete events.', 'danger')
        return redirect(url_for('events'))
    
    event = Event.query.get_or_404(event_id)
    event_name = event.name
    tournament_id = event.tournament_id
    
    # Delete event participants
    EventParticipant.query.filter_by(event_id=event_id).delete()
    
    # Delete event results
    EventResult.query.filter_by(event_id=event_id).delete()
    
    # Delete the event
    db.session.delete(event)
    db.session.commit()
    
    flash(f'Event "{event_name}" and all associated data have been deleted.', 'success')
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))

@app.route('/events/<int:event_id>/register', methods=['GET', 'POST'])
@login_required
def register_for_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    form = EventParticipantForm()
    form.event_id.data = event_id  # Pre-set the event ID
    
    # Set up participant choices based on event type
    if event.is_team_event:
        teams = Team.query.all()
        if teams:
            form.participant_id.choices = [(str(t.id), t.name) for t in teams]
        else:
            form.participant_id.choices = [("-1", "No teams available - create a team first")]
    else:
        individuals = Participant.query.filter_by(is_individual=True).all()
        if individuals:
            form.participant_id.choices = [(str(p.id), p.name) for p in individuals]
        else:
            form.participant_id.choices = [("-1", "No individuals available - register participants first")]
    
    if form.validate_on_submit():
        # For team events
        if event.is_team_event:
            # Check if the selection is valid
            if form.participant_id.data == "-1":
                flash('No teams available. Create a team first.', 'warning')
                return redirect(url_for('create_team'))
                
            # Check if team is already registered
            team_id = form.participant_id.data
            existing = EventParticipant.query.filter_by(
                event_id=event_id, 
                team_id=team_id
            ).first()
            
            if existing:
                flash('This team is already registered for this event.', 'warning')
                return redirect(url_for('event_detail', event_id=event_id))
            
            # Register all team members
            team = Team.query.get(team_id)
            members = Participant.query.filter_by(team_id=team.id).all()
            
            for member in members:
                event_participant = EventParticipant(
                    event_id=event_id,
                    participant_id=member.id,
                    team_id=team.id
                )
                db.session.add(event_participant)
            
            db.session.commit()
            flash(f'Team "{team.name}" has been registered for the event!', 'success')
            
        # For individual events
        else:
            # Check if the selection is valid
            if form.participant_id.data == "-1":
                flash('No individual participants available. Register a participant first.', 'warning')
                return redirect(url_for('register_participant'))
                
            participant_id = form.participant_id.data
            existing = EventParticipant.query.filter_by(
                event_id=event_id, 
                participant_id=participant_id
            ).first()
            
            if existing:
                flash('This participant is already registered for this event.', 'warning')
                return redirect(url_for('event_detail', event_id=event_id))
            
            participant = Participant.query.get(participant_id)
            event_participant = EventParticipant(
                event_id=event_id,
                participant_id=participant_id
            )
            db.session.add(event_participant)
            db.session.commit()
            
            flash(f'Participant "{participant.name}" has been registered for the event!', 'success')
        
        return redirect(url_for('event_detail', event_id=event_id))
    
    return render_template('college/register_for_event.html', 
                          title=f'Register for {event.name}', 
                          form=form,
                          event=event)

@app.route('/events/<int:event_id>/record-result', methods=['GET', 'POST'])
@login_required
def record_event_result(event_id):
    if not current_user.is_admin:
        flash('You need administrator privileges to record results.', 'danger')
        return redirect(url_for('event_detail', event_id=event_id))
        
    event = Event.query.get_or_404(event_id)
    
    form = EventResultForm()
    form.event_id.data = event_id  # Pre-set the event ID
    
    if event.is_team_event:
        # Get registered teams for this event
        registered_teams = db.session.query(Team).join(EventParticipant).filter(EventParticipant.event_id == event_id).distinct().all()
        if registered_teams:
            form.team_id.choices = [(str(t.id), t.name) for t in registered_teams]
        else:
            form.team_id.choices = [("-1", 'No teams registered for this event')]
        form.participant_id.choices = [("0", 'N/A - Team Event')]
    else:
        # Get registered individuals for this event
        registered_participants = db.session.query(Participant).join(EventParticipant).filter(
            EventParticipant.event_id == event_id,
            Participant.is_individual == True
        ).all()
        if registered_participants:
            form.participant_id.choices = [(str(p.id), p.name) for p in registered_participants]
        else:
            form.participant_id.choices = [("-1", 'No individuals registered for this event')]
        form.team_id.choices = [("0", 'N/A - Individual Event')]
    
    if form.validate_on_submit():
        if event.is_team_event:
            if form.team_id.data == "-1":
                flash('No teams registered for this event. Please register teams first.', 'warning')
                return redirect(url_for('register_for_event', event_id=event_id))
            elif form.team_id.data == "0":
                flash('Please select a team for team events.', 'danger')
                return redirect(url_for('record_event_result', event_id=event_id))
            
        if not event.is_team_event:
            if form.participant_id.data == "-1":
                flash('No individuals registered for this event. Please register participants first.', 'warning')
                return redirect(url_for('register_for_event', event_id=event_id))
            elif form.participant_id.data == "0":
                flash('Please select a participant for individual events.', 'danger')
                return redirect(url_for('record_event_result', event_id=event_id))
            
        # Check for duplicate rank
        existing_rank = EventResult.query.filter_by(
            event_id=event_id, 
            rank=form.rank.data
        ).first()
        
        if existing_rank:
            flash(f'Rank {form.rank.data} is already assigned for this event.', 'warning')
            return redirect(url_for('record_event_result', event_id=event_id))
            
        # Get points for this rank from the points system
        points_system = PointsSystem.query.filter_by(
            tournament_id=event.tournament_id,
            rank=form.rank.data,
            is_team_event=event.is_team_event
        ).first()
        
        points_awarded = points_system.points if points_system else 0
        
        # Record the result
        result = EventResult(
            event_id=event_id,
            participant_id=form.participant_id.data if not event.is_team_event else None,
            team_id=form.team_id.data if event.is_team_event else None,
            rank=form.rank.data,
            score=form.score.data or 0,
            points_awarded=points_awarded
        )
        db.session.add(result)
        
        # Check if all participants have results and mark event as completed if so
        if event.is_team_event:
            total_teams = db.session.query(EventParticipant).filter_by(event_id=event_id).distinct(EventParticipant.team_id).count()
            total_results = EventResult.query.filter_by(event_id=event_id).count()
            
            if total_results >= total_teams:
                event.is_completed = True
        else:
            total_participants = EventParticipant.query.filter_by(event_id=event_id).count()
            total_results = EventResult.query.filter_by(event_id=event_id).count()
            
            if total_results >= total_participants:
                event.is_completed = True
        
        db.session.commit()
        
        if event.is_team_event:
            team = Team.query.get(form.team_id.data)
            flash(f'Result recorded for team "{team.name}" with rank {form.rank.data}!', 'success')
        else:
            participant = Participant.query.get(form.participant_id.data)
            flash(f'Result recorded for participant "{participant.name}" with rank {form.rank.data}!', 'success')
        
        return redirect(url_for('event_detail', event_id=event_id))
    
    return render_template('college/record_result.html', 
                          title=f'Record Result for {event.name}', 
                          form=form,
                          event=event)

@app.route('/tournaments/rankings')
def tournament_rankings():
    # Get all tournaments of both types
    tournaments = Tournament.query.filter(Tournament.tournament_type.in_(['INDIVIDUAL', 'TEAM'])).all()
    tournament_id = request.args.get('tournament_id', type=int)
    
    # Check if there are any tournaments
    if not tournaments:
        flash('No tournaments found. Create a tournament first.', 'info')
        return redirect(url_for('tournaments'))
    
    if tournament_id:
        tournament = Tournament.query.get_or_404(tournament_id)
        individual_rankings, team_rankings = get_college_tournament_rankings(tournament_id)
        
        events = Event.query.filter_by(tournament_id=tournament_id).all()
        
        return render_template('college/rankings.html', 
                              title=f'{tournament.name} Rankings',
                              tournament=tournament,
                              individual_rankings=individual_rankings if tournament.tournament_type == 'INDIVIDUAL' else [],
                              team_rankings=team_rankings if tournament.tournament_type == 'TEAM' else [],
                              tournaments=tournaments,
                              events=events)
    else:
        # Just show the tournament selection page or redirect to first tournament
        if tournaments:
            return render_template('college/rankings.html',
                                 title='Tournament Rankings',
                                 tournaments=tournaments,
                                 tournament=tournaments[0],
                                 individual_rankings=[],
                                 team_rankings=[],
                                 events=[])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
