from django.db import models

# Create your models here.
class PlayerMatchSingular(models.Model):
    username = models.CharField()
    compoundSentiment = models.FloatField()
    messages = models