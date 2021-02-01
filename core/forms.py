from django import forms

from .models import Profile, Teams, StaffCustomTeams

from django.core.exceptions import ValidationError

class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('activision_tag',)


class TeamsForm(forms.ModelForm):
    
    class Meta:
        model = Teams
        fields = ('profiles','team_name','team_type',)
    
    def clean(self):
        '''
        Make sure the user does 
        not make a squad greater
        than 4 people
        '''

        profiles = self.cleaned_data.get('profiles')

        if profiles.count() > 4:
            raise ValidationError("Max squad is 4 people!")
        return self.cleaned_data


class JoinCompetitionRequestForm(forms.ModelForm):

    class Meta:
        model = StaffCustomTeams
        fields = ('team_name', 
                'team_banner',
                'team_captain_email',
                'team_twitch_stream_user',

                'player_1', 'player_1_id_type', 
                'player_2', 'player_2_id_type', 
                'player_3', 'player_3_id_type', 
                'player_4', 'player_4_id_type',)

        labels = {
            'team_banner': 'Team logo (URL only - Do not change if you do not have logo)',
            'team_captain_email': 'Team Captain Email (Contact Information - Any updates will be via email)',
            'team_twitch_stream_user': 'Team Twitch User (User only - Not URL)',

            'player_1': 'Player 1 Id - (Battlenet, Psnet or Xbox)',
            'player_2': 'Player 2 Id - (Battlenet, Psnet or Xbox)',
            'player_3': 'Player 3 Id - (Battlenet, Psnet or Xbox)',
            'player_4': 'Player 4 Id - (Battlenet, Psnet or Xbox)',

            'player_1_id_type': 'Player 1 - Id type',
            'player_2_id_type': 'Player 2 - Id type',
            'player_3_id_type': 'Player 3 - Id type',
            'player_4_id_type': 'Player 4 - Id type',
        }

            