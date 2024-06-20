from django.urls import path
from .views import get_books, get_image,play_video,hello_world,webcam,capture_image,register,registerAPI


urlpatterns = [
    path('', get_books, name='get_books'),
    path('image/', get_image, name='get_image'),
    path('video/', play_video, name='play_video'),
    path('hello/', hello_world, name='hello_world'),
    path('webcam/', webcam, name='webcam'),
    path('capture/', capture_image, name='capture_image'),
    path('register_form/', register, name='register'),
    path('register/', registerAPI, name='registerAPI'),



]