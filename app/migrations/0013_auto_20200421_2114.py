# Generated by Django 2.2 on 2020-04-21 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20200421_2107'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='idea',
            options={'ordering': ['-votes', '-date_time']},
        ),
    ]
