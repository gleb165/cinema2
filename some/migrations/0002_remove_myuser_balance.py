# Generated by Django 3.1.5 on 2021-03-11 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('some', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='balance',
        ),
    ]
