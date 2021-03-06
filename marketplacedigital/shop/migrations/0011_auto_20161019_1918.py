# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-19 21:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import shop.models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_purchase_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productfile',
            name='uploaded_file',
            field=models.FileField(upload_to=shop.models.user_directory_path),
        ),
    ]
