from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def show_records(request):
    return render(request, 'records/all_records.html')