from django import forms
from .models import Profile
import cv2


class UserCreationFormWithProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio']  # Include fields you want to include in the profile

    def save(self, commit=True):
        profile = super().save(commit=False)
        if profile.photo:
            image = cv2.imread(profile.photo.path)
            if image is not None:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                clarity = cv2.Laplacian(gray, cv2.CV_64F).var()
                if clarity < 100:
                    raise ValueError("The photo is not clear enough.")
        if commit:
            profile.save()
        return profile