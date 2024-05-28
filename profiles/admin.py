from django.contrib import admin
from .models import Profile
import cv2


class ProfileAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # id obj.photo:
        #     image = cv2.imread(obj.photo.path)
        #     id image is not None:
        #         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #         clarity = cv2.Laplacian(gray, cv2.CV_64F).var()
        #         id clarity < 100:
        #             raise ValueError("The photo is not clear enough.")
        super().save_model(request, obj, form, change)


admin.site.register(Profile, ProfileAdmin)
