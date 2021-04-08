from background_task import background
from core.models import StaffCustomTeams, StaffCustomCompetition, Player, Match, ConfigController
from django.db.models import Q

from .email import EmailNotificationSystem
from .warzone_api import WarzoneApi

from . import util, signals
from .scoring import ScoringSystem
from pytz import timezone
from datetime import datetime
import time

# Competition bg jobs

# This config controller is instantiated here to avoid any issues with migrations
try:
    time_to_run = ConfigController.objects.get(name = 'main_config_controller').competitions_bg_tasks
except Exception as e:
    time_to_run = 1

def recalculate_competition_stats(custom_config, comp_name):
    '''
    Caculates all the competition stats
    based on the rest api data for 
    later use and parsing
    '''

    print()
    print('** calling recalculate_competition_stats **')

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    competition_start_time = competition.start_time # Datetime.datetime format
    competition_end_time = competition.end_time     # Datetime.datetime format
    competition_type = competition.competition_type

    team_users = {}

    teams = StaffCustomTeams.objects.filter(competition = competition.id, 
                                            checked_in = True)

    for team in teams:
        team_users = {
            team.player_1: (team.player_1_kd, team.player_1_id_type),
            team.player_2: (team.player_2_kd, team.player_2_id_type),
            team.player_3: (team.player_3_kd, team.player_3_id_type),
            team.player_4: (team.player_4_kd, team.player_4_id_type),
        }

        # Saves user to Player Model
        print('Adding Players to Player model')
        print()

        for user_id, data in team_users.items():
            player_kd = data[0]
            player_id_type = data[1]

            if user_id is not None:

                # if player_kd == null or 0 or empty
                # Then we want to recalculate it.

                if player_kd == 0 or player_kd == '' or player_kd == None:
                    print('KD Is not present for {} - Will recalculate'.format(user_id))

                    time.sleep(1)

                    warzone_api = WarzoneApi(tag = user_id, platform = player_id_type, 
                                            cod_x_rapidapi_key = custom_config["cod_x_rapidapi_key"], 
                                            cod_x_rapidapi_host = custom_config["cod_x_rapidapi_host"])
                    
                    data, error, error_message = warzone_api.get_warzone_general_stats()

                    if error == False:
                        print('New kd {} for {}'.format(user_id, data['br_all']['kdRatio']))
                        
                        player_kd = data['br_all']['kdRatio']

                        team_users[user_id] = (player_kd, player_id_type)

                        util.add_to_player_model(competition = competition,
                                                team = team,
                                                user_kd = player_kd,
                                                user_id = user_id,
                                                user_id_type = player_id_type)
                    else:
                        print('There was an error with the player data - the kd will be set as default and will not save player')
                        player_kd = 0
                        team_users[user_id] = (player_kd, player_id_type)
                else:
                    util.add_to_player_model(competition = competition,
                                            team = team,
                                            user_kd = player_kd,
                                            user_id = user_id,
                                            user_id_type = player_id_type)

        print()
        print('Ending Players to Player model')

        # Use the team_users dict to repopulate
        # Kds to those missing.
        kd_list = []

        for user, data in team_users.items():
            kd_list.append(data[0])
        
        try:
            team.player_1_kd = kd_list[0]
            team.player_2_kd = kd_list[1]
            team.player_3_kd = kd_list[2]
            team.player_4_kd = kd_list[3]
        except IndexError:
            print('Kd list is index error')

        # Cleaning none dataues from team_users
        filtered = {k: v for k, v in team_users.items() if k is not None}
        team_users.clear()
        team_users.update(filtered)

        print('******* Team Users for team {} ********'.format(team.team_name))
        print(team_users)
        print('***************************************************')

        data_list = []
        old_matches_list = []
        error_per_team_dict = {}

        for user, data in team_users.items():
            user_id_type = data[1] # Check tuple
            time.sleep(1) # Needed since our api only allows us to do one request per 1 sec
            
            clean_data, matches_without_time_filter, error, error_message = util.get_custom_data(user_tag = user, 
                                                                            user_id_type = user_id_type,
                                                                            competition_start_time = competition_start_time,
                                                                            competition_end_time = competition_end_time,
                                                                            competition_type = competition_type,
                                                                            custom_config = custom_config)

            if error:
                print()
                print('Error retriving data from {}'.format(user))
                print()
                error_per_team_dict[user] = error_message
            else:
                try:
                    # Display data
                    data_list.append(clean_data)
                    old_matches_list.append(matches_without_time_filter)

                    # Get the player object
                    player = Player.objects.get(user_id = user)

                    # Saving data into matches model object
                    print('Adding Matches to Match model')

                    user_matches_list = clean_data[user]
                    
                    for index, match in enumerate(user_matches_list):
                        match_id = match['matchID']
                        kills = match['kills']
                        kd = match['kd']
                        damage_done = match['damageDone']
                        damage_taken = match['damageTaken']
                        placement = match['teamPlacement']
                        deaths = match['deaths']
                        headshots = match['headshots']
                        team_wipes = match['teamWipes']
                        longest_streak = match['longestStreak']
                        percent_time_moving = match['percent_time_moving']
                        utc_start_time = match['utcStartSeconds']
                        time_played = match['timePlayed']

                        # Search if the match already exists if not then add it.
                        util.add_to_match_model(competition = competition, 
                                                team = team,
                                                player = player,
                                                match_id = match_id,
                                                kills = kills,
                                                kd = kd,
                                                deaths = deaths,
                                                headshots = headshots,
                                                damage_done = damage_done,
                                                damage_taken = damage_taken,
                                                placement = placement,
                                                team_wipes = team_wipes,
                                                longest_streak = longest_streak,
                                                percent_time_moving = percent_time_moving,
                                                utc_start_time = utc_start_time,
                                                time_played = time_played,
                                                player_kd_at_time = player.user_kd,
                                                index = index)
                except Exception as e:
                    print('Error: {}'.format(e))
                
                print('Ending Matches to Match model')
            
            team.errors = error_per_team_dict
            team.save()

        # match matches per team with match id
        organized_data = util.match_matches_with_matches_id(data_list, team_users)

        team_users = {}

        team = StaffCustomTeams.objects.get(team_name = team.team_name)
        team.data = data_list
        
        print()
        print('******** Loading team data_stats ********')
        print('******** Team {} ********'.format(team))
        
        # If the stats were loaded once, do not load again.
        if team.data_stats_loaded == False:
            print('******** data_stats_loaded == False ********')
            print('******** data_stats_loaded will be loaded********')
            team.data_stats = old_matches_list
            team.data_stats_loaded = True

        print('******** data_stats_loaded == True ********')
        print('******** data_stats_loaded will NOT be loaded********')
        print()

        team.data_to_render = organized_data
        team.save()


def calculate_competition_scores(comp_name):
    '''
    Parses from previous data and 
    calculates the points for each
    player and team

    Based on how many matches the user
    wants to count - The matches will be sorted
    and cut for the top 5 matches for instance
    if the key list is smaller than the number 
    set, then it will grab them all
    '''

    print()
    print('** calling calculate_competition_scores **')

    users = []

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)
    teams = StaffCustomTeams.objects.filter(competition = competition.id).order_by('-score')

    competition_scoring = {
        'points_per_kill': competition.points_per_kill,
        'points_per_first_place': competition.points_per_first_place,
        'points_per_second_place': competition.points_per_second_place,
        'points_per_third_place': competition.points_per_third_place,
        'points_per_fourth_place': competition.points_per_fourth_place,
        'points_per_fifth_place': competition.points_per_fifth_place,
    }

    for team in teams:
        users.append(team.player_1)
        users.append(team.player_2)
        users.append(team.player_3)
        users.append(team.player_4)

        total_points = []

        matches_data = team.data_to_render

        match_score = {}
        for key, val in matches_data.items():

            kills = []
            placements = []
            stim_glitch_detected = False

            for user in users:
                if user is not None:
                    try:
                        kills.append(val[user][0]['kills'])
                        placements.append(val[user][0]['teamPlacement'])

                        if val[user][0]['stimGlitch'] == True:
                            stim_glitch_detected = True

                    except Exception as e:
                        # print(e)
                        pass

            matches_data[key]['points'] = {
                'kills': kills,
                'placement': placements[0],
            }

            # Start scoring system
            scoring = ScoringSystem(competition_scoring = competition_scoring)

            points_for_kills = scoring.get_points_per_kill(sum(matches_data[key]['points']['kills']))
            points_for_placement = scoring.get_points_per_placement(matches_data[key]['points']['placement'])

            matches_data[key]['points'] = {
                'kills': points_for_kills,
                'placement': points_for_placement,
                'total_points': int(points_for_kills + points_for_placement),
                'top_match': False,
                'stim_glitch_detected': stim_glitch_detected,
            }

        print('Sorting and calculating top matches! number_of_matches_to_count_points is {}'.format(competition.number_of_matches_to_count_points))

        key_list = []

        for key, val in matches_data.items():
            dict_to_sort = {}
            dict_to_sort['key'] = key
            dict_to_sort['total_points'] = val['points']['total_points']
            key_list.append(dict_to_sort)

        key_list = sorted(key_list, key = lambda i: i['total_points'], reverse = True)

        if len(key_list) < competition.number_of_matches_to_count_points:

            print('The total amount of matches {} is smaller than number_of_matches_to_count_points {}'.format(len(key_list),
                                                                                                            competition.number_of_matches_to_count_points))
            for key in key_list[0 : len(key_list)]:

                print('-----------> Match selected for scoring with id {} and total points of {}'.format(key['key'],
                                                                                                        matches_data[key['key']]['points']['total_points']))

                # Selecting the match as a top match.
                matches_data[key['key']]['points']['top_match'] = True

                total_points.append(matches_data[key['key']]['points']['total_points'])
        else:
            print('The total amount of matches {} is greater or equal to the number_of_matches_to_count_points {}'.format(len(key_list),
                                                                                                                        competition.number_of_matches_to_count_points))
            for key in key_list[0 : competition.number_of_matches_to_count_points]:

                print('-----------> Match selected for scoring with id {} and total points of {}'.format(key['key'], 
                                                                                                        matches_data[key['key']]['points']['total_points']))

                # Selecting the match as a top match.
                matches_data[key['key']]['points']['top_match'] = True

                total_points.append(matches_data[key['key']]['points']['total_points'])
        
        print('Total points calculated {}'.format(sum(total_points)))

        team = StaffCustomTeams.objects.get(team_name = team)
        team.data_to_render = matches_data
        team.score = sum(total_points)
        team.save()


@background(schedule = time_to_run)
def calculate_status_of_competition(custom_config, comp_name):
    '''
    Calculates the status of the competition
    based on the competition ending time
    and runs background jobs that calculate
    user data and points.
    '''
    
    print()
    print('** Starting bg calculations! **')

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    # Job starts flag
    competition.manually_calculate_bg_job_status = 'Started'
    competition.save()

    # Job in-progress flag
    competition.manually_calculate_bg_job_status = 'In-Progress'
    competition.save()
    
    recalculate_competition_stats(custom_config = custom_config,
                                comp_name = comp_name)

    calculate_competition_scores(comp_name = comp_name)

    # Job ends flag
    competition.manually_calculate_bg_job_status = 'Completed'
    competition.save()

    ts = time.time()
    current_time = datetime.fromtimestamp(ts)

    start = competition.start_time
    end = competition.end_time

    print('--------')
    print('competition name: ', competition.competition_name)
    print('Current time', current_time)
    print('Start time: ', start)
    print('End time: ', end)

    if current_time.timestamp() >= start.timestamp() and not current_time.timestamp() >= end.timestamp():
        # The competition has In-Progress
        # And the competition has not ended
        competition.competition_status = 'In-Progress'
        competition.save()
        print('The competition Status is: In-Progress')

    elif current_time.timestamp() >= start.timestamp():
        # The competition Status is: Ended
        competition.competition_status = 'Ended'
        competition.save()
        print('The competition Status is: Ended')

    else:
        # The competition Status is: not Started
        competition.competition_status = 'Not-Started'
        competition.save()
        print('The competition Status is: not Started')
    
    print('--------')

    time.sleep(7)

    # Reset job
    competition.manually_calculate_bg_job_status = 'Not-Running'
    competition.save()


@background(schedule = 1)
def calculate_status_of_competition_once(custom_config, comp_name):
    '''
    Calculates the status of the 
    competition once.
    '''

    print()
    print('** Starting bg calculations once! **')

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)
    
    recalculate_competition_stats(custom_config = custom_config,
                                comp_name = comp_name)
    
    # Job in-progress flag
    competition.manually_calculate_bg_job_status = 'In-Progress'
    competition.save()

    calculate_competition_scores(comp_name = comp_name)

    # Job ends flag
    competition.manually_calculate_bg_job_status = 'Completed'
    competition.save()

    start = competition.start_time
    end = competition.end_time

    ts = time.time()
    current_time = datetime.fromtimestamp(ts)

    print('--------')
    print('competition name: ', competition.competition_name)
    print('Current time', current_time)
    print('Start time: ', start)
    print('End time: ', end)

    if current_time.timestamp() >= start.timestamp() and not current_time.timestamp() >= end.timestamp():
        # The competition has In-Progress
        # And the competition has not ended
        competition.competition_status = 'In-Progress'
        competition.save()
        print('The competition Status is: In-Progress')

    elif current_time.timestamp() >= start.timestamp():
        # The competition Status is: Ended
        competition.competition_status = 'Ended'
        competition.save()
        print('The competition Status is: Ended')

    else:
        # The competition Status is: not Started
        competition.competition_status = 'Not-Started'
        competition.save()
        print('The competition Status is: not Started')
    
    print('--------')
    time.sleep(7)

    # Reset job
    competition.manually_calculate_bg_job_status = 'Not-Running'
    competition.save()


@background(schedule = 1)
def remediate_users_kd(custom_config, comp_name):
    '''
    Remediation for all users that do not have
    their kd's loaded - We load each players kd
    and their respective existing matches with the
    player kd at time.
    '''

    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    competition.manually_calculate_bg_job_status = 'In-Progress'
    competition.save()

    players = competition.players.all()

    all_players_to_remediate = players.count()
    counter = 0

    for player in players:
        
        time.sleep(1)

        print('Remediating user {} kd'.format(player.user_id))

        try:

            warzone_api = WarzoneApi(tag = player.user_id, platform = player.user_id_type, 
                                    cod_x_rapidapi_key = custom_config["cod_x_rapidapi_key"], 
                                    cod_x_rapidapi_host = custom_config["cod_x_rapidapi_host"])

            data = warzone_api.get_warzone_general_stats()

            print('New kd {} for {}'.format(player.user_id, data['br_all']['kdRatio']))
                        
            player_kd = data['br_all']['kdRatio']
            player.user_kd = player_kd
            player.save()

            player_matches = Match.objects.filter(player = player.id, competition = competition.id)

            for match in player_matches:
                print('Updating match: {} with kd {}'.format(match.match_id, player_kd))
                match.player_kd_at_time = player_kd
                match.kd = match.kd
                match.save()

            counter += 1
            total = all_players_to_remediate - counter
            print('Total players left to remidiate {}'.format(total))
        
        except Exception as e:
            print(e)
            print('There was an error with the user')
    
    competition.manually_calculate_bg_job_status = 'Completed'
    competition.save()

    time.sleep(7)

    # Reset job
    competition.manually_calculate_bg_job_status = 'Not-Running'
    competition.save()


@background(schedule = 1)
def competition_close_inscriptions(competition_id):
    '''
    This bg job is fired when the 
    competition is created and it will
    automatically close the job when
    there are 30 minutes before the 
    competition
    '''

    competition = StaffCustomCompetition.objects.get(competition_name = competition_id)
    competition.competition_is_closed = True
    competition.save()



# Notification bg jobs
class EmailNotificationSystemJob:
    @background(schedule = 120)
    def send_check_in_notification(competition_name, competition_id):
        '''
        This job will run 120 seconds from now.

        Background job that sends email notification
        if the competition time - 1 hour is >= to 
        the current time
        '''
        
        print()
        print('** STARTING Email notification BG Job for {} with id {} **'.format(competition_name, competition_id))

        # Check that competition exist
        # If try fails, then it will mean
        # that the competition no longer 
        # exists, but there will be an
        # orphan bg job..
        competition_object_exist = False

        try:
            competition = StaffCustomCompetition.objects.get(id = competition_id)

            email_list = [team.team_captain_email for team in competition.teams.all()]

            competition_config = {
                'competition_name': competition.competition_name,
                'competition_id': competition.id,
                'start_time': competition.start_time,
                'team_emails': email_list,
            }

            competition_object_exist = True

        except Exception as e:
            print()
            print('--> Competition {} does not exist'.format(competition_name))
        
        if competition_object_exist:
            util.check_if_competition_is_one_hour_from_start(competition_config)
            competition.email_job_created = True
            competition.save()
        else:
            print('--> Competition does not exists! Orphan Bg Job with id {}'.format(competition_id))
        print('** ENDING Email notification BG Job for {} with id {} **'.format(competition_name, competition_id))
        print()
    

    @background(schedule = 1)
    def send_email_update(competiton_name, subject, body, recipients_list):
        '''
        Email updates for mass updates to
        the competition or tournament
        to all participant teams.
        '''

        email_sys = EmailNotificationSystem()

        data_email = ('Duelout Tournament Update: ' + subject,
                     body,
                    'noreply@duelout.com',
                    'something')

        all_data = []

        # Convert tuples to list 
        # to manipulate and then
        # back to tuples

        for email in recipients_list:
            new = list(data_email)
            new[-1] = [email]
            all_data.append(tuple(new))
        
        all_data = tuple(all_data)

        email_sys.send_mass_email_to_teams(all_data)
    
