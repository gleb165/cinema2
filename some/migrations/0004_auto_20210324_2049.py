# Generated by Django 3.1.7 on 2021-03-24 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('some', '0003_auto_20210316_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='busy',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='show',
            name='film',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shows', related_query_name='shows', to='some.film'),
        ),
        migrations.AlterField(
            model_name='show',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shows', related_query_name='shows', to='some.place'),
        ),
    ]
