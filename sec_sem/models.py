from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image


def validate_image(image):
    if image.file.content_type not in ['image/jpeg', 'image/png']:
        raise ValidationError("Only JPEG and PNG images are allowed.")

    # Опциональная проверка размера изображения
    max_size = (4086, 4086)  # Максимальные допустимые размеры (ширина, высота)
    image = Image.open(image)
    if image.width > max_size[0] or image.height > max_size[1]:
        raise ValidationError(f"Image dimensions should not exceed {max_size[0]}x{max_size[1]} pixels.")


class Photo(models.Model):
    image = models.ImageField()

    class Meta:
        app_label = 'sec_sem'


class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='logs/')  # Поле для хранения изображения
    timestamp = models.DateTimeField(auto_now_add=True)  # Дата и время создания записи

    def __str__(self):
        return f'Log for {self.user.username} at {self.timestamp}'

    class Meta:
        app_label = 'sec_sem'
