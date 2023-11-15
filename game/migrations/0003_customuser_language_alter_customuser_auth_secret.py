# Generated by Django 4.2.6 on 2023-11-15 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_customuser_delete_yourmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='language',
            field=models.CharField(default='en', max_length=2),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='auth_secret',
            field=models.CharField(default='UX7WOEPMTZ7JJHWKNF4PMUQ5LXBHQO5K', max_length=32),
        ),
    ]
