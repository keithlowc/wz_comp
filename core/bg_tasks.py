from background_task import background
from core.models import StaffCustomTeams, StaffCustomCompetition

from . import util, signals
from pytz import timezone
from datetime import datetime
import time

@background(schedule = 1)
def recalculate_competition_stats(comp_name):
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

    team_users = []

    teams = StaffCustomTeams.objects.filter(competition = competition.id)

    for team in teams:
        team_users.append(team.player_1)
        team_users.append(team.player_2)
        team_users.append(team.player_3)
        team_users.append(team.player_4)

        data_list = []

        for users in team_users:
            if users is not None:
                time.sleep(1)
                clean_data = util.get_custom_data(users, competition_start_time, competition_end_time, competition_type)
                data_list.append(clean_data)

        team_users = []

        team = StaffCustomTeams.objects.get(team_name = team.team_name)
        team.data = data_list
        team.save()


@background(schedule = 1)
def calculate_competition_scores(comp_name):
    '''
    Parses from previous data and 
    calculates the points for each
    player and team
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

        data = team.data
        
        scoring_data = []

        kills = []
        placement = []

        score_for_kills = 0

        for user in users:
            if user is not None:
                for person in data:
                    kills_dict = {}
                    placement_dict = {}

                    try:
                        new_data = person[user]
                        for info in new_data:
                            kills.append(info['kills'])
                            placement.append(info['teamPlacement'])

                        kills_dict['kills'] = kills
                        placement_dict['placement'] = placement

                        new_data = {
                            user: {
                                'kills': kills,
                                'placement': placement,
                            }
                        }

                        scoring_data.append(new_data)
                    except Exception as e:
                        print('Json for USER  was Not found')

                for val in scoring_data:
                    try:
                        score_for_kills = sum(val[user]['kills']) * competition.points_per_kill
                    except Exception as e:
                        print('User is not found inside of scoring data')

        print('--------------> Results: The score for team {} is {}'.format(team, score_for_kills))

        team = StaffCustomTeams.objects.get(team_name = team)
        team.data_to_score = scoring_data
        team.score = score_for_kills
        team.save()


@background(schedule = 1)
def calculate_status_of_competition(comp_name):
    '''
    Calculates the status of the competition
    based on the competition ending time
    and runs background jobs that calculate
    user data and points.
    '''
    print()
    print('** Starting bg calculations! **')

    recalculate_competition_stats(comp_name)
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
    print('--------')

    # Status
    # 'In-Progress': 1,
    # 'Ended': 2,
    # 'Not started': 3,

    if current_time.timestamp() >= start.timestamp() and not current_time.timestamp() >= end.timestamp():
        # The competition has In-Progress
        # And the competition has not ended
        competition.competition_status = 1
        competition.save()
        print('** The competition Status is: In-Progress **')

    elif current_time.timestamp() >= start.timestamp():
        # The competition Status is: Ended
        competition.competition_status = 2
        competition.save()
        print('** The competition Status is: Ended **')

    else:
        # The competition Status is: not Started
        competition.competition_status = 3
        competition.save()
        print('** The competition Status is: not Started **')
        

