from django.contrib import admin
from django.urls import path

from PlayerMatch.views import FileFieldView

app_name = 'PlayerMatch'

urlpatterns = [
    path('upload/', FileFieldView.as_view(), name='replay-upload')
]