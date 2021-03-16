from django.core.exceptions import ValidationError


def validate_competition_name(value):
    '''
    Validation on validators inside the
    model - The competition name should
    not contain forward slashes at all.
    '''

    if value.find('/') != -1:
        raise ValidationError('Your name should not contain forward slashes ("/")!')
    return value