# Generated by Django 3.2.6 on 2021-10-08 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_memory_expiration'),
    ]

    operations = [
        migrations.AddField(
            model_name='memory',
            name='expiration',
            field=models.DateTimeField(default=None, editable=False),
            preserve_default=False,
        ),
    ]
