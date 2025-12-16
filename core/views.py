from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Room, RoomRequest, Post, Message, DirectMessage, Profile
from .forms import (
    RoomForm,
    MessageForm,
    DirectMessageForm,
    JapaneseUserCreationForm,
    ProfileForm,
)
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Max, Q, DateTimeField, Value
from django.db.models.functions import Greatest, Coalesce


# =====================
# ホーム画面
# =====================
def home(request):
    limit = timezone.now() - timedelta(hours=24)

    # 24時間以内の投稿だけ表示
    posts = Post.objects.filter(
        created_at__gte=limit
    ).select_related("user").order_by("-created_at")

    return render(
        request,
        "core/home.html",
        {
            "posts": posts,
        }
    )


# =====================
# 新規投稿
# =====================
@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        image = request.FILES.get("image")

        if text == "":
            return render(
                request,
                "core/create_post.html",
                {"error": "投稿内容を入力してください"},
            )

        Post.objects.create(user=request.user, text=text, image=image)
        return redirect("home")

    return render(request, "core/create_post.html")


# =====================
# ルーム作成
# =====================
@login_required
def create_room(request):
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect("home")
    else:
        form = RoomForm()

    return render(request, "core/create_room.html", {"form": form})


# =====================
# ルーム一覧
# =====================
@login_required
def room_list(request):
    rooms = Room.objects.all().order_by("-created_at")

    # 自分が申請したルームID一覧
    requested_room_ids = RoomRequest.objects.filter(user=request.user).values_list(
        "room_id",
        flat=True,
    )

    # 自分が承認済みのルームID一覧
    approved_room_ids = RoomRequest.objects.filter(
        user=request.user, approved=True
    ).values_list("room_id", flat=True)

    # 自分が作成者のルーム
    my_rooms = Room.objects.filter(host=request.user)

    # 未承認リクエスト数（作成者用）
    request_count = RoomRequest.objects.filter(
        room__in=my_rooms, approved=False
    ).count()

    return render(
        request,
        "core/rooms.html",
        {
            "rooms": rooms,
            "requested_room_ids": requested_room_ids,
            "approved_room_ids": approved_room_ids,
            "request_count": request_count,
            "has_requests": request_count > 0,
        },
    )


# =====================
# ルーム参加リクエスト
# =====================
@login_required
def send_request(request, room_id):
    room = Room.objects.get(id=room_id)

    already = RoomRequest.objects.filter(user=request.user, room=room).exists()
    if not already:
        RoomRequest.objects.create(user=request.user, room=room)

    return redirect("room_list")


@login_required
def request_list(request):
    my_rooms = Room.objects.filter(host=request.user)
    requests = RoomRequest.objects.filter(room__in=my_rooms, approved=False)

    return render(request, "core/request_list.html", {"requests": requests})


@login_required
def approve_request(request, request_id):
    req = get_object_or_404(RoomRequest, id=request_id)

    # ルーム作成者以外は承認できない
    if req.room.host != request.user:
        return redirect("room_list")

    req.approved = True
    req.save()

    return redirect("request_list")


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # ======================
    # 入室許可チェック
    # ======================
    is_host = room.host == request.user
    is_approved = RoomRequest.objects.filter(
        user=request.user, room=room, approved=True
    ).exists()

    if not (is_host or is_approved):
        return redirect("room_list")

    # ======================
    # ★ 24時間超えメッセージ削除 ★
    # ======================
    limit = timezone.now() - timedelta(hours=24)
    Message.objects.filter(room=room, created_at__lt=limit).delete()

    # ======================
    # メッセージ取得
    # ======================
    messages = Message.objects.filter(room=room).order_by("created_at")

    # ======================
    # メッセージ送信
    # ======================
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.room = room
            msg.user = request.user
            msg.save()
            return redirect("room_detail", room_id=room.id)
    else:
        form = MessageForm()

    return render(
        request,
        "core/room_detail.html",
        {
            "room": room,
            "messages": messages,
            "form": form,
            "is_host": is_host,
        },
    )


# ==============================
# DM 一覧（会話相手一覧）
# ==============================
@login_required
def dm_list(request):
    me = request.user

    users = (
        User.objects.filter(Q(dm_sender__receiver=me) | Q(dm_receiver__sender=me))
        .exclude(id=me.id)
        .annotate(
            last_sent_at=Max("dm_sender__created_at", filter=Q(dm_sender__receiver=me)),
            last_received_at=Max(
                "dm_receiver__created_at", filter=Q(dm_receiver__sender=me)
            ),
        )
        .annotate(last_dm_at=Greatest("last_sent_at", "last_received_at"))
        .order_by("-last_dm_at")
        .distinct()
    )

    return render(
        request,
        "core/dm_list.html",
        {"users": users},
    )


# ==============================
# DM チャット画面
# ==============================
@login_required
def dm_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = DirectMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
    ).order_by("created_at")

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            DirectMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                text=text,
            )
        return redirect("dm_chat", user_id=other_user.id)

    return render(
        request,
        "core/dm_chat.html",
        {
            "other_user": other_user,
            "messages": messages,
        },
    )


# ==============================
# ユーザー一覧（DM送信用）
# ==============================
@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "core/user_list.html", {"users": users})


# ==============================
# 新規登録
# ==============================
def signup(request):
    if request.method == "POST":
        form = JapaneseUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = JapaneseUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


# ==============================
# プロフィール詳細表示
# ==============================
@login_required
def profile(request, user_id):
    user_profile = get_object_or_404(Profile, user__id=user_id)
    return render(request, "core/profile.html", {"profile": user_profile})


# ==============================
# プロフィール編集（ログインユーザーのみ）
# ==============================
@login_required
def edit_profile(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)

    # 他人のプロフィール編集は禁止
    if profile.user != request.user:
        return redirect("profile", user_id=user_id)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile", user_id=user_id)

    else:
        form = ProfileForm(instance=profile)

    return render(request, "core/edit_profile.html", {"form": form})
