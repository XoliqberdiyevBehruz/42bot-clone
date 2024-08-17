import random
from datetime import timedelta
from django.core.cache import cache

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import json


class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True)
    username = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=50, unique=True, null=True)

    class Meta:
        db_table = 'user_users'

    def generate_code(self):
        code = ''.join([str(random.randint(0, 100) % 10) for _ in range(6)])
        expiration_time = timezone.now() + timedelta(minutes=5)
        cache_key = f'user_confirm_{code}'
        cache_data = {
            'user_id': self.id,
            'code': code,
            'expiration_time': expiration_time.isoformat()
        }
        cache.set(cache_key, json.dumps(cache_data), timeout=300)
        return code

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        self.generate_code()


class UserConfirm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.BigIntegerField()
    expiration_time = models.DateTimeField()

    class Meta:
        db_table = 'user_confirm'

    def __str__(self):
        return f'{self.code}'