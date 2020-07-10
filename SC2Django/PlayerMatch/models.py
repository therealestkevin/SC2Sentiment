from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class PlayerMatchSingular(models.Model):
    username = models.CharField(max_length=100, blank=True)
    compoundSentiment = models.FloatField()
    messages = ArrayField(
        models.TextField(), blank=True
    )
    messageSentiments = ArrayField(
        models.FloatField(), blank=True
    )


class OverallSentiment(models.Model):
    terranSentiment = models.FloatField()
    zergSentiment = models.FloatField()
    protossSentiment = models.FloatField()
