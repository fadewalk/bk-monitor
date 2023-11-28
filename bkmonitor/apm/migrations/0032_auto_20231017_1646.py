# Generated by Django 3.2.15 on 2023-10-17 08:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('apm', '0031_auto_20230829_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileDataSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bk_biz_id', models.IntegerField(verbose_name='业务id')),
                ('app_name', models.CharField(max_length=255, verbose_name='所属应用')),
                ('bk_data_id', models.IntegerField(default=-1, verbose_name='数据id')),
                ('result_table_id', models.CharField(default='', max_length=128, verbose_name='结果表id')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'abstract': False,
            },
        )
    ]
