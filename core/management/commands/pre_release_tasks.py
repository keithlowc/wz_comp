from django.core.management.base import BaseCommand, CommandError
from core.models import ConfigController

class Command(BaseCommand):
    help = 'Loads any config file needed from db'

    def handle(self, *args, **options):
        # Creates the configcontroller object needed for
        # main configuration
        
        if len(ConfigController.objects.all()) < 1:
            ConfigController.objects.create()