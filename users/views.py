from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from djoser.views import UserViewSet

@api_view(['POST'])
@permission_classes([AllowAny])  # Разрешить доступ неаутентифицированным пользователям
def user_registration(request):
    serializer = UserViewSet.serializer_class(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)