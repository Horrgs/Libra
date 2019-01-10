from django.urls import path

from . import views

app_name = 'welcome'
urlpatterns = [
    path('', views.index, name='index'),
    path('present', views.start_slide_show, name='present')
]