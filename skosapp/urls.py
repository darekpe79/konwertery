from django.urls import path
from . import views

app_name = 'skosapp'  # Ustaw nazwę aplikacji jako przestrzeń nazw

urlpatterns = [
    path('upload/', views.upload_excel, name='upload_excel'),
]
