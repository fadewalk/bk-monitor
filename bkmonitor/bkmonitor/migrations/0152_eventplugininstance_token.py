# Generated by Django 3.2.15 on 2023-12-26 11:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bkmonitor', '0151_merge_20231226_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventplugininstance',
            name='token',
            field=models.CharField(default='', max_length=64, verbose_name='关联信息token'),
        ),
    ]
