from .warzone_api import WarzoneApi
from .email import EmailNotificationSystem

from core.models import StaffCustomTeams, Player, Match

import datetime, time

from itertools import groupby


def pprintstart(message):
    print()
    print(message)


def calculate_average(matches, element):
    ratios = []
    for match in matches:
        kd = match['playerStats'][element]
        ratios.append(kd)
    
    avg = sum(ratios) / len(ratios)

    return '{:.3f}'.format(avg)

# Matches related

def exclude_matches_of_type(matches_list, competition_type_list):
    '''
    Exclude matches that contain
    the competition type assigned

    Exclude this one too br_dmz_plunquad
    '''

    clean_matches = []

    for match in matches_list:
        if match["mode"] not in competition_type_list:
            clean_matches.append(match)
        else:
            print("Skipped this match")
            print("The match mode is {}".format(match["mode"]))
    
    return clean_matches


def filter_matches(matches_list, competition_type):
    '''
    Filter matches based on type
    '''

    print()
    print('** Started to filter matches **')

    new_matches_list = []

    if competition_type == 'SQUADS':
        match_type = 'br_brquads'
    elif competition_type == 'TRIOS':
        match_type = 'br_brtrios'
    elif competition_type == 'DUOS':
        match_type = 'br_brduos'
    elif competition_type == 'SOLOS':
        match_type = 'br_brsolo'

    for match in matches_list:
        if match['mode'] == match_type:
            new_matches_list.append(match)

    for match in new_matches_list:
        print('The match mode is {} - By {} - Match #ID {}'.format(match['mode'], match['player']['username'], match['matchID']))
    
    return new_matches_list


def get_values_from_matches(matches_list, message, user_tag = None):
    
    all_matches = []

    print('Player name: {} for {}'.format(matches_list[0]['player']['username'], message))

    for index, matches in enumerate(matches_list):
        # print('Player name: {}'.format(matches['player']['username']))

        data = {}
        try:
            # Plunder matches do not have positioning 
            # This is important because we are getting 
            # that initial data for our graphs.
            data['matchID'] = matches['matchID']
            data['kd'] = matches['playerStats']['kdRatio']
            data['kills'] = matches['playerStats']['kills']
            data['deaths'] = matches['playerStats']['deaths']
            data['headshots'] = matches['playerStats']['headshots']
            data['damageDone'] = matches['playerStats']['damageDone']
            data['damageTaken'] = matches['playerStats']['damageTaken']
            data['teamPlacement'] = matches['playerStats']['teamPlacement']

            all_matches.append(data)
        except Exception as e:
            print('SKIPPING this match since there was an error with: {} - Match type {}'.format(e, matches['mode']))
    
    if user_tag is not None:

        final_data = {}
        final_data[str(user_tag)] = all_matches
        return final_data

    else:
        return all_matches


def match_matches_with_matches_id(data_list, team_users):
    '''
    Solution on https://stackoverflow.com/questions/65432225/merge-these-two-json-objects-based-on-a-specific-key-inside-of-them-in-python/65432494#65432494
    Matches each user with one match
    and same users with the same match id

    matches = [
        {
            'match_id': 123,
            'placement': 2,
            'klowerito': {
                'kills': 6,
                'damage': 900,
                'kd': 2.5
            },
            'klowerito': {
                'kills': 6,
                'damage': 900,
                'kd': 2.5
            }
        }
    ]
    '''

    dics = {}
    for k1 in data_list:
        for k2 in k1:        
            for e in k1[k2]:
                m = e.get('matchID', None)
                if m is None: continue
                if not m in dics: dics[m] = {}
                dics[m].update({k2: collect_data(k2, m, data_list)})
    
    return dics


def collect_data(key_id, match_id, data_list):
    '''
    https://stackoverflow.com/questions/65432225/merge-these-two-json-objects-based-on-a-specific-key-inside-of-them-in-python/65432494#65432494
    '''

    d = []
    for k1 in data_list:
        for k2 in k1:
            if k2 != key_id: continue
            for e in k1[k2]:
                if e.get('matchID', None) == match_id:
                    e1 = e.copy()
                    e1.pop('matchID')
                    d.append(e1)
    return d


def filter_for_time(custom_config, matches_list, competition_start_time, competition_end_time, threshold_time_seconds = 7200):
    '''
    Filters matches for 2 hours by default

    threshold = value from end_time - start_time. ie = 2 hours range
    start_time = 1 pm  - match_time = 1:30 pm = delta = 0:30
    if delta 0:30 < 2 and 1:30 pm <= end_time
    add to lists values
    '''

    custom_config = custom_config

    if custom_config["competitions_dummy_data"]:
        start_time = matches_list[0]['utcStartSeconds']

        print()
        print('** Using Dummy data **')
        print('The start_time: ', start_time)

        dummy_matches = []

        for match in matches_list:
            dummy_matches.append(match)
        
        return dummy_matches[0:5]

    else:
        # Should slice the matches based on the 
        # time range give.
        start_time = competition_start_time
        end_time = competition_end_time
    
        print()
        print('** Using Real Sliced data **')
        print('The start_time: ', start_time)

        top_matches = []

        for match in matches_list:
            match_time = datetime.datetime.fromtimestamp(match['utcStartSeconds'])

            print('Match time: {}'.format(match_time))

            if match_time >= start_time and match_time <= end_time:
                top_matches.append(match)
                print('--------------> {} - Selected Match with Start Time: {} - Competition Start Time {} and END TIME: {}'.format(len(top_matches), 
                                                                        datetime.datetime.fromtimestamp(match['utcStartSeconds']),
                                                                        start_time, end_time))

        return top_matches


def get_custom_data(user_tag, user_id_type, competition_start_time, competition_end_time, competition_type, custom_config):
    '''
    Gets the matches for user_tag
    '''

    warzone_api = WarzoneApi(tag = user_tag.replace('#', '%23'),
                             platform = user_id_type, 
                             cod_x_rapidapi_key = custom_config["cod_x_rapidapi_key"], 
                             cod_x_rapidapi_host = custom_config["cod_x_rapidapi_host"])
    
    matches = warzone_api.get_warzone_matches()

    total_matches_len = len(matches['matches'])

    # For dummy data return all matches 
    # From last match 2 hours before
    # And we are not filtering the matches
    # So we get any match
    if custom_config["competitions_dummy_data"]:
        filtered_matches = matches['matches']
    else:
        filtered_matches = filter_matches(matches['matches'][0:total_matches_len - 1],
                                        competition_type)

    matches_without_time_filter = matches['matches'][0:total_matches_len - 1] # All matches

    data = filter_for_time(custom_config = custom_config,
                          matches_list = filtered_matches, 
                          competition_start_time = competition_start_time,
                          competition_end_time = competition_end_time)

    clean_data = get_values_from_matches(matches_list = data, 
                                        message = 'Clean data',
                                        user_tag = user_tag)

    matches_without_time_filter = exclude_matches_of_type(matches_list = matches_without_time_filter, 
                                                        competition_type_list = ['br_dmz_plnbld',
                                                                                'br_dmz_plndtrios',
                                                                                'br_dmz_plndval1',
                                                                                'brtdm_rmbl',
                                                                                'brtdm_wzrumval2'])

    matches_without_time_filter = get_values_from_matches(matches_list = matches_without_time_filter,
                                                         message = 'Matches without time filter',
                                                         user_tag = user_tag)

    return clean_data, matches_without_time_filter


def add_to_player_model(competition, team, user_id, user_id_type):
    '''
    Adds to the player model
    if the player does not 
    already exist in the model
    '''

    player_found = True
    try:
        Player.objects.get(competition = competition, 
                            team = team, 
                            user_id = user_id, 
                            user_id_type = user_id_type)
    except Exception as e:
        player_found = False
    
    if not player_found:
        print('Saving Player {} to model'.format(user_id))
        Player.objects.create(competition = competition, 
                                team = team, 
                                user_id = user_id,
                                user_id_type = user_id_type)
    else:
        print('Not saving Player {} since it already exists in db!'.format(user_id))


def add_to_match_model(competition, team, player, match_id, kills, kd, deaths, headshots, damage_done, damage_taken, placement, index):
    '''
    Adds the match to the MATCH model
    if this match with
    '''

    found_match = True
    try:
        Match.objects.get(competition = competition, 
                            team = team, 
                            player = player, 
                            match_id = match_id)
    except Exception as e:
        found_match = False

    if not found_match:
        Match.objects.create(competition = competition, 
                                team = team,
                                player = player,
                                match_id = match_id,
                                kills = kills, 
                                kd = kd,
                                deaths = deaths,
                                headshots = headshots, 
                                damage_done = damage_done,
                                damage_taken = damage_taken, 
                                placement = placement)

        print('Match #{} saved!'.format(index))
    else:
        print('Match #{} already exist in db!'.format(index))


# Email notifications related

def check_if_competition_is_one_hour_from_start(competition_config):
    '''
    This function is used on the bg taks for
    email notifications.

    It is running to see if the competition time
    - 1 hour is = to current time. If equal then we
    want to send the email or return true
    '''

    current_time = datetime.datetime.now()

    start_time = competition_config['start_time']

    delta = start_time - current_time

    print()
    print('--> Current server time {}'.format(current_time))
    print('--> Competition start time {}'.format(start_time))
    print('--> Total Delta {}'.format(delta))
    print('--> Email list: {}'.format(competition_config['team_emails']))
    print()

    # If competition time is 1 hour before the current time
    if (delta <= datetime.timedelta(hours = 1)):
        email_sys = EmailNotificationSystem()

        # Email data
        subject = 'Check-In to competition: {}'.format(competition_config['competition_name'])
        competition_name = competition_config['competition_name']

        # Look into the teams that have not been sent email check in
        if len(competition_config['team_emails']) > 0:

            for email in competition_config['team_emails']:
                team = StaffCustomTeams.objects.get(team_captain_email = email, competition_id = competition_config['competition_id'])
                uuid = team.checked_in_uuid

                check_in_url = 'https://www.duelout.com/competition/checkin/{}/{}'.format(competition_name, uuid)
                check_in_url.replace('+','%20')

                print('--> Checking the following teams: {}'.format(team))

                if team.email_check_in_sent == False:
                    print('------> The team {} with email {} will be sent out a check-in notification'.format(team, team.team_captain_email))
                    email_sent = email_sys.send_competition_email(check_in_url, subject, competition_name, [team.team_captain_email])

                    if email_sent:
                        team.email_check_in_sent = True
                        team.save()
                else:
                    print('------> Notification was already sent for team {} with email {}'.format(team, team.team_captain_email))
                    print()
        else:
            print('----> No teams registered')
    # competition is not close to current time
    else:
        print('--> Current delta {} is not <= 1 hour'.format(delta))
        print('--> Emails will not be sent out!')

