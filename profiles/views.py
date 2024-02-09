from django.shortcuts import render
from .models import Profile

def sorted_profiles(request):
    # Get all profiles
    profiles = Profile.objects.all()
    # Sort profiles based on photo clarity
    sorted_profiles = sorted(profiles, key=lambda profile: profile.calculate_clarity(), reverse=True)
    return render(request, 'sorted_profiles.html', {'profiles': sorted_profiles})
