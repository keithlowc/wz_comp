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
                'team_twitch_stream_user',
                'player_1', 'player_1_id_type', 
                'player_2', 'player_2_id_type', 
                'player_3', 'player_3_id_type', 
                'player_4', 'player_4_id_type',)

        labels = {
            'team_banner': 'Team logo (URL only)',
            'team_twitch_stream_user': 'Team Twitch User (User only - Not URL)',
        }

            