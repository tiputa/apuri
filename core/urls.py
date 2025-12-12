from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("home/", views.home, name="home"),
    # 投稿
    path("post/new/", views.create_post, name="create_post"),
    # ルーム
    path("create-room/", views.create_room, name="create_room"),
    path("rooms/", views.room_list, name="room_list"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("rooms/request/<int:room_id>/", views.send_request, name="send_request"),
    path("requests/", views.request_list, name="request_list"),
    path(
        "requests/approve/<int:request_id>/",
        views.approve_request,
        name="approve_request",
    ),
    # DM
    path("dm/", views.dm_list, name="dm_list"),
    path("dm/<int:user_id>/", views.dm_chat, name="dm_chat"),
    # ユーザー一覧
    path("users/", views.user_list, name="user_list"),
    # プロフィール
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("profile/<int:user_id>/edit/", views.edit_profile, name="edit_profile"),
    # 認証
    path("signup/", views.signup, name="signup"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)