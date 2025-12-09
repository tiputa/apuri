from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Room, RoomRequest, Post, Message, DirectMessage
from .forms import RoomForm, MessageForm, DirectMessageForm
from .forms import JapaneseUserCreationForm


def home(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "core/home.html", {"posts": posts})


@login_required
def create_post(request):
    if request.method == "POST":
        text = request.POST.get("text")
        Post.objects.create(user=request.user, text=text)
        return redirect("home")
    return render(request, "core/create_post.html")


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


def room_list(request):
    rooms = Room.objects.all().order_by("-created_at")
    return render(request, "core/rooms.html", {"rooms": rooms})


@login_required
def send_request(request, room_id):
    room = Room.objects.get(id=room_id)

    # 既に送っていたら作らない
    already = RoomRequest.objects.filter(user=request.user, room=room).exists()
    if not already:
        RoomRequest.objects.create(user=request.user, room=room)

    return redirect("room_list")


@login_required
def request_list(request):
    # 自分が作ったルームへのリクエストだけ表示
    my_rooms = Room.objects.filter(host=request.user)
    requests = RoomRequest.objects.filter(room__in=my_rooms, approved=False)

    return render(request, "core/request_list.html", {"requests": requests})


@login_required
def approve_request(request, request_id):
    req = RoomRequest.objects.get(id=request_id)

    # 承認フラグを ON
    req.approved = True
    req.save()

    return redirect("request_list")


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # 承認されていないユーザーは入れない
    allowed = (
        RoomRequest.objects.filter(
            user=request.user,
            room=room,
            approved=True,
        ).exists()
        or room.host == request.user
    )

    if not allowed:
        return redirect("room_list")

    messages = Message.objects.filter(room=room).order_by("created_at")

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
        },
    )


@login_required
def dm_list(request):
    # 自分が送った or 受け取った相手を一覧にする
    sent = DirectMessage.objects.filter(sender=request.user).values_list(
        "receiver", flat=True
    )
    received = DirectMessage.objects.filter(receiver=request.user).values_list(
        "sender", flat=True
    )

    user_ids = set(list(sent) + list(received))
    users = User.objects.filter(id__in=user_ids)

    return render(request, "core/dm_list.html", {"users": users})


@login_required
def dm_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # メッセージ取得（自分↔相手）
    messages = DirectMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user],
    ).order_by("created_at")

    # 送信処理
    if request.method == "POST":
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect("dm_chat", user_id=other_user.id)
    else:
        form = DirectMessageForm()

    return render(
        request,
        "core/dm_chat.html",
        {"other_user": other_user, "messages": messages, "form": form},
    )


def signup(request):
    if request.method == "POST":
        form = JapaneseUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
    else:
        form = JapaneseUserCreationForm()

    return render(request, "registration/signup.html", {"form": form})
