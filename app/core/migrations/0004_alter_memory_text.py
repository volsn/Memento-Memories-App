# Generated by Django 3.2.6 on 2021-10-08 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_memory_expiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memory',
            name='text',
            field=models.TextField(blank=True),
        ),
    ]
