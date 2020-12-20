from .warzone_api import WarzoneApi
from .models import ConfigController
from warzone_general.settings import headers

import datetime, time

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
        data['matchID'] = matches['matchID']

        all_matches.append(data)
    
    if user_tag is not None:

        final_data = {}
        final_data[str(user_tag)] = all_matches
        return final_data

    else:
        return all_matches


def filter_for_time(matches_list, competition_start_time, competition_end_time, threshold_time_seconds = 7200):
    '''
    Filters matches for 2 hours by default
    '''

    # threshold = value from end_time - start_time. ie = 2 hours range
    # start_time = 1 pm  - match_time = 1:30 pm = delta = 0:30
    # if delta 0:30 < 2 and 1:30 pm <= end_time
    # add to lists values

    config = ConfigController.objects.get(name = 'main_config_controller')

    if config.competitions_dummy_data:
        # Dummy data = False by default
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
        print('This time: {} - {} = {}'.format(start_time, match['utcStartSeconds'], delta))

        if delta <= threshold_time and match['utcStartSeconds'] <= end_time:
            top_matches.append(match)
            print('--------------> {} Selected Match: The delta: {} < {} threshold and match time {} <= {} end'.format(len(top_matches), 
                                                                                                                delta, threshold_time, 
                                                                                                                datetime.datetime.fromtimestamp(match['utcStartSeconds']), 
                                                                                                                datetime.datetime.fromtimestamp(end_time)))
        
    return top_matches


def get_custom_data(user_tag, competition_start_time, competition_end_time):
    '''
    Gets the matches for user_tag
    '''

    warzone_api = WarzoneApi(tag = user_tag.replace('#', '%23'), platform = 'acti')

    matches = warzone_api.get_warzone_matches()

    total_matches_len = len(matches['matches'])

    data = filter_for_time(matches['matches'][0:total_matches_len - 1], competition_start_time, competition_end_time)

    clean_data = get_values_from_matches(data, user_tag)

    return clean_data





