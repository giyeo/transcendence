from django.db import models

# Create your models here.
class UserModel(models.Model):
    login = models.CharField(max_length=20)
    nickname = models.CharField(max_length=20)
    auth_secret = models.CharField(max_length=32)
    wins = models.PositiveIntegerField()
    loses = models.PositiveIntegerField()

