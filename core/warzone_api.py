import requests

from warzone_general.settings import headers

headers = headers

'''
https://rapidapi.com/elreco/api/call-of-duty-modern-warfare?endpoint=apiendpoint_c8a294f3-e186-4365-a85c-5ef29d0fe735
'''

class WarzoneApi:
    def __init__(self, tag, platform, headers = headers):
        self.tag = tag.replace('#', '%23')
        self.platform = platform
        self.headers = headers
    
    def get_warzone_matches(self):
        '''
        Get warzone matches
        '''

        url = 'https://call-of-duty-modern-warfare.p.rapidapi.com/warzone-matches/{}/{}'.format(self.tag, self.platform)

        response = requests.request("GET", url, headers = self.headers)

        battle_royale_data = response.json()

        return battle_royale_data


    def get_warzone_general_stats(self):
        '''
        Get warzone matches
        '''

        url = 'https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/{}/{}'.format(self.tag, self.platform)

        response = requests.request("GET", url, headers = self.headers)

        battle_royale_data = response.json()

        return battle_royale_data


    def get_warzone_weekly_stats(self):
        '''
        Get the warzone weekly stats
        '''

        url = 'https://call-of-duty-modern-warfare.p.rapidapi.com/weekly-stats/{}/{}'.format(self.tag, self.platform)

        response = requests.request("GET", url, headers = self.headers)

        battle_royale_data = response.json()

        return battle_royale_data