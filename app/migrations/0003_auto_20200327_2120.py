# Generated by Django 2.2 on 2020-03-27 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_user_password'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Token',
            new_name='UserToken',
        ),
    ]