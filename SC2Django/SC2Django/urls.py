"""SC2Django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from PlayerMatch.views import FileFieldView, sentiment_data, TerranTableView, ZergTableView, ProtossTableView
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', TemplateView.as_view(template_name="about.html")),
    path('', FileFieldView.as_view(), name='replay-upload'),
    path('sentiment/', sentiment_data, name='sentiment-data'),
    path('thanks/', TemplateView.as_view(template_name="PlayerMatch/thanks.html"), name='thanks-page'),
    path('about/', TemplateView.as_view(template_name="about.html"), name='about-page'),
    path('terran/', TerranTableView.as_view(), name='terran-table'),
    path('zerg/', ZergTableView.as_view(), name='zerg-table'),
    path('protoss/', ProtossTableView.as_view(), name='protoss-table'),
]


