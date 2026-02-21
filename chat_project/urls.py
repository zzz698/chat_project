from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from chat_app.views import custom_logout  # 导入自定义视图
urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('chat_app.urls')),  # 默认首页指向 chat_app
    path('login/', auth_views.LoginView.as_view(template_name='chat_app/login.html'), name='login'),

    path('logout/', custom_logout, name='logout'),  # 替换 LogoutView
]

# 媒体文件支持（图片上传）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
