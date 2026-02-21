from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.db import models
from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class GlobalBackground(models.Model):
    image = models.ImageField(upload_to='backgrounds/')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "全局背景"

    @classmethod
    def get_background(cls):
        bg = cls.objects.first()
        return bg.image.url if bg and bg.image else None



class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.timestamp}'

    @staticmethod
    def recent_messages():
        # 先取倒序的最新200条主键id
        ids = (
            Message.objects
            .filter(timestamp__gte=timezone.now() - timedelta(days=1))
            .order_by('-timestamp')
            .values_list('id', flat=True)[:100]
        )
        # 再按正序取这200条消息
        return Message.objects.filter(id__in=ids).order_by('timestamp')

    def save(self, *args, **kwargs):
        # 如果有上传图片且超过200KB，进行压缩
        if self.image and self.image.size > 100 * 1024:
            img = Image.open(self.image)
            output = BytesIO()

            # 压缩 JPEG/PNG（默认压成JPEG）
            format = 'JPEG'
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            quality = 85  # 初始压缩质量
            while True:
                output.seek(0)
                img.save(output, format=format, quality=quality)
                if output.tell() <= 200 * 1024 or quality < 30:
                    break
                quality -= 5

            # 替换原图
            output.seek(0)
            self.image = InMemoryUploadedFile(
                output, 'ImageField', self.image.name, 'image/jpeg',
                output.tell(), None
            )

        super().save(*args, **kwargs)
