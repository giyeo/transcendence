from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models

import pyotp

class CustomUser(models.Model):
    login = models.CharField(max_length=42, unique=True)
    auth_secret = models.CharField(max_length=32, default=pyotp.random_base32())
    twofa_enabled = models.BooleanField(default=False)
    language = models.CharField(max_length=2, default="en")
    
class Queue(models.Model):
    user_id = models.IntegerField()
    login = models.CharField(max_length=42)
    gamemode = models.CharField(max_length=32, default="default")
    match_type = models.CharField(max_length=32, default="default")
    match_suggested_name = models.CharField(max_length=32, default="")
