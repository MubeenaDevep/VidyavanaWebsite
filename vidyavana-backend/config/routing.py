from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from apps.notifications import consumers

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    re_path(r"^ws/notifications/$", consumers.NotificationConsumer.as_asgi()),
                ]
            )
        ),
    }
)
