from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
import uuid


# Create your models here.
class CustomUser(AbstractUser):
    plan = models.ForeignKey('Plan', on_delete=models.DO_NOTHING, null=True)


class ImageSize(models.Model):
    size = models.CharField(max_length=64)

    def __str__(self):
        return str(self.size)


class Plan(models.Model):
    name = models.CharField(max_length=64)
    height = models.ManyToManyField(ImageSize)
    link = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class Image(models.Model):
    name = models.CharField()
    file = models.ImageField(upload_to='images/')
    uploaded_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):

        if self.file:
            from PIL import Image as PILImage
            image = PILImage.open(self.file)
            self.width, self.height = image.size

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class ExpiringLink(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.DO_NOTHING)
    image = models.ForeignKey('Image', on_delete=models.DO_NOTHING)
    expiration_date = models.DateField(default=date.today)
    expiration_time = models.IntegerField(default=300)
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)

    @classmethod
    def generate_unique_key(cls):
        return uuid.uuid4()