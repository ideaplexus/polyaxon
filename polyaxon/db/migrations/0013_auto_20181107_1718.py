# Generated by Django 2.1.2 on 2018-11-07 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0012_auto_20181029_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experimentgroup',
            name='group_type',
            field=models.CharField(choices=[('study', 'study'), ('selection', 'selection')], default='study', max_length=10),
        ),
    ]
