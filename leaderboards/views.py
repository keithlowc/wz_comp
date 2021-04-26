from django.shortcuts import render

from .models import Teams

# Create your views here.

def home(request):
    return render(request, 'home.html')

def show_records(request):
    solos = Teams.objects.filter(record_mode = 'Solos').order_by('-kills')
    duos = Teams.objects.filter(record_mode = 'Duos').order_by('-kills')
    trios = Teams.objects.filter(record_mode = 'Trios').order_by('-kills')
    squads = Teams.objects.filter(record_mode = 'Squads').order_by('-kills')

    context = {
        'solos': solos,
        'duos': duos,
        'trios': trios,
        'squads': squads,
    }

    return render(request, 'records/all_records.html', context = context)