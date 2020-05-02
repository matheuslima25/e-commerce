from django.urls import include, path

from core import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
]
