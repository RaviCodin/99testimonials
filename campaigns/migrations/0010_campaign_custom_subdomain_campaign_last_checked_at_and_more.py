# Generated by Django 5.1.7 on 2025-03-25 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0009_alter_campaign_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='custom_subdomain',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='campaign',
            name='last_checked_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='verification_status',
            field=models.BooleanField(default=False),
        ),
    ]
