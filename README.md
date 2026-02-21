# 实时聊天室项目

基于 Django + Django Channels 构建的实时 WebSocket 聊天室，支持图片发送、消息撤回、用户头像等功能，提供桌面端与移动端双界面。

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Django 5.0 |
| 实时通信 | Django Channels 4.2 + WebSocket |
| ASGI 服务器 | Daphne |
| 图片处理 | Pillow |
| 静态文件 | WhiteNoise |
| 部署 | Docker + Nginx |
| 数据库 | SQLite（开发）|

## 功能特性

- **实时消息**：基于 WebSocket 的双向实时通信，消息即时广播
- **图片发送**：支持上传图片，自动压缩至 200KB 以内
- **消息撤回**：30 秒内可撤回已发送消息，实时同步给所有在线用户
- **消息删除**：消息发送者可删除自己的消息
- **用户系统**：注册、登录、自定义头像
- **消息历史**：保留最近 24 小时内最多 100 条消息
- **发送限速**：客户端限制 2 秒发送间隔，防止刷屏
- **管理员功能**：发送预设消息（开始下单/停止下单/倒计时图）、上传全局公告背景图
- **双端界面**：桌面端（chatroom）+ 移动端（chatroom2）独立模板
- **粘贴图片**：支持从剪贴板粘贴图片并预览后发送

## 项目结构

```
chat_project/
├── chat_app/                  # 主应用
│   ├── migrations/            # 数据库迁移文件
│   ├── admin.py               # Django 后台配置
│   ├── apps.py                # 应用配置（含信号注册）
│   ├── consumers.py           # WebSocket 消费者
│   ├── forms.py               # 表单定义
│   ├── models.py              # 数据模型
│   ├── routing.py             # WebSocket 路由
│   ├── signals.py             # 信号：自动创建用户 Profile
│   ├── urls.py                # URL 路由
│   └── views.py               # 视图函数
├── chat_project/              # 项目配置
│   ├── asgi.py                # ASGI 配置（HTTP + WebSocket）
│   ├── settings.py            # Django 配置
│   ├── urls.py                # 主路由
│   └── wsgi.py
├── templates/
│   └── chat_app/
│       ├── base.html                      # 基础模板（背景样式）
│       ├── chatroom.html                  # 桌面端聊天界面
│       ├── chatroom2.html                 # 移动端聊天界面
│       ├── login.html                     # 登录页
│       ├── register.html                  # 注册页
│       └── upload_global_background.html  # 管理员公告上传
├── media/                     # 用户上传文件
│   ├── avatars/               # 用户头像
│   ├── backgrounds/           # 公告背景图
│   └── chat_images/           # 聊天图片
├── docker-compose.yml         # Docker 编排
├── requirements.txt           # Python 依赖
└── manage.py
```

## 数据模型

### Profile
用户扩展信息，与 `User` 一对一关联，存储用户头像。新用户注册时通过信号自动创建。

### Message
聊天消息，关联发送者（User），包含文本内容、可选图片附件、发送时间。图片上传时自动压缩。

### GlobalBackground
全局公告图片（单条记录），管理员可上传，展示给所有用户查看规则/公告。

## API 接口

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 聊天室主页（桌面端） |
| `/post/` | POST | 发送消息（文本/图片） |
| `/register/` | GET/POST | 用户注册 |
| `/login/` | GET/POST | 用户登录 |
| `/logout/` | GET | 用户登出 |
| `/api/recent_messages/` | GET | 获取最近 50 条消息（JSON） |
| `/api/recent_messages_apiint/<count>` | GET | 获取指定数量消息（JSON） |
| `/send_preset/` | POST | 发送预设消息（管理员） |
| `/send_preset_image/` | POST | 发送预设图片（管理员） |
| `/upload_global_background` | GET/POST | 上传公告背景图（管理员） |
| `/delete_message/<id>/` | POST | 删除消息 |
| `/recall_message/<id>/` | POST | 撤回消息（30 秒内有效） |

### WebSocket

- **端点**：`ws://<host>/ws/chat/`
- 连接后加入 `chat_room` 频道组，消息实时广播给所有成员

## 快速开始

### 方式一：本地开发

**环境要求**：Python 3.10+

```bash
# 1. 克隆项目
git clone https://github.com/zzz698/chat_project.git
cd chat_project

# 2. 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 数据库迁移
python manage.py migrate

# 4. 创建超级管理员（可选）
python manage.py createsuperuser

# 5. 启动开发服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000 打开聊天室。

### 方式二：Docker 部署

```bash
# 构建并启动所有服务（web + nginx + redis）
docker-compose up -d --build

# 执行数据库迁移
docker-compose exec web python manage.py migrate

# 收集静态文件
docker-compose exec web python manage.py collectstatic --noinput
```

访问 http://localhost 打开聊天室。

## 生产环境注意事项

部署前务必处理以下安全问题：

1. **Secret Key**：将 `settings.py` 中的 `SECRET_KEY` 替换为随机密钥，并通过环境变量注入，不要硬编码在代码中
2. **关闭 Debug 模式**：设置 `DEBUG = False`
3. **限制 ALLOWED_HOSTS**：填写实际域名或 IP，不要使用 `['*']`
4. **使用 Redis Channel Layer**：`InMemoryChannelLayer` 不支持多进程/多 worker，生产环境替换为：
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {'hosts': [('redis', 6379)]},
       },
   }
   ```
5. **数据库**：替换 SQLite 为 PostgreSQL 或 MySQL
6. **HTTPS**：配置 SSL 证书，WebSocket 使用 `wss://`

## 依赖说明

```
django==5.0.3          # Web 框架
channels==4.2.2        # WebSocket 支持
daphne                 # ASGI 服务器
pillow==10.4.0         # 图片处理
whitenoise             # 静态文件服务
asgiref==3.8.1         # ASGI 工具库
```

安装依赖：

```bash
pip install -r requirements.txt
```
