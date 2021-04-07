from core.models import Analytics
import requests, datetime

'''
https://rapidapi.com/elreco/api/call-of-duty-modern-warfare?endpoint=apiendpoint_c8a294f3-e186-4365-a85c-5ef29d0fe735
'''

class WarzoneApi:
    def __init__(self, tag, platform, cod_x_rapidapi_key, cod_x_rapidapi_host):
        self.tag = tag.replace('#', '%23')
        self.platform = platform
        self.headers = {
            'x-rapidapi-key': cod_x_rapidapi_key,
            'x-rapidapi-host': cod_x_rapidapi_host,
        }
    
    def get_warzone_matches(self):
        '''
        Get warzone matches.
        '''

        error = False
        error_message = ''

        url = 'https://call-of-duty-modern-warfare.p.rapidapi.com/warzone-matches/{}/{}'.format(self.tag, self.platform)

        response = requests.request("GET", url, headers = self.headers)

        battle_royale_data = response.json()

        # Lets measure how many calls are we doing per day
        todays_date = datetime.datetime.now().date()

        try:
            todays_analytic = Analytics.objects.get(date = todays_date)
            todays_analytic.amount_of_warzone_api_requests_calls += 1
            todays_analytic.save()
            print('Analytics already exists so updating')
        except Exception as e:
            Analytics.objects.create(date = todays_date, amount_of_warzone_api_requests_calls = 1)
            print('Analytics does not exist so creating new!')
        
        try:
            if battle_royale_data['error'] == True and battle_royale_data['message'] == '404 - Not found. Incorrect username or platform? Misconfigured privacy settings?':
                error = True
                error_message = 'User account not found'
            elif battle_royale_data['error'] == True and battle_royale_data['message'] == 'Not permitted: not allowed':
                error = True
                error_message = 'Account is private'
        except Exception:
            pass

        return battle_royale_data, error, error_message


    def get_warzone_general_stats(self):
        '''
        Get warzone matches
        '''

        error = False
        error_message = ''

        url = 'https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/{}/{}'.format(self.tag, self.platform)

        response = requests.request("GET", url, headers = self.headers)

        battle_royale_data = response.json()

        # Lets measure how many calls are we doing per day
        todays_date = datetime.datetime.now().date()

        try:
            todays_analytic = Analytics.objects.get(date = todays_date)
            todays_analytic.amount_of_warzone_api_requests_calls += 1
            todays_analytic.save()
            print('Analytics already exists so updating')
        except Exception as e:
            Analytics.objects.create(date = todays_date, amount_of_warzone_api_requests_calls = 1)
            print('Analytics does not exist so creating new!')
        
        try:
            if battle_royale_data['error'] == True and battle_royale_data['message'] == '404 - Not found. Incorrect username or platform? Misconfigured privacy settings?':
                error = True
                error_message = 'User account not found'
            elif battle_royale_data['error'] == True and battle_royale_data['message'] == 'Not permitted: not allowed':
                error = True
                error_message = 'Account is private'
        except Exception:
            pass

        return battle_royale_data, error, error_message


    def get_warzone_weekly_stats(self):
        '''
        Get the warzone weekly stats
        '''

        url = 'https://call-of-duty-modern-warfare.p.rapidapi.com/weekly-stats/{}/{}'.format(self.tag, self.platform)

        response = requests.request("GET", url, headers = self.headers)

        battle_royale_data = response.json()

        return battle_royale_data