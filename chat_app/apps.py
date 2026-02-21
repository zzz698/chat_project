from django.apps import AppConfig

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'chat_app'

    def ready(self):
        import chat_app.signals  # 导入信号模块

class ChatAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_app'
