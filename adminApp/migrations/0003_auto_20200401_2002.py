# Generated by Django 2.2 on 2020-04-01 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminApp', '0002_answer_evaluated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer_body',
            field=models.TextField(),
        ),
    ]
