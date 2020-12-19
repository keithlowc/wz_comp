from .warzone_api import WarzoneApi
from warzone_general.settings import headers

import datetime

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

# Matches related

def get_values_from_matches(matches_list, user_tag = None):
    
    all_matches = []

    for index, matches in enumerate(matches_list):
        data = {}
        data['kd'] = matches['playerStats']['kdRatio']
        data['kills'] = matches['playerStats']['kills']

        # TeamPlacement sometimes is not in the request
        try:
            data['teamPlacement'] = matches['playerStats']['teamPlacement']
        except Exception as e:
            data['teamPlacement'] = 0

        data['damageDone'] = matches['playerStats']['damageDone']

        all_matches.append(data)
    
    if user_tag is not None:

        final_data = {}
        final_data[str(user_tag)] = all_matches
        return final_data

    else:
        return all_matches


def filter_for_time(matches_list, threshold_time_seconds = 7200):
    '''
    Filters matches for 2 hours by default
    Need to add first_match_time as utc.now()
    '''
    
    first_match_time = matches_list[0]['utcStartSeconds']

    top_matches = []

    threshold_time = datetime.timedelta(seconds = threshold_time_seconds)

    for match in matches_list:
        delta = calculate_time_delta(first_match_time, match['utcStartSeconds'])

        if delta < threshold_time:
            top_matches.append(match)
        
    return top_matches


def get_custom_data(user_tag):
    '''
    Gets the matches for user_tag
    '''

    warzone_api = WarzoneApi(tag = user_tag.replace('#', '%23'),platform = 'acti')
    matches = warzone_api.get_warzone_matches()

    total_matches_len = len(matches['matches'])

    data = filter_for_time(matches['matches'][0:total_matches_len - 1])

    clean_data = get_values_from_matches(data, user_tag)

    print(clean_data)
    print()

    return clean_data


def warzone_competition_rules(data, kills = False, placement = False):
    if kills:
        total_kills = sum(data)
        total_kills = total_kills * 2

        return total_kills
    
    elif placement:
        
        return 1



