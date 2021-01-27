from background_task import background
from core.models import StaffCustomTeams, StaffCustomCompetition

from . import util, signals
from pytz import timezone
from datetime import datetime
import time

@background(schedule = 1)
def recalculate_competition_stats(cod_x_rapidapi_key, cod_x_rapidapi_host, comp_name):
    '''
    Caculates all the competition stack
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

    teams = StaffCustomTeams.objects.filter(competition = competition.id)

    for team in teams:
        team_users = {
            team.player_1: team.player_1_id_type,
            team.player_2: team.player_2_id_type,
            team.player_3: team.player_3_id_type,
            team.player_4: team.player_4_id_type,
        }

        filtered = {k: v for k, v in team_users.items() if k is not None}
        team_users.clear()
        team_users.update(filtered)

        print('******* Team Users ********')
        print(team_users)
        print('***************************')

        data_list = []
        old_matches_list = []

        for user, user_id_type in team_users.items():
            time.sleep(1)
            clean_data, matches_without_time_filter = util.get_custom_data(user, user_id_type, competition_start_time, competition_end_time, competition_type, cod_x_rapidapi_key, cod_x_rapidapi_host)

            data_list.append(clean_data)
            old_matches_list.append(matches_without_time_filter)

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

    for team in teams:
        users.append(team.player_1)
        users.append(team.player_2)
        users.append(team.player_3)
        users.append(team.player_4)

        total_points = []

        data = team.data_to_render

        match_score = {}
        for key, val in data.items():

            kills = []
            placements = []
            for user in users:
                if user is not None:
                    try:
                        kills.append(val[user][0]['kills'])
                        placements.append(val[user][0]['teamPlacement'])
                    except Exception as e:
                        print(e)

            data[key]['points'] = {
                'kills': kills,
                'placement': placements[0],
            }

            points_for_kills = sum(data[key]['points']['kills']) * competition.points_per_kill

            if data[key]['points']['placement'] == 1:
                placement = competition.points_per_first_place
            elif data[key]['points']['placement'] == 2:
                placement = competition.points_per_second_place
            elif data[key]['points']['placement'] == 3:
                placement = competition.points_per_third_place
            else:
                placement = 0

            data[key]['points'] = {
                'kills': points_for_kills,
                'placement': placement,
                'total_points': int(points_for_kills + placement),
            }

        print('Sorting and calculating top matches! number_of_matches_to_count_points is {}'.format(competition.number_of_matches_to_count_points))

        key_list = []

        for key, val in data.items():
            dict_to_sort = {}
            dict_to_sort['key'] = key
            dict_to_sort['total_points'] = val['points']['total_points']
            key_list.append(dict_to_sort)

        key_list = sorted(key_list, key = lambda i: i['total_points'], reverse = True)

        if len(key_list) < competition.number_of_matches_to_count_points:
            print('The total amount of matches {} is smaller than number_of_matches_to_count_points {}'.format(len(key_list), competition.number_of_matches_to_count_points))
            for key in key_list[0 : len(key_list)]:
                print('-----------> Match selected for scoring with id {} and total points of {}'.format(key['key'], data[key['key']]['points']['total_points']))
                total_points.append(data[key['key']]['points']['total_points'])
        else:
            print('The total amount of matches {} is greater or equal to the number_of_matches_to_count_points {}'.format(len(key_list), competition.number_of_matches_to_count_points))
            for key in key_list[0 : competition.number_of_matches_to_count_points]:
                print('-----------> Match selected for scoring with id {} and total points of {}'.format(key['key'], data[key['key']]['points']['total_points']))
                total_points.append(data[key['key']]['points']['total_points'])

        team = StaffCustomTeams.objects.get(team_name = team)
        team.data_to_render = data
        team.score = sum(total_points)
        team.save()


@background(schedule = 1)
def calculate_status_of_competition(config, comp_name):
    '''
    Calculates the status of the competition
    based on the competition ending time
    and runs background jobs that calculate
    user data and points.
    '''
    print()
    print('** Starting bg calculations! **')

    recalculate_competition_stats(config.cod_x_rapidapi_key, config.cod_x_rapidapi_host, comp_name)
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

