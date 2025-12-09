from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('home/', views.home, name='home'),
    path("post/new/", views.create_post, name="create_post"),
    path("create-room/", views.create_room, name="create_room"),
    path("rooms/", views.room_list, name="room_list"),
    path(
        "rooms/request/<int:room_id>/",
        views.send_request,
        name="send_request",
    ),
    path("requests/", views.request_list, name="request_list"),
    path(
        "requests/approve/<int:request_id>/",
        views.approve_request,
        name="approve_request",
    ),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("dm/", views.dm_list, name="dm_list"),
    path("dm/<int:user_id>/", views.dm_chat, name="dm_chat"),
    path("signup/", views.signup, name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
