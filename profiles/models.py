from django.db import models
from django.contrib.auth.models import User
import cv2

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(blank=True, upload_to='photos')
    bio = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"profile of {self.user.username}"

    def save(self, *args, **kwargs):
        # Check if the photo is provided
        if self.photo:
            # Load image
            image = cv2.imread(self.photo.path)
            if image is not None:
                # Convert image to grayscale
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Calculate Laplacian variance as a measure of clarity
                clarity = cv2.Laplacian(gray, cv2.CV_64F).var()
                # Check if the clarity meets your criteria, for example, clarity > 100
                if clarity < 100:
                    raise ValueError("The photo is not clear enough.")
            return("Edil chort")
        # Call the parent class's save method to save the object
        super().save(*args, **kwargs)
