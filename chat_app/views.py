from datetime import timedelta
from time import timezone

from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import MessageForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os
from django.contrib.auth import logout
from django.shortcuts import redirect

from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from .models import Message
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Message  # 你的消息模型
from django.core.files import File
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import GlobalBackground
from .forms import BackgroundImageForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Message
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserForm, ProfileForm

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Message
from django.contrib.auth.decorators import login_required


# message.timestamp 是带时区的 datetime 对象
from django.utils import timezone
from datetime import timedelta
@login_required
@require_POST
def recall_message(request, msg_id):
    try:
        msg = Message.objects.get(id=msg_id)
    except Message.DoesNotExist:
        return HttpResponseNotFound('消息不存在')

    if (msg.user != request.user )  and  (request.user == "超级管理" ):
        return HttpResponseForbidden('不能撤回他人消息')

    if (timezone.now() - msg.timestamp > timedelta(seconds=30)) and  (request.user == "超级管理") :
        return HttpResponseForbidden('撤回时间超过30秒')

    # 标记为撤回或者删除消息
    msg.text = '[消息已撤回]'
    msg.is_recalled = True
    msg.save()


    # 撤回成功后，通过 channel layer 广播撤回事件
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_room',  # 假设所有用户都在这个群组
        {
            'type': 'chat.recall',  # 事件类型
            'id': msg_id,
            'user': request.user.username,
        }
    )

    return JsonResponse({'success': True})



async def chat_message_recall(self, event):
    message_id = event['message_id']
    await self.send(text_data=json.dumps({
        'action': 'recall',
        'message_id': message_id,
    }))


# //后端删除接口
@require_POST
@login_required
def delete_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id, user=request.user)
        message.delete()
        return JsonResponse({"status": "ok"})
    except Message.DoesNotExist:
        return JsonResponse({"status": "not found"}, status=404)

# //注册视图
from django.shortcuts import render, redirect
from .forms import UserForm, ProfileForm

def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])  # 密码加密
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'avatar' in request.FILES:
                filename = f"avatars/{user.username}.jpg"
                profile.avatar.name = filename

            profile.save()
            return redirect('login')  # 你也可以跳转到首页：redirect('index')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()

        return render(request, 'chat_app/register.html', {
            'user_form': user_form,
            'profile_form': profile_form
    })


def broadcast_message(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat_room",
        {
            "type": "chat.message",
            "message": message.text,
            "user": message.user.username,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "image": message.image.url if message.image else "",
            "id": message.id,  # 加上 ID
        }
    )

@csrf_exempt
@login_required
def send_preset(request):
    if request.method == "POST":
        data = json.loads(request.body)
        command = data.get("command")

        channel_layer = get_channel_layer()

        if command == "倒计时图":

            msg=Message.objects.create(user=request.user, text="倒计时100")
            broadcast_message(msg)
            return JsonResponse({"status": "ok"})


        elif command == "开始下单":
            msg = Message.objects.create(user=request.user, text="开始下单")
            broadcast_message(msg)
            return JsonResponse({"status": "ok"})

        elif command == "停止下单":
            msg = Message.objects.create(user=request.user, text="停止下单")
            broadcast_message(msg)
            return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "error"}, status=400)


@login_required
def upload_global_background(request):
    if request.user.username != '超级管理':
        raise PermissionDenied("只有 超级管理 用户能修改全局背景")

    bg, created = GlobalBackground.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = BackgroundImageForm(request.POST, request.FILES, instance=bg)
        if form.is_valid():
            form.save()
            return redirect('chatroom')
    else:
        form = BackgroundImageForm(instance=bg)

    return render(request, 'chat_app/upload_global_background.html', {'form': form})

@login_required
def send_preset_image(request):
    if request.method == 'POST' and request.user.username == '超级管理':
        preset_path = os.path.join('media', 'preset', 'example.jpg')  # 你的预设图片路径
        with open(preset_path, 'rb') as f:
            message = Message(user=request.user)
            message.image.save('example.jpg', File(f))
            message.save()
    return redirect('chatroom')  # 重定向到聊天室页面

def custom_logout(request):
    logout(request)
    # return redirect('login')
    return redirect('/')

def recent_messages_apiint(request, count):
    messages = Message.objects.order_by('-timestamp')[:count]  # 倒序取 count 条
    data = []
    for msg in reversed(messages):  # 再反转成正序（时间从早到晚）
        data.append({
            'user': msg.user.username if msg.user else '游客',
            'text': msg.text,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'image': msg.image.url if msg.image else ''
        })
    return JsonResponse({'messages': data})
def recent_messages_api(request):
    messages = Message.objects.order_by('-timestamp')[:50]   # 倒序取100条，再反转成正序
    data = []
    for msg in messages:
        data.append({
            'user': msg.user.username if msg.user else '游客',
            'text': msg.text,
            # 'timestamp': localtime(msg.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            # 'image': msg.image.url if msg.image else ''
        })
    return JsonResponse({'messages': data})


# ✅ 允许所有人访问聊天室
def chatroom(request):
    messages = Message.recent_messages().order_by('timestamp')
    form = MessageForm()

    bg_url = GlobalBackground.get_background()
    return render(request, 'chat_app/chatroom.html', {
        'form': form,
        'messages': messages,
        'global_background_url': bg_url,
    })

# @login_required(login_url='/login/')
def post_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()

            # ✅ 发送 WebSocket 广播消息
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "chat_room",  # group name，和 consumer 一致
                {
                    "type": "chat.message",
                    "message": message.text,
                    "user": message.user.username,
                    # "timestamp": localtime(message.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),

                    # 如果有图片，发送图片路径（可选）
                    "image": message.image.url if message.image else "",
                    "id": message.id,  # 加上 ID
                }
            )
    return redirect('chatroom')
