"""
URL configuration for fplmate_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from django.urls import path, re_path
from django.shortcuts import redirect
from .hello import hello
from models.views import predict_rating
from .scraper import scrape
from models.recomender import RecommendTeamView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('landing',hello,name='hello'),
    # path('scrape', scrape),  # Endpoint to scrape a page
    path('predict-rating', predict_rating),  # Endpoint to predict player rating
    path('recommend-team', RecommendTeamView.as_view(), name='recommend_team'),
    re_path(r'^.*$', lambda request: redirect('/landing'))  # Catch-all redirect
]
