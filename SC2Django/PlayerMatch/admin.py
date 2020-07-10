from django.contrib import admin

# Register your models here.
from .models import PlayerMatchSingular, OverallSentiment

admin.site.register(PlayerMatchSingular)
admin.site.register(OverallSentiment)
