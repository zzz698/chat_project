# chat_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatroom, name='chatroom'),
    path('post/', views.post_message, name='post_message'),
    path('send-preset-image/', views.send_preset_image, name='send_preset_image'),
    path('upload_global_background', views.upload_global_background, name='upload_global_background'),

    path('api/recent_messages/', views.recent_messages_api, name='recent_messages_api'),
    path('api/recent_messages_apiint/<int:count>', views.recent_messages_apiint, name='recent_messages_apiint'),
    path('send_preset/', views.send_preset, name='send_preset'),
    path('register/', views.register, name='register'),

    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('recall_message/<int:msg_id>/', views.recall_message, name='recall_message'),

]
