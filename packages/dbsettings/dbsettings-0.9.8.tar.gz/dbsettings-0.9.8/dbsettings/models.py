from django.db import models

# Create your models here.

class Setting(models.Model):
    key = models.CharField(primary_key=True, max_length=255)
    description = models.TextField(null=True, blank=True)
    value = models.TextField()

    def __str__(self):
        return self.key
