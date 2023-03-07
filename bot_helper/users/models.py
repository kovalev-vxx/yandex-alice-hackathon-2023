from django.db import models


class User(models.Model):
    alice_user_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
