from rest_framework import serializers

from user import models


class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserConfirm
        fields = ['code']

