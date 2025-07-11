from django.db import models

class CoverImage(models.Model):
    final_image = models.ImageField(upload_to='covers/')