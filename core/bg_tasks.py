from background_task import background
from core.models import StaffCustomTeams, StaffCustomCompetition, Player, Match

from .email import EmailNotificationSystem

from . import util, signals
from .scoring import ScoringSystem
from pytz import timezone
from datetime import datetime
import time

# Competition bg jobs

@background(schedule = 1)
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
            team.player_1: team.player_1_id_type,
            team.player_2: team.player_2_id_type,
            team.player_3: team.player_3_id_type,
            team.player_4: team.player_4_id_type,
        }

        # Saves user to Player Model
        util.pprintstart('Adding Players to Player model')

        for user_id, user_id_type in team_users.items():
            if user_id is not None:
                util.add_to_player_model(competition = competition,
                                        team = team,
                                        user_id = user_id,
                                        user_id_type = user_id_type)

        util.pprintstart('Ending Players to Player model')

        # Cleaning none values
        filtered = {k: v for k, v in team_users.items() if k is not None}
        team_users.clear()
        team_users.update(filtered)

        print('******* Team Users for team {} ********'.format(team.team_name))
        print(team_users)
        print('***************************')

        data_list = []
        old_matches_list = []

        for user, user_id_type in team_users.items():
            time.sleep(1)
            error_with_user = False
            
            try:
                clean_data, matches_without_time_filter = util.get_custom_data(user_tag = user, 
                                                                            user_id_type = user_id_type,
                                                                            competition_start_time = competition_start_time,
                                                                            competition_end_time = competition_end_time,
                                                                            competition_type = competition_type,
                                                                            custom_config = custom_config)

                # Display data
                data_list.append(clean_data)
                old_matches_list.append(matches_without_time_filter)

                # Get the player object
                player = Player.objects.get(competition = competition,
                                            team = team,
                                            user_id = user)

                # Saving data into matches model object
                util.pprintstart('Adding Matches to Match model')

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
                                            index = index)
                
                util.pprintstart('Ending Matches to Match model')
            except Exception as e:
                print('THERE WAS AN ISSUE WITH THE PLAYERS DATA - SO I WILL NOT LOAD THE {} DATA'.format(user))
                error_with_user = True

        if not error_with_user:
            # match matches per team with match id
            organized_data = util.match_matches_with_matches_id(data_list, team_users)

            team_users = {}

            team = StaffCustomTeams.objects.get(team_name = team.team_name)
            team.data = data_list
            
            print()
            print('-- Loading team data_stats --')
            print('-- Team {} --'.format(team))
            # If the stats were loaded once, do not load again.
            if team.data_stats_loaded == False:
                print('-- data_stats_loaded == False --')
                print('-- data_stats_loaded will be loaded--')
                team.data_stats = old_matches_list
                team.data_stats_loaded = True

            print('-- data_stats_loaded == True --')
            print('-- data_stats_loaded will NOT be loaded--')
            print()

            team.data_to_render = organized_data
            team.save()


@background(schedule = 1)
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
            for user in users:
                if user is not None:
                    try:
                        kills.append(val[user][0]['kills'])
                        placements.append(val[user][0]['teamPlacement'])
                    except Exception as e:
                        # print(e)
                        pass

            matches_data[key]['points'] = {
                'kills': kills,
                'placement': placements[0],
            }

            # Start scoring system
            scoring = ScoringSystem(competition_scoring = competition_scoring)

            # team_rank = scoring.check_tier_with_kd(team_kd)
            # match_rank = scoring.check_tier_with_kd(match_kd)

            # team_rank_position = scoring.get_position_from_tier(team_rank)
            # match_rank_position = scoring.get_position_from_tier(match_rank)

            # team_rank_tolerance_high = team_rank_position + 4
            # team_rank_tolerance_low = team_rank_position - 4

            # rank_movement = team_rank_tolerance_low - match_rank_position
            # total_ranks_before_team_rank_tolerance_low = team_rank_tolerance_low - 1

            # CALCULATE PERCETAGE
            # total_pct = 100 / total_ranks_before_team_rank_tolerance_low
            # total_penalty = rank_movement * total_pct

            # if skbmm_normalizing:
            # 


            points_for_kills = scoring.get_points_per_kill(sum(matches_data[key]['points']['kills']))
            points_for_placement = scoring.get_points_per_placement(matches_data[key]['points']['placement'])

            matches_data[key]['points'] = {
                'kills': points_for_kills,
                'placement': points_for_placement,
                'total_points': int(points_for_kills + points_for_placement),
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

                total_points.append(matches_data[key['key']]['points']['total_points'])
        else:
            print('The total amount of matches {} is greater or equal to the number_of_matches_to_count_points {}'.format(len(key_list),
                                                                                                                         competition.number_of_matches_to_count_points))
            for key in key_list[0 : competition.number_of_matches_to_count_points]:

                print('-----------> Match selected for scoring with id {} and total points of {}'.format(key['key'], 
                                                                                                        matches_data[key['key']]['points']['total_points']))

                total_points.append(matches_data[key['key']]['points']['total_points'])
        
        print('Total points calculated {}'.format(sum(total_points)))

        team = StaffCustomTeams.objects.get(team_name = team)
        team.data_to_render = matches_data
        team.score = sum(total_points)
        team.save()


@background(schedule = 1)
def calculate_status_of_competition(custom_config, comp_name):
    '''
    Calculates the status of the competition
    based on the competition ending time
    and runs background jobs that calculate
    user data and points.
    '''
    print()
    print('** Starting bg calculations! **')

    recalculate_competition_stats(custom_config, comp_name)
    calculate_competition_scores(comp_name)

    ts = time.time()
    current_time = datetime.fromtimestamp(ts)
    competition = StaffCustomCompetition.objects.get(competition_name = comp_name)

    start = competition.start_time
    end = competition.end_time

    print('--------')
    print('competition name: ', competition.competition_name)
    print('Current time', current_time)
    print('Start time: ', start)
    print('End time: ', end)

    # Status
    # 'In-Progress': 1,
    # 'Ended': 2,
    # 'Not started': 3,

    if current_time.timestamp() >= start.timestamp() and not current_time.timestamp() >= end.timestamp():
        # The competition has In-Progress
        # And the competition has not ended
        competition.competition_status = 1
        competition.save()
        print('The competition Status is: In-Progress')

    elif current_time.timestamp() >= start.timestamp():
        # The competition Status is: Ended
        competition.competition_status = 2
        competition.save()
        print('The competition Status is: Ended')

    else:
        # The competition Status is: not Started
        competition.competition_status = 3
        competition.save()
        print('The competition Status is: not Started')
    
    print('--------')

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
    
