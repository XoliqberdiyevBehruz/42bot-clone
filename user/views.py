from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from user.models import UserConfirm, User
from user.serializers import CodeSerializer
from django.core.cache import cache
import json


class VerifyCodeAPIView(APIView):
    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            user_confirm = cache.get(f'user_confirm_{code}')
            if user_confirm:
                user_confirm = json.loads(user_confirm)
                user = User.objects.get(id=user_confirm['user_id'])
                cache_code = user_confirm['code']
                expiration_time = user_confirm['expiration_time']
                if cache_code:
                    token, created = Token.objects.get_or_create()
                    data = {
                        'token': token.key,
                        'phone': user.phone,
                        'username': user.username,
                        'telegram_id': user.telegram_id
                    }
                    return Response(data, status=status.HTTP_200_OK)

                else:
                    return Response({'error': 'Notogri kod'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success': False})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

