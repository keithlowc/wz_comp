from .warzone_api import WarzoneApi

import datetime, time

from itertools import groupby

def covert_epoch_time_utc(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%c')


def calculate_time_delta(start_1, start_2):
    a = datetime.datetime.fromtimestamp(start_1)
    b = datetime.datetime.fromtimestamp(start_2)

    total_delta = a - b

    return total_delta


def calculate_average(matches, element):
    ratios = []
    for match in matches:
        kd = match['playerStats'][element]
        ratios.append(kd)
    
    avg = sum(ratios) / len(ratios)

    return '{:.3f}'.format(avg)


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

# Matches related

def get_values_from_matches(matches_list, user_tag = None):
    
    all_matches = []

    for index, matches in enumerate(matches_list):
        data = {}
        data['kd'] = matches['playerStats']['kdRatio']
        data['kills'] = matches['playerStats']['kills']
        try:
            data['teamPlacement'] = matches['playerStats']['teamPlacement']
        except Exception as e:
            print('Error teamplacement not found!')
            data['teamPlacement'] = 100

        data['damageDone'] = matches['playerStats']['damageDone']
        data['matchID'] = matches['matchID']

        all_matches.append(data)
    
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


def filter_for_time(config, matches_list, competition_start_time, competition_end_time, threshold_time_seconds = 7200):
    '''
    Filters matches for 2 hours by default

    threshold = value from end_time - start_time. ie = 2 hours range
    start_time = 1 pm  - match_time = 1:30 pm = delta = 0:30
    if delta 0:30 < 2 and 1:30 pm <= end_time
    add to lists values
    '''

    config = config

    if config.competitions_dummy_data:
        start_time = matches_list[0]['utcStartSeconds']

        print()
        print('** Using Dummy data **')
        print('The start_time: ', start_time)

        threshold_time = datetime.timedelta(seconds = threshold_time_seconds)

        end_time = time.time()
    else:
        # Should slice the matches based on the 
        # time range give.
        start_time = competition_start_time.timestamp()
        end_time = competition_end_time.timestamp()
        threshold_time = calculate_time_delta(end_time, start_time)
    
        print()
        print('** Using Real Sliced data **')
        print('The start_time: ', start_time)

    top_matches = []

    for match in matches_list:
        delta = calculate_time_delta(start_time, match['utcStartSeconds'])
        print('Start Time: {} - Match time {} = delta {} - {}'.format(datetime.datetime.fromtimestamp(start_time),
                                                               datetime.datetime.fromtimestamp(match['utcStartSeconds']), 
                                                               delta, 
                                                               match['matchID']))

        if delta <= threshold_time and match['utcStartSeconds'] <= end_time:
            top_matches.append(match)
            print('--------------> {} - Selected Match: The delta: {} < {} threshold and match time {} <= {} end'.format(len(top_matches), 
                                                                                                                delta, threshold_time, 
                                                                                                                datetime.datetime.fromtimestamp(match['utcStartSeconds']), 
                                                                                                                datetime.datetime.fromtimestamp(end_time)))
        
    return top_matches


def get_custom_data(user_tag, user_id_type, competition_start_time, competition_end_time, competition_type, config):
    '''
    Gets the matches for user_tag
    '''

    warzone_api = WarzoneApi(tag = user_tag.replace('#', '%23'),
                             platform = user_id_type, 
                             cod_x_rapidapi_key = config.cod_x_rapidapi_key, 
                             cod_x_rapidapi_host = config.cod_x_rapidapi_host)
    
    matches = warzone_api.get_warzone_matches()

    total_matches_len = len(matches['matches'])

    filtered_matches = filter_matches(matches['matches'][0:total_matches_len - 1],
                                     competition_type)

    matches_without_time_filter = matches['matches'][0:total_matches_len - 1] # All matches

    data = filter_for_time(config,
                          filtered_matches, 
                          competition_start_time, 
                          competition_end_time)

    clean_data = get_values_from_matches(data, user_tag)

    matches_without_time_filter = get_values_from_matches(matches_without_time_filter,
                                                         user_tag)

    return clean_data, matches_without_time_filter


