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
    terranSentimentCount = models.IntegerField(null=True)
    terranSentimentOverall = models.FloatField(null=True)
    zergSentimentCount = models.IntegerField(null=True)
    zergSentimentOverall = models.FloatField(null=True)
    protossSentimentCount = models.IntegerField(null=True)
    protossSentimentOverall = models.FloatField(null=True)
