from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from user.models import UserConfirm
from user.serializers import CodeSerializer


class VerifyCodeAPIView(APIView):
    def post(self, request):
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            try:
                user_confirm = UserConfirm.objects.get(code=code)

                if timezone.now() > user_confirm.expiration_time:
                    return Response({'error': 'Kode vaqti tugagan'}, status=status.HTTP_400_BAD_REQUEST)

                user = user_confirm.user
                token, created = Token.objects.get_or_create(user=user)
                data = {
                    'token': token.key,
                    'phone': user.phone,
                    'username': user.username,
                    'telegram_id': user.telegram_id
                }
                return Response(data, status=status.HTTP_200_OK)

            except UserConfirm.DoesNotExist:
                return Response({'error': 'Notogri kod'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

