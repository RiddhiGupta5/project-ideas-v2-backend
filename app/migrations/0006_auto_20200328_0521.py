# Generated by Django 2.2 on 2020-03-27 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20200328_0342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default=' ', max_length=500, null=True),
        ),
    ]