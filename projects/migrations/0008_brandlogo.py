# Generated by Django 5.1.4 on 2025-03-16 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrandLogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='project_%(project_id)s/brand_logos/')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brand_logos', to='projects.project')),
            ],
        ),
    ]
