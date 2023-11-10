from django.db import models

import pyotp

# Create your models here.
class UserModel(models.Model):
    name = models.CharField(max_length=42)
    login = models.CharField(max_length=42)
    auth_secret = models.CharField(max_length=32, default=pyotp.random_base32())
    twofa_enabled = models.BooleanField(default=False)
    wins = models.PositiveIntegerField(default=0)
    loses = models.PositiveIntegerField(default=0)