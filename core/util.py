from .warzone_api import WarzoneApi
from .email import EmailNotificationSystem

from core.models import StaffCustomTeams, Player, Match
from core.anomaly_detection import AnomalyDetection

import datetime, time

from itertools import groupby


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


def get_values_from_matches(matches_list, message, competition_model_rank, user_tag = None):
    
    all_matches = []

    print('Player name: {} for {}'.format(matches_list[0]['player']['username'], message))

    for index, matches in enumerate(matches_list):

        data = {}

        # Data that may not show up
        try:
            data['teamWipes'] = matches['playerStats']['objectiveTeamWiped']
        except Exception as e:
            data['teamWipes'] = 0

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
            data['longestStreak'] = matches['playerStats']['longestStreak']
            data['gulag'] = matches['playerStats']['gulagKills']
            data['loadouts'] = matches['player']['loadout']
            data['percentTimeMoving'] = matches['playerStats']['percentTimeMoving']
            data['utcStartSeconds'] = matches['utcStartSeconds']
            data['timePlayed'] = matches['playerStats']['timePlayed']

            # Anomaly detection
            anomaly_detector = AnomalyDetection(competition_rank = competition_model_rank)
            data['anomalousMatch'] = anomaly_detector.detect_anomalous_match(data['kills'])

            # Gulag
            if data['gulag'] > 1:
                data['gulag'] == True
            
            # Exploit/Bug detection
            data['stimGlitch'] = stimulant_glitch_detection(data['loadouts'], data['damageTaken'])

            all_matches.append(data)

        except Exception as e:
            print('SKIPPING this match since there was an error with: {} - Match type {}'.format(e, matches['mode']))
    
    if user_tag is not None:

        final_data = {}
        final_data[str(user_tag)] = all_matches
        return final_data

    else:
        return all_matches


def stimulant_glitch_detection(loadouts_in_match, damage_taken):
    '''
    Returns true if stimulant glitch detection
    is found.
    '''

    for loadout in loadouts_in_match:
        if loadout['tactical']['name'] == 'equip_adrenaline':
            if damage_taken > 3500:
                return True

    return False
            

from collections import OrderedDict

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

    dics = OrderedDict()
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
        start_time = competition_start_time
        end_time = competition_end_time
    
        print()
        print('** Using Real Sliced data **')
        print('The competition start_time: ', start_time)

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


def get_custom_data(user_tag, user_id_type, competition_start_time, competition_end_time, competition_type, competition_model_rank, custom_config):
    '''
    Gets the matches for user_tag
    '''

    clean_data = []
    matches_without_time_filter = []

    warzone_api = WarzoneApi(tag = user_tag.replace('#', '%23'),
                             platform = user_id_type, 
                             cod_x_rapidapi_key = custom_config["cod_x_rapidapi_key"], 
                             cod_x_rapidapi_host = custom_config["cod_x_rapidapi_host"])
    
    matches, error, error_message = warzone_api.get_warzone_matches()

    if error:
        # If there is any error while getting user
        # data then we will return empty values
        # and the error and error message
        return clean_data, matches_without_time_filter, error, error_message

    else:
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

        # If matches are found within the
        # time range if they aren't then
        # clean data is empty
        if len(data) > 0:
            clean_data = get_values_from_matches(matches_list = data, 
                                                message = 'Clean data',
                                                user_tag = user_tag,
                                                competition_model_rank = competition_model_rank)

        matches_without_time_filter = exclude_matches_of_type(matches_list = matches_without_time_filter, 
                                                            competition_type_list = ['br_dmz_plnbld',
                                                                                    'br_dmz_plndtrios',
                                                                                    'br_dmz_plndval1',
                                                                                    'brtdm_rmbl',
                                                                                    'brtdm_wzrumval2',
                                                                                    'br_rebirth_rbrthquad'])

        matches_without_time_filter = get_values_from_matches(matches_list = matches_without_time_filter,
                                                            message = 'Matches without time filter',
                                                            user_tag = user_tag,
                                                            competition_model_rank = competition_model_rank)

        return clean_data, matches_without_time_filter, error, error_message


def add_to_player_model(competition, team, user_kd, user_id, user_id_type):
    '''
    Adds to the player model
    if the player does not 
    already exist in the model
    '''

    player_found = True
    try:
        # Search for the player name and id type
        # if player exists
        # then we go ahead and make sure we add the new 
        # team to it.
        Player.objects.get(user_id = user_id, 
                            user_id_type = user_id_type)
    except Exception as e:
        player_found = False
    
    if not player_found:
        print('Saving Player {} to model'.format(user_id))
        player = Player.objects.create(user_kd = user_kd,
                                        user_id = user_id,
                                        user_id_type = user_id_type)

        player.competition.add(competition)
        player.team.add(team)
    else:
        player = Player.objects.get(user_id = user_id, 
                                    user_id_type = user_id_type)

        player.competition.add(competition)
        player.team.add(team)
        print('Not saving Player {} since it already exists in db! But adding relation ship to team and competition'.format(user_id))


def add_to_match_model(competition, team, player, match_id, kills, kd, deaths, headshots, damage_done, damage_taken, placement, team_wipes, longest_streak, percent_time_moving, utc_start_time, time_played, player_kd_at_time, index):
    '''
    Adds the match to the MATCH model
    if this match with
    '''

    found_match = True
    try:
        Match.objects.get(player = player, 
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
                                team_wipes = team_wipes,
                                longest_streak = longest_streak,
                                percent_time_moving = percent_time_moving,
                                placement = placement,
                                time_played = time_played,
                                utc_start_time = utc_start_time,
                                player_kd_at_time = player_kd_at_time)

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

                team_emails = []
                team_emails.append(team.team_captain_email)
                team_emails.append(team.player_2_email)
                team_emails.append(team.player_3_email)
                team_emails.append(team.player_4_email)

                team_emails = [i for i in team_emails if i] # Clearn empty values

                if team.email_check_in_sent == False:
                    print('------> The team {} with email {} will be sent out a check-in notification'.format(team, team_emails))

                    for email in team_emails:
                        email_sent = email_sys.send_competition_email(check_in_url, subject, competition_name, [email])

                    if email_sent:
                        team.email_check_in_sent = True
                        team.save()
                else:
                    print('------> Notification was already sent for team {} with email {}'.format(team, team_emails))
                    print()
        else:
            print('----> No teams registered')
    # competition is not close to current time
    else:
        print('--> Current delta {} is not <= 1 hour'.format(delta))
        print('--> Emails will not be sent out!')

