# Generated by Django 5.1 on 2024-08-17 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_user_telegram_id'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='user',
            table='user_users',
        ),
    ]
