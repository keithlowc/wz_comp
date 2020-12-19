from django import forms

from .models import Profile, Teams

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
            