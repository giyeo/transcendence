# Generated by Django 4.2.6 on 2023-11-13 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=42, unique=True)),
                ('auth_secret', models.CharField(default='AF6RUTV4EDDERJABWP7HT7Z3P2JYUZII', max_length=32)),
                ('twofa_enabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name='YourModel',
        ),
    ]
