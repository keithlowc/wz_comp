from django.core.management.base import BaseCommand, CommandError
from core.models import ConfigController, Analytics

class Command(BaseCommand):
    help = 'Loads any config file needed from db'

    def handle(self, *args, **options):
        # Creates the configcontroller object needed for
        # main configuration

        print('----------- PRE-RELEASE TASKS -----------')

        config = ConfigController.objects.all().count()
        analytics = Analytics.objects.all().count()
        
        if config < 1:
            ConfigController.objects.create()
        else:
            print('-------> Did not create config controller since it already exists!')
        
