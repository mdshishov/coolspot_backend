from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["GET"])
def home_page(request):
    return Response(
        {
            "type": "home",
            "blocks": [
                {
                    "type": "text",
                    "content": "Привет! Добро пожаловать на главную страницу 🚀",
                }
            ],
        }
    )
